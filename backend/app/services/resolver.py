"""Decision-time forecast resolver.

Resolves the latest forecast published before or at the decision cut-off time on D-1
for each half-hour settlement period of delivery day D.
"""

from datetime import date, datetime, time, timedelta

import pandas as pd

from backend.app.config import DEFAULT_CUTOFF_TIME, LONDON_TZ, PERIODS_PER_DAY, UTC_TZ
from backend.app.schemas.data_models import DayResolutionSummary, HalfHourPeriod


def parse_delivery_date(delivery_date_str: str) -> date:
    """Parse YYYY-MM-DD delivery date."""
    return datetime.strptime(delivery_date_str, "%Y-%m-%d").date()


def parse_cutoff_time(cutoff_time_str: str) -> time:
    """Parse HH:MM cut-off time."""
    parts = cutoff_time_str.strip().split(":")
    return time(hour=int(parts[0]), minute=int(parts[1]))


def compute_cutoff_datetime_utc(delivery_d: date, cutoff_t: time) -> datetime:
    """Compute the decision cut-off datetime in UTC.

    A decision for delivery day D is made on D-1 at cutoff_t in Europe/London time.
    """
    decision_date = delivery_d - timedelta(days=1)
    local_cutoff = datetime.combine(decision_date, cutoff_t, tzinfo=LONDON_TZ)
    return local_cutoff.astimezone(UTC_TZ)


def generate_day_settlement_periods(delivery_d: date) -> list[tuple[int, datetime, datetime]]:
    """Generate all 48 half-hour settlement periods for a delivery day in Europe/London, converted to UTC.

    Returns list of tuples: (period_index 1..48, start_time_utc, end_time_utc)
    """
    periods = []
    # Base midnight in London time
    start_local = datetime.combine(delivery_d, time(0, 0), tzinfo=LONDON_TZ)
    for i in range(1, PERIODS_PER_DAY + 1):
        period_start_local = start_local + timedelta(minutes=(i - 1) * 30)
        period_end_local = period_start_local + timedelta(minutes=30)
        periods.append(
            (i, period_start_local.astimezone(UTC_TZ), period_end_local.astimezone(UTC_TZ))
        )
    return periods


