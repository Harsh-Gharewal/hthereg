"""Pytest configuration and shared fixtures for unit and integration tests."""

from datetime import UTC, datetime, timedelta

import pandas as pd
import pytest


@pytest.fixture
def sample_delivery_day() -> str:
    """Standard delivery day for testing."""
    return "2026-01-15"


@pytest.fixture
def mock_hand_crafted_records() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create small, hand-crafted fixtures with known expected outputs for resolver and metrics testing.

    Delivery Day: 2026-01-15 (Cut-off is 2026-01-14 09:00:00 UTC)
    """
    cutoff = datetime(2026, 1, 14, 9, 0, tzinfo=UTC)

    # 4 sample settlement periods on 2026-01-15
    st_period1 = datetime(2026, 1, 15, 0, 0, tzinfo=UTC)
    st_period2 = datetime(2026, 1, 15, 0, 30, tzinfo=UTC)
    st_period3 = datetime(2026, 1, 15, 1, 0, tzinfo=UTC)
    st_period4 = datetime(2026, 1, 15, 1, 30, tzinfo=UTC)

    # Forecast records with specific edge-case scenarios:
    # Period 1: Multiple publish times before cut-off (06:00, 08:00, 09:00 exact equality), plus one after cutoff (10:00)
    # Expected: The one published exactly at 09:00 (gen: 12500 MW)
    # Period 2: Multiple publish times with duplicate rows at same publish time (stream duplicate)
    # Expected: 13000 MW
    # Period 3: No forecast before cutoff (only published at 10:00 after cutoff)
    # Expected: None (gap preserved)
    # Period 4: Single forecast published at D-2 (horizon > 36h)
    # Expected: 11000 MW
    forecast_rows = [
        # Period 1
        {
            "start_time_utc": st_period1,
            "publish_time_utc": cutoff - timedelta(hours=3),
            "generation_mw": 11000.0,
        },
        {
            "start_time_utc": st_period1,
            "publish_time_utc": cutoff - timedelta(hours=1),
            "generation_mw": 12000.0,
        },
        {
            "start_time_utc": st_period1,
            "publish_time_utc": cutoff,
            "generation_mw": 12500.0,
        },  # Exactly at cutoff!
        {
            "start_time_utc": st_period1,
            "publish_time_utc": cutoff + timedelta(hours=1),
            "generation_mw": 14000.0,
        },  # After cutoff
        # Period 2: Duplicate at 08:30
        {
            "start_time_utc": st_period2,
            "publish_time_utc": cutoff - timedelta(minutes=30),
            "generation_mw": 13000.0,
        },
        {
            "start_time_utc": st_period2,
            "publish_time_utc": cutoff - timedelta(minutes=30),
            "generation_mw": 13000.0,
        },
        # Period 3: Only published after cut-off
        {
            "start_time_utc": st_period3,
            "publish_time_utc": cutoff + timedelta(hours=2),
            "generation_mw": 15000.0,
        },
        # Period 4: Published early at D-2 18:00
        {
            "start_time_utc": st_period4,
            "publish_time_utc": datetime(2026, 1, 13, 18, 0, tzinfo=UTC),
            "generation_mw": 11000.0,
        },
    ]
    forecasts_df = pd.DataFrame(forecast_rows)

    # Actuals for the 4 periods
    actual_rows = [
        {
            "start_time_utc": st_period1,
            "generation_mw": 13000.0,
        },  # error = 12500 - 13000 = -500 (under-forecast)
        {
            "start_time_utc": st_period2,
            "generation_mw": 12000.0,
        },  # error = 13000 - 12000 = +1000 (over-forecast)
        {
            "start_time_utc": st_period3,
            "generation_mw": 14500.0,
        },  # forecast was None -> error is None
        # Period 4 actual is missing (simulating edge case missing actuals)
    ]
    actuals_df = pd.DataFrame(actual_rows)

    return forecasts_df, actuals_df
