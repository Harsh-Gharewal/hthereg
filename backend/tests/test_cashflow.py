"""Unit tests for balancing mechanism cashflow and imbalance risk calculations."""

from datetime import datetime, timezone

from backend.app.schemas.data_models import (
    DayResolutionSummary,
    HalfHourPeriod,
)
from backend.app.services.cashflow import (
    DEFAULT_IMBALANCE_PRICE_GBP_PER_MWH,
    DEFAULT_PEAK_SURCHARGE_GBP_PER_MWH,
    compute_day_cashflow,
)


def test_cashflow_single_period():
    """Verify single period MWh calculation and cashflow impact."""
    period = HalfHourPeriod(
        period_index=1,
        start_time_utc=datetime(2026, 1, 15, 0, 0, tzinfo=timezone.utc),
        start_time_local="00:00",
        end_time_utc=datetime(2026, 1, 15, 0, 30, tzinfo=timezone.utc),
        forecast_mw=1000.0,
        actual_mw=800.0,
        error_mw=200.0,  # Short 200 MW => 100 MWh shortfall
        publish_time_utc=datetime(2026, 1, 14, 8, 0, tzinfo=timezone.utc),
        horizon_hours=16.0,
    )

    day_summary = DayResolutionSummary(
        delivery_date="2026-01-15",
        cutoff_time="09:00",
        cutoff_datetime_utc=datetime(2026, 1, 14, 9, 0, tzinfo=timezone.utc),
        periods=[period],
    )

    cashflow = compute_day_cashflow(day_summary, base_price_gbp=100.0, peak_surcharge_gbp=0.0)

    assert cashflow.evaluated_periods == 1
    assert cashflow.gross_short_mwh == 100.0
    assert cashflow.gross_long_mwh == 0.0
    assert cashflow.net_imbalance_mwh == 100.0
    # 100 MWh * £100/MWh = £10,000 penalty
    assert cashflow.total_short_penalty_gbp == 10000.0
    assert cashflow.net_cashflow_exposure_gbp == 10000.0
    assert cashflow.hedge_savings_p10_p90_gbp > 0


def test_cashflow_peak_hour_surcharge():
    """Verify peak period SP 35 applies peak surcharge."""
    period = HalfHourPeriod(
        period_index=35,
        start_time_utc=datetime(2026, 1, 15, 17, 0, tzinfo=timezone.utc),
        start_time_local="17:00",
        end_time_utc=datetime(2026, 1, 15, 17, 30, tzinfo=timezone.utc),
        forecast_mw=1000.0,
        actual_mw=1200.0,
        error_mw=-200.0,  # Long 200 MW => 100 MWh surplus
        publish_time_utc=datetime(2026, 1, 14, 8, 0, tzinfo=timezone.utc),
        horizon_hours=33.0,
    )

    day_summary = DayResolutionSummary(
        delivery_date="2026-01-15",
        cutoff_time="09:00",
        cutoff_datetime_utc=datetime(2026, 1, 14, 9, 0, tzinfo=timezone.utc),
        periods=[period],
    )

    base = DEFAULT_IMBALANCE_PRICE_GBP_PER_MWH
    peak = DEFAULT_PEAK_SURCHARGE_GBP_PER_MWH
    cashflow = compute_day_cashflow(day_summary)

    p = cashflow.periods[0]
    assert p.system_imbalance_price_gbp == base + peak
    assert p.is_short is False
    assert cashflow.gross_long_mwh == 100.0
    assert cashflow.total_long_settlement_gbp == 100.0 * (base + peak)
