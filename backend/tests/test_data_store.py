"""Unit tests for the DataStore layer."""

from backend.app.services.data_store import data_store


def test_data_store_has_snapshot():
    """Verify that parquet/sqlite snapshot files exist and are readable."""
    assert data_store.has_snapshot() is True

    actuals = data_store.get_actuals()
    forecasts = data_store.get_forecasts()

    assert len(actuals) > 0
    assert len(forecasts) > 0
    assert "start_time_utc" in actuals.columns
    assert "generation_mw" in actuals.columns
    assert "publish_time_utc" in forecasts.columns


def test_available_delivery_days():
    """Verify delivery days list for January 2026 purchase window."""
    days = data_store.get_available_delivery_days()
    assert len(days) == 31  # 2026-01-02 through 2026-02-01
    assert days[0] == "2026-01-02"
    assert days[-1] == "2026-02-01"


def test_data_health():
    """Verify data health returns valid row counts and status."""
    health = data_store.get_data_health()
    assert health.actuals_count > 1000
    assert health.forecasts_count > 1000
    assert health.earliest_actual_utc is not None
    assert health.latest_actual_utc is not None
    assert health.health_ok is True


def test_evaluate_period_range():
    """Verify multi-day resolution and error computation across live snapshot."""
    # Test a 3-day sample range
    df = data_store.evaluate_period_range(
        from_date_str="2026-01-05", to_date_str="2026-01-07", cutoff_time_str="09:00"
    )
    # 3 days * 48 periods = 144 periods
    assert len(df) == 144
    assert "forecast_mw" in df.columns
    assert "actual_mw" in df.columns
    assert "error_mw" in df.columns
    assert "horizon_hours" in df.columns

    # Check that error is populated where both forecast and actual exist
    valid = df.dropna(subset=["forecast_mw", "actual_mw"])
    assert len(valid) > 0
    for _, row in valid.iterrows():
        expected_err = round(row["forecast_mw"] - row["actual_mw"], 2)
        assert abs(row["error_mw"] - expected_err) < 1e-4
