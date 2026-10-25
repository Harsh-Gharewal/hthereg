"""Unit tests for statistical metrics calculations."""

import numpy as np
import pandas as pd

from backend.app.services.metrics import (
    calculate_accuracy_by_horizon,
    calculate_accuracy_by_hour,
    calculate_error_distribution,
    calculate_summary_metrics,
)


def test_summary_metrics_known_values():
    """Verify metrics calculation against mathematically exact values.

    Errors: [-500, 1000, -200, 300, -600]
    Count: 5
    Sum: -500 + 1000 - 200 + 300 - 600 = 0
    Bias: 0.0
    Abs Sum: 500 + 1000 + 200 + 300 + 600 = 2600
    MAE: 2600 / 5 = 520.0
    Sq Sum: 250000 + 1000000 + 40000 + 90000 + 360000 = 1,740,000
    Mean Sq: 1740000 / 5 = 348000
    RMSE: sqrt(348000) = 589.92
    """
    errors = [-500.0, 1000.0, -200.0, 300.0, -600.0]
    actuals = [12000.0, 11000.0, 14000.0, 13000.0, 10000.0]  # mean = 12000.0

    summary = calculate_summary_metrics(errors, actuals)

    assert summary.count == 5
    assert summary.bias_mw == 0.0
    assert summary.mae_mw == 520.0
    assert summary.rmse_mw == 589.92
    # nMAE = 520.0 / 12000.0 * 100 = 4.33%
    assert summary.nmae_pct == 4.33
    assert summary.min_error_mw == -600.0
    assert summary.max_error_mw == 1000.0
    assert summary.p50_mw == -200.0


def test_summary_metrics_empty():
    """Verify empty inputs return zeroed summary gracefully."""
    summary = calculate_summary_metrics([])
    assert summary.count == 0
    assert summary.mae_mw == 0.0
    assert summary.bias_mw == 0.0
    assert summary.nmae_pct is None


def test_accuracy_by_horizon():
    """Verify horizon binning groups lead times correctly."""
    df = pd.DataFrame(
        [
            {"horizon_hours": 6.0, "error_mw": -200.0},
            {"horizon_hours": 8.0, "error_mw": -400.0},
            {"horizon_hours": 15.0, "error_mw": 500.0},
            {"horizon_hours": 20.0, "error_mw": -300.0},
            {"horizon_hours": 30.0, "error_mw": 800.0},
        ]
    )

    buckets = calculate_accuracy_by_horizon(df)
    # Bucket 0-12h has 2 items: -200 and -400 -> MAE = 300, Bias = -300
    b0_12 = next(b for b in buckets if b.bucket_label == "0 - 12h")
    assert b0_12.count == 2
    assert b0_12.mae_mw == 300.0
    assert b0_12.bias_mw == -300.0

    # Bucket 12-24h has 2 items: 500 and -300 -> MAE = 400, Bias = 100
    b12_24 = next(b for b in buckets if b.bucket_label == "12 - 24h")
    assert b12_24.count == 2
    assert b12_24.mae_mw == 400.0
    assert b12_24.bias_mw == 100.0


def test_accuracy_by_hour():
    """Verify 24 hours diurnal aggregation."""
    # Create periods for hour 10 and hour 14
    df = pd.DataFrame(
        [
            {
                "start_time_utc": "2026-01-15T10:00:00Z",
                "error_mw": -500.0,
                "actual_mw": 14000.0,
                "forecast_mw": 13500.0,
            },
            {
                "start_time_utc": "2026-01-15T10:30:00Z",
                "error_mw": -300.0,
                "actual_mw": 14200.0,
                "forecast_mw": 13900.0,
            },
            {
                "start_time_utc": "2026-01-15T14:00:00Z",
                "error_mw": 400.0,
                "actual_mw": 12000.0,
                "forecast_mw": 12400.0,
            },
        ]
    )

    hours = calculate_accuracy_by_hour(df)
    assert len(hours) == 24

    h10 = hours[10]
    assert h10.count == 2
    assert h10.mae_mw == 400.0
    assert h10.bias_mw == -400.0
    assert h10.avg_actual_mw == 14100.0

    h14 = hours[14]
    assert h14.count == 1
    assert h14.mae_mw == 400.0
    assert h14.bias_mw == 400.0


def test_error_distribution_histogram():
    """Verify histogram binning returns valid counts and quantile markers."""
    errors = np.random.normal(0, 500, 100).tolist()
    dist = calculate_error_distribution(errors, num_bins=10)
    assert dist.total_count == 100
    assert len(dist.bins) == 10
    assert sum(b.count for b in dist.bins) == 100
    assert dist.p10_mw <= dist.p50_mw <= dist.p90_mw