def resolve_day_forecast(
    delivery_date_str: str,
    cutoff_time_str: str = DEFAULT_CUTOFF_TIME,
    forecasts_df: pd.DataFrame | None = None,
    actuals_df: pd.DataFrame | None = None,
    historical_band_map: dict[int, tuple[float, float]] | None = None,
) -> DayResolutionSummary:
    """Resolve the latest forecast published at or before the decision cut-off for each settlement period.

    Rules enforced:
    1. Decision cut-off is on D-1 at cutoff_time_str in Europe/London time.
    2. For each period start_time, take the forecast with the MAX publish_time <= cut_off_utc.
    3. Handles exact equality: publish_time == cut_off_utc is valid and eligible.
    4. Handles duplicates: if duplicate rows exist with the same publish_time, the latest is taken.
    5. Gaps are preserved: if no forecast exists at or before cut-off, forecast_mw is None.
    6. Actuals joined on start_time_utc. If missing, actual_mw is None.
    7. Error = forecast_mw - actual_mw (MW).
    8. Horizon = (start_time_utc - publish_time_utc) in hours.
    9. Error bands: P10 and P90 historical error offsets applied if historical_band_map is provided.
    """
    deliv_date = parse_delivery_date(delivery_date_str)
    cutoff_t = parse_cutoff_time(cutoff_time_str)
    cutoff_utc = compute_cutoff_datetime_utc(deliv_date, cutoff_t)

    settlement_periods = generate_day_settlement_periods(deliv_date)
    period_start_times = [p[1] for p in settlement_periods]

    # Pre-index actuals by start_time_utc
    actuals_map: dict[datetime, float] = {}
    if actuals_df is not None and not actuals_df.empty:
        # Normalize datetime to UTC
        act_df = actuals_df.copy()
        if not pd.api.types.is_datetime64_any_dtype(act_df["start_time_utc"]):
            act_df["start_time_utc"] = pd.to_datetime(act_df["start_time_utc"], utc=True)
        elif act_df["start_time_utc"].dt.tz is None:
            act_df["start_time_utc"] = act_df["start_time_utc"].dt.tz_localize("UTC")
        else:
            act_df["start_time_utc"] = act_df["start_time_utc"].dt.tz_convert("UTC")

        # Map to dict (last non-null if duplicates exist)
        for _, row in act_df.iterrows():
            st = row["start_time_utc"].to_pydatetime()
            actuals_map[st] = (
                float(row["generation_mw"]) if pd.notnull(row["generation_mw"]) else None
            )

    # Filter eligible forecasts: start_time in period_start_times AND publish_time <= cutoff_utc
    latest_forecasts_map: dict[datetime, dict] = {}
    if forecasts_df is not None and not forecasts_df.empty:
        f_df = forecasts_df.copy()
        for col in ["start_time_utc", "publish_time_utc"]:
            if not pd.api.types.is_datetime64_any_dtype(f_df[col]):
                f_df[col] = pd.to_datetime(f_df[col], utc=True)
            elif f_df[col].dt.tz is None:
                f_df[col] = f_df[col].dt.tz_localize("UTC")
            else:
                f_df[col] = f_df[col].dt.tz_convert("UTC")

        # Filter strictly <= cutoff_utc
        eligible = f_df[
            (f_df["start_time_utc"].isin(period_start_times))
            & (f_df["publish_time_utc"] <= cutoff_utc)
        ]

        if not eligible.empty:
            # Sort by start_time_utc, then publish_time_utc ascending so last() is the latest
            sorted_el = eligible.sort_values(by=["start_time_utc", "publish_time_utc"])
            latest_grouped = sorted_el.groupby("start_time_utc").last()

            for st_idx, row in latest_grouped.iterrows():
                st_dt = st_idx.to_pydatetime() if hasattr(st_idx, "to_pydatetime") else st_idx
                pub_dt = (
                    row["publish_time_utc"].to_pydatetime()
                    if hasattr(row["publish_time_utc"], "to_pydatetime")
                    else row["publish_time_utc"]
                )
                gen_mw = float(row["generation_mw"]) if pd.notnull(row["generation_mw"]) else None
                latest_forecasts_map[st_dt] = {"publish_time_utc": pub_dt, "generation_mw": gen_mw}

    # Assemble 48 periods
    period_models: list[HalfHourPeriod] = []
    forecast_values = []
    actual_values = []
    error_values = []

    for idx, start_utc, end_utc in settlement_periods:
        start_local_str = start_utc.astimezone(LONDON_TZ).strftime("%H:%M")

        fc_entry = latest_forecasts_map.get(start_utc)
        forecast_mw = None
        pub_utc = None
        pub_local_str = None
        horizon_hours = None

        if fc_entry:
            forecast_mw = fc_entry["generation_mw"]
            pub_utc = fc_entry["publish_time_utc"]
            pub_local_str = pub_utc.astimezone(LONDON_TZ).strftime("%Y-%m-%d %H:%M")
            horizon_hours = round((start_utc - pub_utc).total_seconds() / 3600.0, 2)
            if forecast_mw is not None:
                forecast_values.append(forecast_mw)

        actual_mw = actuals_map.get(start_utc)
        if actual_mw is not None:
            actual_values.append(actual_mw)

        error_mw = None
        if forecast_mw is not None and actual_mw is not None:
            error_mw = round(forecast_mw - actual_mw, 2)
            error_values.append(error_mw)

        # Historical error band (P10 and P90 bounds around forecast)
        p10_band = None
        p90_band = None
        if forecast_mw is not None and historical_band_map is not None:
            # Map horizon to closest rounded integer or bucket
            h_int = int(round(horizon_hours)) if horizon_hours is not None else 24
            if h_int in historical_band_map:
                p10_err, p90_err = historical_band_map[h_int]
                # Lower bound = forecast - p90_err (or forecast + p10_err depending on sign)
                # Since error = forecast - actual => actual = forecast - error
                # P10 error is typically negative (underforecast -> actual is higher)
                # We save the expected actual interval [forecast - p90_error, forecast - p10_error]
                p10_band = round(max(0.0, forecast_mw - p90_err), 2)
                p90_band = round(forecast_mw - p10_err, 2)

        period_models.append(
            HalfHourPeriod(
                period_index=idx,
                start_time_utc=start_utc,
                start_time_local=start_local_str,
                end_time_utc=end_utc,
                forecast_mw=forecast_mw,
                publish_time_utc=pub_utc,
                publish_time_local=pub_local_str,
                horizon_hours=horizon_hours,
                actual_mw=actual_mw,
                error_mw=error_mw,
                error_band_p10_mw=p10_band,
                error_band_p90_mw=p90_band,
            )
        )

    peak_fc = max(forecast_values) if forecast_values else None
    avg_fc = round(sum(forecast_values) / len(forecast_values), 2) if forecast_values else None
    peak_act = max(actual_values) if actual_values else None
    avg_act = round(sum(actual_values) / len(actual_values), 2) if actual_values else None
    mean_err = round(sum(error_values) / len(error_values), 2) if error_values else None
    mae = round(sum(abs(e) for e in error_values) / len(error_values), 2) if error_values else None

    return DayResolutionSummary(
        delivery_date=delivery_date_str,
        cutoff_time=cutoff_time_str,
        cutoff_datetime_utc=cutoff_utc,
        peak_forecast_mw=peak_fc,
        avg_forecast_mw=avg_fc,
        peak_actual_mw=peak_act,
        avg_actual_mw=avg_act,
        mean_error_mw=mean_err,
        mae_mw=mae,
        periods=period_models,
    )
