"""Unit tests for the decision-time forecast resolver."""

from backend.app.config import LONDON_TZ
from backend.app.services.resolver import (
    compute_cutoff_datetime_utc,
    generate_day_settlement_periods,
    parse_cutoff_time,
    parse_delivery_date,
    resolve_day_forecast,
)


def test_settlement_periods_count():
    """Verify that exactly 48 half-hour settlement periods are generated for a day."""
    deliv_d = parse_delivery_date("2026-01-15")
    periods = generate_day_settlement_periods(deliv_d)
    assert len(periods) == 48
    assert periods[0][0] == 1
    assert periods[-1][0] == 48

    # First period starts at 00:00 Europe/London
    assert periods[0][1].astimezone(LONDON_TZ).strftime("%H:%M") == "00:00"
    # 48th period starts at 23:30 Europe/London
    assert periods[-1][1].astimezone(LONDON_TZ).strftime("%H:%M") == "23:30"


def test_cutoff_computation():
    """Verify decision cut-off is on D-1 at configured time."""
    deliv_d = parse_delivery_date("2026-01-15")
    cutoff_t = parse_cutoff_time("09:00")
    cutoff_utc = compute_cutoff_datetime_utc(deliv_d, cutoff_t)

    # D-1 is 2026-01-14
    assert cutoff_utc.year == 2026
    assert cutoff_utc.month == 1
    assert cutoff_utc.day == 14
    assert cutoff_utc.hour == 9
    assert cutoff_utc.minute == 0


def test_resolver_with_mock_fixtures(sample_delivery_day, mock_hand_crafted_records):
    """Test core domain rules using hand-crafted edge-case records."""
    forecasts_df, actuals_df = mock_hand_crafted_records

    summary = resolve_day_forecast(
        delivery_date_str=sample_delivery_day,
        cutoff_time_str="09:00",
        forecasts_df=forecasts_df,
        actuals_df=actuals_df,
    )

    assert summary.delivery_date == sample_delivery_day
    assert len(summary.periods) == 48

    p1 = summary.periods[0]  # Period 1 (00:00)
    # Scenario: publish at 06:00 (11000), 08:00 (12000), 09:00 (12500 - exact cutoff), 10:00 (14000 - after cutoff)
    # Expected: The one published exactly at 09:00 (12500 MW)
    assert p1.forecast_mw == 12500.0
    assert p1.actual_mw == 13000.0
    # error = forecast - actual = 12500 - 13000 = -500 (under-forecast)
    assert p1.error_mw == -500.0
    # horizon: 2026-01-15 00:00 minus 2026-01-14 09:00 = 15 hours
    assert p1.horizon_hours == 15.0

    p2 = summary.periods[1]  # Period 2 (00:30)
    # Scenario: stream duplicate at 08:30 (13000 MW)
    assert p2.forecast_mw == 13000.0
    assert p2.actual_mw == 12000.0
    # error = 13000 - 12000 = +1000 (over-forecast)
    assert p2.error_mw == 1000.0

    p3 = summary.periods[2]  # Period 3 (01:00)
    # Scenario: only published at 10:00 (after cutoff).
    # Expected: None (must preserve gap, never fill silently!)
    assert p3.forecast_mw is None
    assert p3.actual_mw == 14500.0
    assert p3.error_mw is None

    p4 = summary.periods[3]  # Period 4 (01:30)
    # Scenario: forecast published at D-2 18:00 (11000 MW), actual is missing
    assert p4.forecast_mw == 11000.0
    assert p4.actual_mw is None
    assert p4.error_mw is None
    # horizon: 2026-01-15 01:30 minus 2026-01-13 18:00 = 31.5 hours
    assert p4.horizon_hours == 31.5


def test_cutoff_sensitivity(sample_delivery_day, mock_hand_crafted_records):
    """Test that shifting cut-off time alters forecast selection dynamically."""
    forecasts_df, actuals_df = mock_hand_crafted_records

    # If cutoff is 07:00 instead of 09:00 on D-1
    # For Period 1, 08:00 and 09:00 are now after cut-off!
    # Expected: The 06:00 forecast (11000 MW)
    summary_early = resolve_day_forecast(
        delivery_date_str=sample_delivery_day,
        cutoff_time_str="07:00",
        forecasts_df=forecasts_df,
        actuals_df=actuals_df,
    )
    p1_early = summary_early.periods[0]
    assert p1_early.forecast_mw == 11000.0

    # If cutoff is 11:00 instead of 09:00 on D-1
    # For Period 1, 10:00 forecast (14000 MW) is now eligible and latest
    summary_late = resolve_day_forecast(
        delivery_date_str=sample_delivery_day,
        cutoff_time_str="11:00",
        forecasts_df=forecasts_df,
        actuals_df=actuals_df,
    )
    p1_late = summary_late.periods[0]
    assert p1_late.forecast_mw == 14000.0
