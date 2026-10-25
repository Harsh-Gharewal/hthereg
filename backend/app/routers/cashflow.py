"""Router for financial cashflow & imbalance settlement risk endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.dependencies import get_data_store
from backend.app.services.cashflow import (
    DEFAULT_IMBALANCE_PRICE_GBP_PER_MWH,
    DayCashflowSummary,
    compute_day_cashflow,
)
from backend.app.services.data_store import DataStore
from backend.app.services.resolver import resolve_day_forecast

router = APIRouter(prefix="/cashflow", tags=["Cashflow & Imbalance Risk"])


@router.get("/day", response_model=DayCashflowSummary)
def get_day_cashflow_endpoint(
    delivery_date: Annotated[str, Query(description="Delivery date (YYYY-MM-DD)")],
    cutoff_time: Annotated[str, Query(description="D-1 cut-off time (HH:MM)")] = "09:00",
    base_price_gbp: Annotated[
        float, Query(description="Baseload imbalance price in GBP/MWh")
    ] = DEFAULT_IMBALANCE_PRICE_GBP_PER_MWH,
    store: DataStore = Depends(get_data_store),
) -> DayCashflowSummary:
    """Calculate balancing mechanism cashflow exposure and hedge savings for a delivery day."""
    if not store.has_snapshot():
        raise HTTPException(status_code=503, detail="BMRS snapshot data not loaded")

    day_summary = resolve_day_forecast(
        delivery_date_str=delivery_date,
        cutoff_time_str=cutoff_time,
        forecasts_df=store.get_forecasts(),
        actuals_df=store.get_actuals(),
        historical_band_map=store.get_historical_band_map(),
    )

    return compute_day_cashflow(day_summary, base_price_gbp=base_price_gbp)
