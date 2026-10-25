"""Pure function statistical metrics engine for wind forecast error analysis.

All calculations here are pure functions without side-effects, making them
100% testable and shared between API endpoints and tests.
"""

import math
from collections.abc import Sequence

import numpy as np
import pandas as pd

from backend.app.config import LONDON_TZ
from backend.app.schemas.data_models import (
    AccuracySummary,
    ErrorDistribution,
    HistogramBin,
    HorizonAccuracyBucket,
    HourAccuracyBucket,
)


def calculate_summary_metrics(
    errors: Sequence[float], actuals: Sequence[float] | None = None
) -> AccuracySummary:
    """Calculate aggregate error metrics: Bias, MAE, RMSE, nMAE, P10, P50, P90.

    Formula definitions:
    - Error = Forecast - Actual (MW)
    - Bias (Mean Error) = (1/N) * sum(Error)
    - MAE = (1/N) * sum(|Error|)
    - RMSE = sqrt((1/N) * sum(Error^2))
    - nMAE = (MAE / mean(Actual)) * 100%
    - P10, P50, P90: 10th, 50th, 90th percentiles of Error
    """
    clean_errs = [e for e in errors if e is not None and not math.isnan(e)]
    if not clean_errs:
        return AccuracySummary(
            count=0,
            bias_mw=0.0,
            mae_mw=0.0,
            rmse_mw=0.0,
            nmae_pct=None,
            p10_mw=0.0,
            p50_mw=0.0,
            p90_mw=0.0,
            min_error_mw=0.0,
            max_error_mw=0.0,
        )

    arr = np.array(clean_errs, dtype=float)
    count = len(arr)
    bias = float(np.mean(arr))
    mae = float(np.mean(np.abs(arr)))
    rmse = float(np.sqrt(np.mean(arr**2)))
    p10 = float(np.percentile(arr, 10))
    p50 = float(np.percentile(arr, 50))
    p90 = float(np.percentile(arr, 90))
    min_err = float(np.min(arr))
    max_err = float(np.max(arr))

    nmae_pct = None
    if actuals is not None:
        clean_acts = [a for a in actuals if a is not None and not math.isnan(a)]
        if clean_acts:
            mean_act = float(np.mean(clean_acts))
            if mean_act > 0:
                nmae_pct = round((mae / mean_act) * 100.0, 2)

    return AccuracySummary(
        count=count,
        bias_mw=round(bias, 2),
        mae_mw=round(mae, 2),
        rmse_mw=round(rmse, 2),
        nmae_pct=nmae_pct,
        p10_mw=round(p10, 2),
        p50_mw=round(p50, 2),
        p90_mw=round(p90, 2),
        min_error_mw=round(min_err, 2),
        max_error_mw=round(max_err, 2),
    )


def calculate_accuracy_by_horizon(
    df: pd.DataFrame, buckets: list[tuple[float, float, str]] | None = None
) -> list[HorizonAccuracyBucket]:
    """Group errors into horizon lead time buckets and compute MAE & Bias for each."""
    if df.empty or "horizon_hours" not in df.columns or "error_mw" not in df.columns:
        return []

    if buckets is None:
        buckets = [
            (0.0, 12.0, "0 - 12h"),
            (12.0, 24.0, "12 - 24h"),
            (24.0, 36.0, "24 - 36h"),
            (36.0, 48.0, "36 - 48h"),
            (48.0, 120.0, "48h+"),
        ]

    valid = df.dropna(subset=["horizon_hours", "error_mw"]).copy()
    results = []

    for low, high, label in buckets:
        mask = (valid["horizon_hours"] >= low) & (valid["horizon_hours"] < high)
        subset = valid[mask]
        count = len(subset)
        if count > 0:
            errs = subset["error_mw"].values
            mae = float(np.mean(np.abs(errs)))
            bias = float(np.mean(errs))
            results.append(
                HorizonAccuracyBucket(
                    horizon_min_hours=low,
                    horizon_max_hours=high,
                    bucket_label=label,
                    count=count,
                    mae_mw=round(mae, 2),
                    bias_mw=round(bias, 2),
                )
            )
        else:
            results.append(
                HorizonAccuracyBucket(
                    horizon_min_hours=low,
                    horizon_max_hours=high,
                    bucket_label=label,
                    count=0,
                    mae_mw=0.0,
                    bias_mw=0.0,
                )
            )

    return results


