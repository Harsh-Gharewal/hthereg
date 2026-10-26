"""Configuration settings for the Day-Ahead Wind Forecast platform."""

from pathlib import Path
from zoneinfo import ZoneInfo

from pydantic import BaseModel

# Base paths
BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_DIR / "data"

# Timezone
LONDON_TZ = ZoneInfo("Europe/London")
UTC_TZ = ZoneInfo("UTC")

# Trading Desk Defaults
DEFAULT_CUTOFF_TIME = "09:00"  # 09:00 Europe/London on D-1
SETTLEMENT_PERIOD_MINUTES = 30
PERIODS_PER_DAY = 48

# January 2026 Evaluation Window
# Decisions made in Jan 2026: D-1 is 2026-01-01 to 2026-01-31 -> Delivery days 2026-01-02 to 2026-02-01
JANUARY_2026_START_DELIVERY = "2026-01-02"
JANUARY_2026_END_DELIVERY = "2026-02-01"

# Ingestion Window (buffer included: fetch actuals 1 Jan to 2 Feb, forecasts published 30 Dec 2025 to 31 Jan 2026)
INGEST_ACTUALS_START = "2026-01-01"
INGEST_ACTUALS_END = "2026-02-02"
INGEST_FORECAST_PUBLISH_START = "2025-12-30T00:00:00Z"
INGEST_FORECAST_PUBLISH_END = "2026-02-01T23:59:59Z"

# File paths
ACTUALS_PARQUET = DATA_DIR / "actuals.parquet"
FORECASTS_PARQUET = DATA_DIR / "forecasts.parquet"
SQLITE_DB_PATH = DATA_DIR / "bmrs.db"


class Settings(BaseModel):
    app_name: str = "WindWise — UK Day-Ahead Wind Forecast Desk"
    default_cutoff: str = DEFAULT_CUTOFF_TIME
    data_dir: Path = DATA_DIR
    actuals_file: Path = ACTUALS_PARQUET
    forecasts_file: Path = FORECASTS_PARQUET
    sqlite_db: Path = SQLITE_DB_PATH


settings = Settings()
