"""Integration tests for FastAPI REST API endpoints."""

from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    """Validate /api/health returns 200, health_ok, and non-zero counts."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["health_ok"] is True
    assert data["actuals_count"] > 0
    assert data["forecasts_count"] > 0
    assert "server_time_utc" in data


def test_days_list(client: TestClient):
    """Validate /api/days returns all 31 days of January 2026 evaluation window."""
    response = client.get("/api/days")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 31
    assert len(data["days"]) == 31
    assert data["days"][0] == "2026-01-02"
    assert data["days"][-1] == "2026-02-01"


def test_forecast_valid_date(client: TestClient):
    """Validate /api/forecast returns 48 periods with calculated metrics."""
    response = client.get("/api/forecast?delivery_date=2026-01-15&cutoff_time=09:00")
    assert response.status_code == 200
    data = response.json()
    assert data["delivery_date"] == "2026-01-15"
    assert data["cutoff_time"] == "09:00"
    assert len(data["periods"]) == 48
    assert data["periods"][0]["period_index"] == 1
    assert data["periods"][-1]["period_index"] == 48
    assert data["peak_forecast_mw"] is not None
    assert data["avg_forecast_mw"] is not None


def test_forecast_invalid_date(client: TestClient):
    """Validate /api/forecast returns 400 for delivery date outside range."""
    response = client.get("/api/forecast?delivery_date=2025-12-31")
    assert response.status_code == 400
    assert "delivery_date must be between 2026-01-02 and 2026-02-01" in response.json()["detail"]


def test_forecast_invalid_cutoff_format(client: TestClient):
    """Validate /api/forecast returns 422 for malformed cut-off time."""
    response = client.get("/api/forecast?delivery_date=2026-01-15&cutoff_time=25:00")
    assert response.status_code == 422
    response2 = client.get("/api/forecast?delivery_date=2026-01-15&cutoff_time=not-a-time")
    assert response2.status_code == 422


def test_accuracy_summary_defaults(client: TestClient):
    """Validate default /api/accuracy/summary has all required metric fields."""
    response = client.get("/api/accuracy/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] > 0
    assert data["mae_mw"] > 0
    assert "bias_mw" in data
    assert "rmse_mw" in data
    assert "p10_mw" in data
    assert "p50_mw" in data
    assert "p90_mw" in data
    assert "window" in data
    assert data["window"]["cutoff_time"] == "09:00"


def test_accuracy_custom_window(client: TestClient):
    """Validate /api/accuracy/summary handles custom 3-day window."""
    response = client.get("/api/accuracy/summary?from_date=2026-01-10&to_date=2026-01-12")
    assert response.status_code == 200
    data = response.json()
    # 3 days with hourly forecast publishing gives 72 evaluated points
    assert data["count"] == 72
    assert data["window"]["from_date"] == "2026-01-10"
    assert data["window"]["to_date"] == "2026-01-12"


def test_accuracy_by_horizon(client: TestClient):
    """Validate /api/accuracy/by-horizon groups into 5 lead-time buckets."""
    response = client.get("/api/accuracy/by-horizon")
    assert response.status_code == 200
    data = response.json()
    assert "buckets" in data
    assert len(data["buckets"]) == 5
    total_count = sum(b["count"] for b in data["buckets"])
    assert total_count > 0
    # For day-ahead cutoff (15h-39.5h horizon), active buckets have count > 0 and positive MAE
    active_buckets = [b for b in data["buckets"] if b["count"] > 0]
    assert len(active_buckets) >= 3
    for b in active_buckets:
        assert b["mae_mw"] > 0


def test_accuracy_by_hour(client: TestClient):
    """Validate /api/accuracy/by-hour produces 24 local hour buckets."""
    response = client.get("/api/accuracy/by-hour")
    assert response.status_code == 200
    data = response.json()
    assert "hours" in data
    assert len(data["hours"]) == 24
    for h in data["hours"]:
        assert 0 <= h["hour"] <= 23
        assert h["count"] > 0


def test_accuracy_distribution(client: TestClient):
    """Validate /api/accuracy/distribution computes histogram bins and quantiles."""
    response = client.get("/api/accuracy/distribution?bins=20")
    assert response.status_code == 200
    data = response.json()
    assert len(data["bins"]) == 20
    assert data["total_count"] > 0
    bin_sum = sum(b["count"] for b in data["bins"])
    assert bin_sum == data["total_count"]
    assert "p10_mw" in data
    assert "p50_mw" in data
    assert "p90_mw" in data


def test_export_csv(client: TestClient):
    """Validate /api/export/csv streams CSV with correct headers and 48 rows."""
    response = client.get("/api/export/csv?from_date=2026-01-15&to_date=2026-01-15")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    lines = [line.strip() for line in response.text.strip().splitlines() if line.strip()]
    assert len(lines) == 49  # 1 header + 48 half-hour rows
    headers = lines[0].split(",")
    assert "delivery_date" in headers
    assert "period_index" in headers
    assert "forecast_mw" in headers
    assert "actual_mw" in headers
    assert "error_mw" in headers


def test_cutoff_sensitivity_via_api(client: TestClient):
    """Validate changing cut-off time alters resolved forecast values."""
    resp_0700 = client.get("/api/forecast?delivery_date=2026-01-15&cutoff_time=07:00")
    resp_1100 = client.get("/api/forecast?delivery_date=2026-01-15&cutoff_time=11:00")
    assert resp_0700.status_code == 200
    assert resp_1100.status_code == 200
    data_0700 = resp_0700.json()
    data_1100 = resp_1100.json()
    assert data_0700["avg_forecast_mw"] != data_1100["avg_forecast_mw"]