def calculate_accuracy_by_hour(df: pd.DataFrame) -> list[HourAccuracyBucket]:
    """Calculate MAE, Bias, and average generation by hour of day (0 to 23 Europe/London time)."""
    if df.empty or "start_time_utc" not in df.columns or "error_mw" not in df.columns:
        return []

    valid = df.dropna(subset=["start_time_utc", "error_mw"]).copy()
    if not pd.api.types.is_datetime64_any_dtype(valid["start_time_utc"]):
        valid["start_time_utc"] = pd.to_datetime(valid["start_time_utc"], utc=True)
    elif valid["start_time_utc"].dt.tz is None:
        valid["start_time_utc"] = valid["start_time_utc"].dt.tz_localize("UTC")
    else:
        valid["start_time_utc"] = valid["start_time_utc"].dt.tz_convert("UTC")

    # Convert to Europe/London hour
    valid["hour"] = valid["start_time_utc"].dt.tz_convert(LONDON_TZ).dt.hour

    results = []
    for h in range(24):
        subset = valid[valid["hour"] == h]
        count = len(subset)
        if count > 0:
            errs = subset["error_mw"].values
            mae = float(np.mean(np.abs(errs)))
            bias = float(np.mean(errs))
            avg_act = (
                float(np.mean(subset["actual_mw"].dropna().values))
                if "actual_mw" in subset.columns and len(subset["actual_mw"].dropna()) > 0
                else 0.0
            )
            avg_fc = (
                float(np.mean(subset["forecast_mw"].dropna().values))
                if "forecast_mw" in subset.columns and len(subset["forecast_mw"].dropna()) > 0
                else 0.0
            )
            results.append(
                HourAccuracyBucket(
                    hour=h,
                    hour_label=f"{h:02d}:00",
                    count=count,
                    mae_mw=round(mae, 2),
                    bias_mw=round(bias, 2),
                    avg_actual_mw=round(avg_act, 2),
                    avg_forecast_mw=round(avg_fc, 2),
                )
            )
        else:
            results.append(
                HourAccuracyBucket(
                    hour=h,
                    hour_label=f"{h:02d}:00",
                    count=0,
                    mae_mw=0.0,
                    bias_mw=0.0,
                    avg_actual_mw=0.0,
                    avg_forecast_mw=0.0,
                )
            )

    return results


def calculate_error_distribution(errors: Sequence[float], num_bins: int = 20) -> ErrorDistribution:
    """Calculate error distribution histogram bins along with P10, P50, and P90 markers."""
    clean_errs = [e for e in errors if e is not None and not math.isnan(e)]
    if not clean_errs:
        return ErrorDistribution(bins=[], p10_mw=0.0, p50_mw=0.0, p90_mw=0.0, total_count=0)

    arr = np.array(clean_errs, dtype=float)
    p10 = float(np.percentile(arr, 10))
    p50 = float(np.percentile(arr, 50))
    p90 = float(np.percentile(arr, 90))

    counts, bin_edges = np.histogram(arr, bins=num_bins)
    bins = []
    for i in range(len(counts)):
        bins.append(
            HistogramBin(
                bin_start=round(float(bin_edges[i]), 1),
                bin_end=round(float(bin_edges[i + 1]), 1),
                count=int(counts[i]),
            )
        )

    return ErrorDistribution(
        bins=bins,
        p10_mw=round(p10, 2),
        p50_mw=round(p50, 2),
        p90_mw=round(p90, 2),
        total_count=len(arr),
    )


def compute_historical_band_map(historical_df: pd.DataFrame) -> dict[int, tuple[float, float]]:
    """Compute (P10_error, P90_error) mapped by integer horizon hours from historical data."""
    if (
        historical_df.empty
        or "horizon_hours" not in historical_df.columns
        or "error_mw" not in historical_df.columns
    ):
        return {}

    valid = historical_df.dropna(subset=["horizon_hours", "error_mw"]).copy()
    if valid.empty:
        return {}

    valid["horizon_round"] = valid["horizon_hours"].round().astype(int)
    band_map: dict[int, tuple[float, float]] = {}

    for h, group in valid.groupby("horizon_round"):
        errs = group["error_mw"].values
        if len(errs) >= 3:
            p10 = float(np.percentile(errs, 10))
            p90 = float(np.percentile(errs, 90))
            band_map[int(h)] = (p10, p90)

    # Fill default fallback if some horizons lack samples
    if band_map:
        all_errs = valid["error_mw"].values
        default_p10 = float(np.percentile(all_errs, 10))
        default_p90 = float(np.percentile(all_errs, 90))
        # ensure keys 0 to 48 exist
        for h in range(49):
            if h not in band_map:
                band_map[h] = (default_p10, default_p90)

    return band_map
