"""Forecast and delivery days router."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.config import (
    DEFAULT_CUTOFF_TIME,
    JANUARY_2026_END_DELIVERY,
    JANUARY_2026_START_DELIVERY,
)
from backend.app.dependencies import get_data_store
from backend.app.schemas.api_models import DayListResponse, ForecastResponse
from backend.app.services.data_store import DataStore
from backend.app.services.resolver import resolve_day_forecast

router = APIRouter(tags=["Forecast"])


@router.get("/days", response_model=DayListResponse)
def get_available_days(store: DataStore = Depends(get_data_store)) -> DayListResponse:
    """Return all available delivery days in the January 2026 evaluation period."""
    days = store.get_available_delivery_days()
    return DayListResponse(days=days, count=len(days))


@router.get("/forecast", response_model=ForecastResponse)
def get_forecast(
    delivery_date: str = Query(..., description="Delivery date YYYY-MM-DD"),
    cutoff_time: str = Query(
        DEFAULT_CUTOFF_TIME,
        pattern=r"^([01]\d|2[0-3]):[0-5]\d$",
        description="Cut-off time HH:MM on D-1 in UK local time",
    ),
    store: DataStore = Depends(get_data_store),
) -> ForecastResponse:
    """Resolve the 48-period forecast for a given delivery date and cutoff time."""
    # Validate delivery date format and window
    try:
        dt = datetime.strptime(delivery_date, "%Y-%m-%d").date()
        min_dt = datetime.strptime(JANUARY_2026_START_DELIVERY, "%Y-%m-%d").date()
        max_dt = datetime.strptime(JANUARY_2026_END_DELIVERY, "%Y-%m-%d").date()
        if dt < min_dt or dt > max_dt:
            raise ValueError()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"delivery_date must be between {JANUARY_2026_START_DELIVERY} "
                f"and {JANUARY_2026_END_DELIVERY}"
            ),
        )

    if not store.has_snapshot():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Data snapshot not available. Run backend/ingest.py first.",
        )

    band_map = store.get_historical_band_map()
    actuals = store.get_actuals()
    forecasts = store.get_forecasts()

    summary = resolve_day_forecast(
        delivery_date_str=delivery_date,
        cutoff_time_str=cutoff_time,
        forecasts_df=forecasts,
        actuals_df=actuals,
        historical_band_map=band_map,
    )

    return ForecastResponse(
        **summary.model_dump(),
        requested_cutoff=cutoff_time,
    )
