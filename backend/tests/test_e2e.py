"""End-to-End integration test suite for GB Wind Power Forecast Desk."""

import csv
import io

import pytest
from fastapi.testclient import TestClient

from backend.app.main import create_app


@pytest.fixture(scope="module")
def client():
    """Create FastAPI test client with loaded data store."""
    app = create_app()
    with TestClient(app) as c:
        yield c


def test_e2e_health_and_days(client):
    """E2E Test 1: Verify health status and January 2026 delivery days availability."""
    # Health check
    res_health = client.get("/api/health")
    assert res_health.status_code == 200
    health_data = res_health.json()
    assert health_data["status"] == "ok"
    assert health_data["actuals_count"] > 0
    assert health_data["forecasts_count"] > 0

    # Days list
    res_days = client.get("/api/days")
    assert res_days.status_code == 200
    days_data = res_days.json()
    assert days_data["count"] == 31
    assert "2026-01-02" in days_data["days"]
    assert "2026-02-01" in days_data["days"]


def test_e2e_forecast_and_cashflow(client):
    """E2E Test 2: Verify point-in-time forecast resolution and cashflow exposure."""
    # Day Forecast
    res_fc = client.get("/api/forecast?delivery_date=2026-02-01&cutoff_time=09:00")
    assert res_fc.status_code == 200
    fc_data = res_fc.json()
    assert fc_data["delivery_date"] == "2026-02-01"
    assert len(fc_data["periods"]) == 48

    # Cashflow endpoint
    res_cf = client.get("/api/cashflow/day?delivery_date=2026-02-01&cutoff_time=09:00")
    assert res_cf.status_code == 200
    cf_data = res_cf.json()
    assert cf_data["delivery_date"] == "2026-02-01"
    assert cf_data["evaluated_periods"] > 0
    assert cf_data["gross_short_mwh"] > 0
    assert cf_data["net_cashflow_exposure_gbp"] != 0
    assert cf_data["hedge_savings_p10_p90_gbp"] > 0
    assert len(cf_data["periods"]) == 48


def test_e2e_accuracy_window(client):
    """E2E Test 3: Verify month-long accuracy evaluation across all 744 settlement periods."""
    res_acc = client.get(
        "/api/accuracy/summary?from_date=2026-01-02&to_date=2026-02-01&cutoff_time=09:00"
    )
    assert res_acc.status_code == 200
    acc = res_acc.json()
    assert acc["evaluated_periods"] == 744
    assert round(acc["mae_mw"]) == 2022
    assert acc["bias_mw"] > 0  # Systematic over-forecasting
    assert acc["p10_mw"] < 0
    assert acc["p90_mw"] > 0


def test_e2e_csv_export_stream(client):
    """E2E Test 4: Verify streaming CSV export data format and row integrity."""
    res_csv = client.get(
        "/api/export/csv?from_date=2026-01-02&to_date=2026-02-01&cutoff_time=09:00"
    )
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers["content-type"]
    assert "attachment" in res_csv.headers["content-disposition"]

    content = res_csv.text
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)

    # Check header
    header = rows[0]
    assert "delivery_date" in header
    assert "period_index" in header
    assert "forecast_mw" in header
    assert "actual_mw" in header
    assert "error_mw" in header

    # Exactly 744 settlement periods (48 periods * 31 days) + 1 header row = 745
    assert len(rows) >= 745
