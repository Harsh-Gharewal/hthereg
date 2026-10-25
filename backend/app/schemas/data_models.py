"""Typed data schemas for domain models, resolver outputs, and metrics."""

from datetime import datetime

from pydantic import BaseModel, Field


class HalfHourPeriod(BaseModel):
    """Represents a single 30-minute settlement period in a delivery day."""

    period_index: int = Field(..., description="1-indexed settlement period (1 to 48)")
    start_time_utc: datetime = Field(..., description="Start of settlement half-hour in UTC")
    start_time_local: str = Field(
        ..., description="Start of settlement half-hour in Europe/London formatted string"
    )
    end_time_utc: datetime = Field(..., description="End of settlement half-hour in UTC")
    forecast_mw: float | None = Field(None, description="Latest forecast before cutoff in MW")
    publish_time_utc: datetime | None = Field(
        None, description="Publish timestamp of chosen forecast in UTC"
    )
    publish_time_local: str | None = Field(None, description="Publish timestamp in Europe/London")
    horizon_hours: float | None = Field(
        None, description="Forecast horizon: start_time minus publish_time in hours"
    )
    actual_mw: float | None = Field(None, description="Actual outturn wind generation in MW")
    error_mw: float | None = Field(None, description="Forecast error in MW: forecast - actual")
    error_band_p10_mw: float | None = Field(
        None, description="10th percentile bound based on historical errors"
    )
    error_band_p90_mw: float | None = Field(
        None, description="90th percentile bound based on historical errors"
    )


class DayResolutionSummary(BaseModel):
    """Summary and 48-period series for a delivery day."""

    delivery_date: str = Field(..., description="Delivery date YYYY-MM-DD")
    cutoff_time: str = Field(..., description="Configured cut-off time (HH:MM) on D-1")
    cutoff_datetime_utc: datetime = Field(..., description="Calculated cutoff datetime in UTC")
    peak_forecast_mw: float | None = None
    avg_forecast_mw: float | None = None
    peak_actual_mw: float | None = None
    avg_actual_mw: float | None = None
    mean_error_mw: float | None = None
    mae_mw: float | None = None
    periods: list[HalfHourPeriod] = Field(default_factory=list)


class AccuracySummary(BaseModel):
    """Summary error metrics across an evaluated window."""

    count: int = Field(..., description="Number of evaluated half-hour points")
    bias_mw: float = Field(..., description="Mean error: forecast - actual (MW)")
    mae_mw: float = Field(..., description="Mean absolute error (MW)")
    rmse_mw: float = Field(..., description="Root mean squared error (MW)")
    nmae_pct: float | None = Field(None, description="Normalised MAE: (MAE / mean actual) * 100%")
    p10_mw: float = Field(..., description="10th percentile of error")
    p50_mw: float = Field(..., description="Median error")
    p90_mw: float = Field(..., description="90th percentile of error")
    min_error_mw: float = Field(...)
    max_error_mw: float = Field(...)


class HorizonAccuracyBucket(BaseModel):
    """Accuracy metrics grouped by forecast lead time horizon."""

    horizon_min_hours: float
    horizon_max_hours: float
    bucket_label: str
    count: int
    mae_mw: float
    bias_mw: float


class HourAccuracyBucket(BaseModel):
    """Accuracy metrics grouped by hour of the delivery day (0 to 23)."""

    hour: int
    hour_label: str
    count: int
    mae_mw: float
    bias_mw: float
    avg_actual_mw: float
    avg_forecast_mw: float


class HistogramBin(BaseModel):
    """Single bin for error distribution."""

    bin_start: float
    bin_end: float
    count: int


class ErrorDistribution(BaseModel):
    """Histogram of errors with quantile markers."""

    bins: list[HistogramBin]
    p10_mw: float
    p50_mw: float
    p90_mw: float
    total_count: int


class DataHealthStatus(BaseModel):
    """Status and data integrity metrics for ingested BMRS datasets."""

    actuals_count: int
    forecasts_count: int
    earliest_actual_utc: str | None = None
    latest_actual_utc: str | None = None
    earliest_forecast_publish_utc: str | None = None
    latest_forecast_publish_utc: str | None = None
    missing_actual_periods: int = 0
    duplicate_rows_detected: int = 0
    health_ok: bool = True
