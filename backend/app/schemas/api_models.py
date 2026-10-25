"""HTTP API request and response models."""

from pydantic import BaseModel, Field

from backend.app.schemas.data_models import (
    AccuracySummary,
    DataHealthStatus,
    DayResolutionSummary,
    ErrorDistribution,
    HorizonAccuracyBucket,
    HourAccuracyBucket,
)


class AccuracyWindowMetadata(BaseModel):
    """Metadata describing the query window and cutoff time for accuracy evaluation."""

    from_date: str = Field(..., description="Start delivery date YYYY-MM-DD")
    to_date: str = Field(..., description="End delivery date YYYY-MM-DD")
    cutoff_time: str = Field(..., description="Cut-off time HH:MM on D-1")


class DayListResponse(BaseModel):
    """List of available delivery days."""

    days: list[str] = Field(..., description="Available delivery dates in YYYY-MM-DD format")
    count: int = Field(..., description="Total count of available delivery days")


class ForecastResponse(DayResolutionSummary):
    """Response model for resolved 48-period forecast for a day."""

    requested_cutoff: str | None = Field(
        None, description="Echoed cutoff time string requested by the client"
    )


class AccuracySummaryResponse(AccuracySummary):
    """Windowed summary accuracy metrics response."""

    window: AccuracyWindowMetadata
    evaluated_periods: int = Field(
        ..., description="Number of evaluated half-hour points (alias for count)"
    )


class HorizonAccuracyResponse(BaseModel):
    """Accuracy metrics grouped by forecast horizon."""

    window: AccuracyWindowMetadata
    buckets: list[HorizonAccuracyBucket]


class HourAccuracyResponse(BaseModel):
    """Accuracy metrics grouped by hour of the day."""

    window: AccuracyWindowMetadata
    hours: list[HourAccuracyBucket]


class DistributionResponse(ErrorDistribution):
    """Forecast error histogram distribution response."""

    window: AccuracyWindowMetadata


class HealthResponse(DataHealthStatus):
    """Service and data health status response."""

    status: str = Field("ok", description="Overall system health status")
    server_time_utc: str = Field(..., description="Current UTC timestamp of the server")
