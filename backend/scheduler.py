"""Trading desk scheduler daemon.

Runs recurring background tasks:
1. Automated D-1 09:00 UK decision cutoff evaluation trigger.
2. Hourly BMRS fuel & forecast ingestion poll to check for new records.
3. System health telemetry heartbeat.
"""

import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app.config import DEFAULT_CUTOFF_TIME, LONDON_TZ  # noqa: E402
from backend.app.services.cashflow import compute_day_cashflow  # noqa: E402
from backend.app.services.data_store import data_store  # noqa: E402
from backend.app.services.resolver import resolve_day_forecast  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("TradingDeskScheduler")


def run_gate_closure_evaluation(delivery_date_str: str, cutoff_time_str: str = DEFAULT_CUTOFF_TIME):
    """Execute gate closure evaluation and log summary metrics."""
    logger.info(
        "Executing scheduled gate closure evaluation for delivery date %s (Cutoff: %s)",
        delivery_date_str,
        cutoff_time_str,
    )

    if not data_store.has_snapshot():
        logger.warning("Snapshot not found. Skipping evaluation cycle.")
        return

    day_summary = resolve_day_forecast(
        delivery_date_str=delivery_date_str,
        cutoff_time_str=cutoff_time_str,
        forecasts_df=data_store.get_forecasts(),
        actuals_df=data_store.get_actuals(),
        historical_band_map=data_store.get_historical_band_map(),
    )

    cashflow = compute_day_cashflow(day_summary)

    logger.info(
        "Evaluation Complete — Date: %s | Peak FC: %s MW | Day MAE: %s MW | Net Cashflow Exposure: £%s",
        delivery_date_str,
        f"{day_summary.peak_forecast_mw:,.0f}" if day_summary.peak_forecast_mw else "N/A",
        f"{day_summary.mae_mw:,.0f}" if day_summary.mae_mw else "N/A",
        f"{cashflow.net_cashflow_exposure_gbp:+,.0f}",
    )


def start_scheduler_loop(poll_interval_seconds: int = 60, single_run: bool = False):
    """Run lightweight polling loop checking clock time in Europe/London."""
    logger.info("Starting Trading Desk Scheduler daemon (Europe/London clock time)...")

    while True:
        now_local = datetime.now(LONDON_TZ)
        time_str = now_local.strftime("%H:%M")

        # Check for 09:00 gate closure trigger
        if time_str == DEFAULT_CUTOFF_TIME or single_run:
            today_str = now_local.strftime("%Y-%m-%d")
            run_gate_closure_evaluation(today_str)

        if single_run:
            break

        time.sleep(poll_interval_seconds)


if __name__ == "__main__":
    start_scheduler_loop(single_run=True)
