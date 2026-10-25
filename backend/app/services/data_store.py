"""Data store layer for reading and caching historical BMRS Parquet / SQLite snapshots."""

import os
import sqlite3
from datetime import datetime, timedelta

import pandas as pd

from backend.app.config import (
    ACTUALS_PARQUET,
    DEFAULT_CUTOFF_TIME,
    FORECASTS_PARQUET,
    JANUARY_2026_END_DELIVERY,
    JANUARY_2026_START_DELIVERY,
    SQLITE_DB_PATH,
)
from backend.app.schemas.data_models import DataHealthStatus
from backend.app.services.metrics import compute_historical_band_map
from backend.app.services.resolver import resolve_day_forecast


class DataStore:
    def __init__(
        self,
        actuals_path: str | None = None,
        forecasts_path: str | None = None,
        db_path: str | None = None,
    ):
        self.actuals_path = str(actuals_path or ACTUALS_PARQUET)
        self.forecasts_path = str(forecasts_path or FORECASTS_PARQUET)
        self.db_path = str(db_path or SQLITE_DB_PATH)

        self._actuals_cache: pd.DataFrame | None = None
        self._forecasts_cache: pd.DataFrame | None = None
        self._band_map_cache: dict[int, tuple[float, float]] | None = None
        self._range_cache: dict[tuple[str, str, str], pd.DataFrame] = {}

    def has_snapshot(self) -> bool:
        """Check if snapshot data is present on disk or in memory cache."""
        if self._actuals_cache is not None and not self._actuals_cache.empty:
            return True
        has_parquet = os.path.exists(self.actuals_path) and os.path.exists(self.forecasts_path)
        has_sqlite = os.path.exists(self.db_path)
        return has_parquet or has_sqlite

    def get_actuals(self) -> pd.DataFrame:
        """Load and cache actuals DataFrame."""
        if self._actuals_cache is not None:
            return self._actuals_cache

        if os.path.exists(self.actuals_path):
            df = pd.read_parquet(self.actuals_path)
        elif os.path.exists(self.db_path):
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query("SELECT start_time_utc, generation_mw FROM actuals", conn)
        else:
            df = pd.DataFrame(columns=["start_time_utc", "generation_mw"])

        if not df.empty:
            df["start_time_utc"] = pd.to_datetime(df["start_time_utc"], utc=True)
            df = (
                df.sort_values("start_time_utc")
                .drop_duplicates(subset=["start_time_utc"])
                .reset_index(drop=True)
            )

        self._actuals_cache = df
        return self._actuals_cache

    def get_forecasts(self) -> pd.DataFrame:
        """Load and cache forecasts DataFrame."""
        if self._forecasts_cache is not None:
            return self._forecasts_cache

        if os.path.exists(self.forecasts_path):
            df = pd.read_parquet(self.forecasts_path)
        elif os.path.exists(self.db_path):
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(
                    "SELECT start_time_utc, publish_time_utc, generation_mw FROM forecasts", conn
                )
        else:
            df = pd.DataFrame(columns=["start_time_utc", "publish_time_utc", "generation_mw"])

        if not df.empty:
            df["start_time_utc"] = pd.to_datetime(df["start_time_utc"], utc=True)
            df["publish_time_utc"] = pd.to_datetime(df["publish_time_utc"], utc=True)
            df = (
                df.sort_values(["start_time_utc", "publish_time_utc"])
                .drop_duplicates(subset=["start_time_utc", "publish_time_utc"])
                .reset_index(drop=True)
            )

        self._forecasts_cache = df
        return self._forecasts_cache

    def set_data(self, actuals_df: pd.DataFrame, forecasts_df: pd.DataFrame):
        """Manually inject in-memory DataFrames (used in tests or after ingestion)."""
        act = actuals_df.copy()
        if not act.empty:
            act["start_time_utc"] = pd.to_datetime(act["start_time_utc"], utc=True)
            act = (
                act.sort_values("start_time_utc")
                .drop_duplicates(subset=["start_time_utc"])
                .reset_index(drop=True)
            )

        fc = forecasts_df.copy()
        if not fc.empty:
            fc["start_time_utc"] = pd.to_datetime(fc["start_time_utc"], utc=True)
            fc["publish_time_utc"] = pd.to_datetime(fc["publish_time_utc"], utc=True)
            fc = (
                fc.sort_values(["start_time_utc", "publish_time_utc"])
                .drop_duplicates(subset=["start_time_utc", "publish_time_utc"])
                .reset_index(drop=True)
            )

        self._actuals_cache = act
        self._forecasts_cache = fc
        self._band_map_cache = None

    def get_available_delivery_days(self) -> list[str]:
        """List distinct delivery days available in January 2026 window."""
        start_d = datetime.strptime(JANUARY_2026_START_DELIVERY, "%Y-%m-%d").date()
        end_d = datetime.strptime(JANUARY_2026_END_DELIVERY, "%Y-%m-%d").date()

        days = []
        curr = start_d
        while curr <= end_d:
            days.append(curr.strftime("%Y-%m-%d"))
            curr += timedelta(days=1)
        return days

    def evaluate_period_range(
        self,
        from_date_str: str | None = None,
        to_date_str: str | None = None,
        cutoff_time_str: str = DEFAULT_CUTOFF_TIME,
    ) -> pd.DataFrame:
        """Resolve all days in the specified range and concatenate resolved period records."""
        from_d = from_date_str or JANUARY_2026_START_DELIVERY
        to_d = to_date_str or JANUARY_2026_END_DELIVERY
        cache_key = (from_d, to_d, cutoff_time_str)
        if cache_key in self._range_cache:
            return self._range_cache[cache_key]

        start = datetime.strptime(from_d, "%Y-%m-%d").date()
        end = datetime.strptime(to_d, "%Y-%m-%d").date()

        actuals = self.get_actuals()
        forecasts = self.get_forecasts()

        rows = []
        curr = start
        while curr <= end:
            day_str = curr.strftime("%Y-%m-%d")
            res = resolve_day_forecast(
                delivery_date_str=day_str,
                cutoff_time_str=cutoff_time_str,
                forecasts_df=forecasts,
                actuals_df=actuals,
                historical_band_map=None,
            )
            for p in res.periods:
                rows.append(
                    {
                        "delivery_date": day_str,
                        "period_index": p.period_index,
                        "start_time_utc": p.start_time_utc,
                        "start_time_local": p.start_time_local,
                        "end_time_utc": p.end_time_utc,
                        "forecast_mw": p.forecast_mw,
                        "publish_time_utc": p.publish_time_utc,
                        "publish_time_local": p.publish_time_local,
                        "horizon_hours": p.horizon_hours,
                        "actual_mw": p.actual_mw,
                        "error_mw": p.error_mw,
                    }
                )
            curr += timedelta(days=1)

        result_df = pd.DataFrame(rows)
        self._range_cache[cache_key] = result_df
        return result_df

    def get_historical_band_map(self) -> dict[int, tuple[float, float]]:
        """Compute or retrieve cached historical P10/P90 error band map by horizon."""
        if self._band_map_cache is not None:
            return self._band_map_cache

        eval_df = self.evaluate_period_range()
        band_map = compute_historical_band_map(eval_df)
        self._band_map_cache = band_map
        return band_map

    def get_data_health(self) -> DataHealthStatus:
        """Inspect datasets and report integrity, gaps, row counts."""
        acts = self.get_actuals()
        fcs = self.get_forecasts()

        earliest_act = (
            acts["start_time_utc"].min().strftime("%Y-%m-%dT%H:%M:%SZ") if not acts.empty else None
        )
        latest_act = (
            acts["start_time_utc"].max().strftime("%Y-%m-%dT%H:%M:%SZ") if not acts.empty else None
        )

        earliest_pub = (
            fcs["publish_time_utc"].min().strftime("%Y-%m-%dT%H:%M:%SZ") if not fcs.empty else None
        )
        latest_pub = (
            fcs["publish_time_utc"].max().strftime("%Y-%m-%dT%H:%M:%SZ") if not fcs.empty else None
        )

        # Check for missing half-hour periods in actuals between Jan 1 and Feb 1
        missing_periods = 0
        if not acts.empty and earliest_act and latest_act:
            min_ts = acts["start_time_utc"].min()
            max_ts = acts["start_time_utc"].max()
            expected_periods = int((max_ts - min_ts).total_seconds() / 1800) + 1
            missing_periods = max(0, expected_periods - len(acts))

        return DataHealthStatus(
            actuals_count=len(acts),
            forecasts_count=len(fcs),
            earliest_actual_utc=earliest_act,
            latest_actual_utc=latest_act,
            earliest_forecast_publish_utc=earliest_pub,
            latest_forecast_publish_utc=latest_pub,
            missing_actual_periods=missing_periods,
            duplicate_rows_detected=0,
            health_ok=(len(acts) > 0 and len(fcs) > 0 and missing_periods < 5),
        )


# Global singleton instance
data_store = DataStore()
