"""Accuracy evaluation endpoints router."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.config import (
    DEFAULT_CUTOFF_TIME,
    JANUARY_2026_END_DELIVERY,
    JANUARY_2026_START_DELIVERY,
)
from backend.app.dependencies import get_data_store
from backend.app.schemas.api_models import (
    AccuracySummaryResponse,
    AccuracyWindowMetadata,
    DistributionResponse,
    HorizonAccuracyResponse,
    HourAccuracyResponse,
)
from backend.app.services.data_store import DataStore
from backend.app.services.metrics import (
    calculate_accuracy_by_horizon,
    calculate_accuracy_by_hour,
    calculate_error_distribution,
    calculate_summary_metrics,
)

router = APIRouter(prefix="/accuracy", tags=["Accuracy"])


def _validate_and_get_window(
    from_date: str | None,
    to_date: str | None,
    cutoff_time: str,
    store: DataStore,
) -> tuple[str, str, str, AccuracyWindowMetadata]:
    """Validate window date parameters and snapshot availability."""
    start_str = from_date or JANUARY_2026_START_DELIVERY
    end_str = to_date or JANUARY_2026_END_DELIVERY

    try:
        start_d = datetime.strptime(start_str, "%Y-%m-%d").date()
        end_d = datetime.strptime(end_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dates must be in YYYY-MM-DD format",
        )

    if start_d > end_d:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="from_date must be before or equal to to_date",
        )

    if not store.has_snapshot():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Data snapshot not available. Run backend/ingest.py first.",
        )

    window = AccuracyWindowMetadata(
        from_date=start_str,
        to_date=end_str,
        cutoff_time=cutoff_time,
    )
    return start_str, end_str, cutoff_time, window


@router.get("/summary", response_model=AccuracySummaryResponse)
def get_accuracy_summary(
    from_date: str | None = Query(None, description="Start delivery date YYYY-MM-DD"),
    to_date: str | None = Query(None, description="End delivery date YYYY-MM-DD"),
    cutoff_time: str = Query(
        DEFAULT_CUTOFF_TIME,
        pattern=r"^([01]\d|2[0-3]):[0-5]\d$",
        description="Cut-off time HH:MM on D-1",
    ),
    store: DataStore = Depends(get_data_store),
) -> AccuracySummaryResponse:
    """Return overall summary metrics (Bias, MAE, RMSE, nMAE, P10/P50/P90) for the window."""
    start_str, end_str, cutoff, window = _validate_and_get_window(
        from_date, to_date, cutoff_time, store
    )
    df = store.evaluate_period_range(start_str, end_str, cutoff)

    valid = df.dropna(subset=["error_mw"])
    summary = calculate_summary_metrics(
        errors=valid["error_mw"].tolist(),
        actuals=valid["actual_mw"].tolist() if "actual_mw" in valid.columns else None,
    )

    return AccuracySummaryResponse(
        **summary.model_dump(),
        evaluated_periods=summary.count,
        window=window,
    )


@router.get("/by-horizon", response_model=HorizonAccuracyResponse)
def get_accuracy_by_horizon(
    from_date: str | None = Query(None, description="Start delivery date YYYY-MM-DD"),
    to_date: str | None = Query(None, description="End delivery date YYYY-MM-DD"),
    cutoff_time: str = Query(
        DEFAULT_CUTOFF_TIME,
        pattern=r"^([01]\d|2[0-3]):[0-5]\d$",
        description="Cut-off time HH:MM on D-1",
    ),
    store: DataStore = Depends(get_data_store),
) -> HorizonAccuracyResponse:
    """Return accuracy metrics grouped by forecast lead-time horizon buckets."""
    start_str, end_str, cutoff, window = _validate_and_get_window(
        from_date, to_date, cutoff_time, store
    )
    df = store.evaluate_period_range(start_str, end_str, cutoff)
    buckets = calculate_accuracy_by_horizon(df)

    return HorizonAccuracyResponse(window=window, buckets=buckets)


@router.get("/by-hour", response_model=HourAccuracyResponse)
def get_accuracy_by_hour(
    from_date: str | None = Query(None, description="Start delivery date YYYY-MM-DD"),
    to_date: str | None = Query(None, description="End delivery date YYYY-MM-DD"),
    cutoff_time: str = Query(
        DEFAULT_CUTOFF_TIME,
        pattern=r"^([01]\d|2[0-3]):[0-5]\d$",
        description="Cut-off time HH:MM on D-1",
    ),
    store: DataStore = Depends(get_data_store),
) -> HourAccuracyResponse:
    """Return accuracy metrics grouped by hour of the day in UK local time (00 to 23)."""
    start_str, end_str, cutoff, window = _validate_and_get_window(
        from_date, to_date, cutoff_time, store
    )
    df = store.evaluate_period_range(start_str, end_str, cutoff)
    hours = calculate_accuracy_by_hour(df)

    return HourAccuracyResponse(window=window, hours=hours)


@router.get("/distribution", response_model=DistributionResponse)
def get_accuracy_distribution(
    from_date: str | None = Query(None, description="Start delivery date YYYY-MM-DD"),
    to_date: str | None = Query(None, description="End delivery date YYYY-MM-DD"),
    cutoff_time: str = Query(
        DEFAULT_CUTOFF_TIME,
        pattern=r"^([01]\d|2[0-3]):[0-5]\d$",
        description="Cut-off time HH:MM on D-1",
    ),
    bins: int = Query(20, ge=5, le=100, description="Number of histogram bins"),
    store: DataStore = Depends(get_data_store),
) -> DistributionResponse:
    """Return histogram distribution of forecast errors with quantile markers."""
    start_str, end_str, cutoff, window = _validate_and_get_window(
        from_date, to_date, cutoff_time, store
    )
    df = store.evaluate_period_range(start_str, end_str, cutoff)
    valid = df.dropna(subset=["error_mw"])
    dist = calculate_error_distribution(valid["error_mw"].tolist(), num_bins=bins)

    return DistributionResponse(window=window, **dist.model_dump())
