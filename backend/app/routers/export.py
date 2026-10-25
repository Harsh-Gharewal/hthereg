"""CSV export endpoint router."""

import csv
import io
from collections.abc import Generator
from datetime import datetime

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from backend.app.config import (
    DEFAULT_CUTOFF_TIME,
    JANUARY_2026_END_DELIVERY,
    JANUARY_2026_START_DELIVERY,
)
from backend.app.dependencies import get_data_store
from backend.app.services.data_store import DataStore

router = APIRouter(prefix="/export", tags=["Export"])

CSV_COLUMNS = [
    "delivery_date",
    "period_index",
    "start_time_utc",
    "start_time_local",
    "forecast_mw",
    "publish_time_utc",
    "horizon_hours",
    "actual_mw",
    "error_mw",
]


def _format_cell(val: object) -> object:
    if val is None or pd.isna(val):
        return ""
    if isinstance(val, pd.Timestamp):
        return val.strftime("%Y-%m-%dT%H:%M:%SZ")
    return val


def generate_csv_stream(df: pd.DataFrame) -> Generator[str, None, None]:
    """Stream CSV rows iteratively to avoid in-memory buffering for large ranges."""
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(CSV_COLUMNS)
    yield output.getvalue()
    output.seek(0)
    output.truncate(0)

    for _, row in df.iterrows():
        writer.writerow([_format_cell(row.get(col)) for col in CSV_COLUMNS])
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)


@router.get("/csv")
def export_csv(
    from_date: str | None = Query(None, description="Start delivery date YYYY-MM-DD"),
    to_date: str | None = Query(None, description="End delivery date YYYY-MM-DD"),
    cutoff_time: str = Query(
        DEFAULT_CUTOFF_TIME,
        pattern=r"^([01]\d|2[0-3]):[0-5]\d$",
        description="Cut-off time HH:MM on D-1",
    ),
    store: DataStore = Depends(get_data_store),
) -> StreamingResponse:
    """Download resolved evaluation period records for date range as a UTF-8 CSV."""
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

    df = store.evaluate_period_range(start_str, end_str, cutoff_time)

    return StreamingResponse(
        generate_csv_stream(df),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=wind_forecast_eval.csv",
        },
    )
