"""Health check endpoint router."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.dependencies import get_data_store
from backend.app.schemas.api_models import HealthResponse
from backend.app.services.data_store import DataStore

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def get_health(store: DataStore = Depends(get_data_store)) -> HealthResponse:
    """Return data integrity status, row counts, and UTC server timestamp."""
    if not store.has_snapshot():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Data snapshot not available. Run backend/ingest.py first.",
        )

    health = store.get_data_health()
    return HealthResponse(
        status="ok" if health.health_ok else "degraded",
        server_time_utc=datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        **health.model_dump(),
    )
