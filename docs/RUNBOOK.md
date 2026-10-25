# GB Wind Forecast Evaluation Desk — Operational Runbook

## 1. System Overview

The **GB Wind Forecast Evaluation Desk** provides point-in-time forecast resolution and accuracy evaluation for Great Britain's national wind generation. It benchmarks National Grid ESO forecasts (`WINDFOR`) against official Elexon Balancing Mechanism Reporting Service (`BMRS`) metered actuals (`FUELHH`).

- **Delivery Window:** January 2026 (744 settlement periods across 31 delivery days: 2026-01-02 to 2026-02-01).
- **Core Cutoff Rule:** Decisions are evaluated as of **09:00 Europe/London on D-1** (prior to daily Day-Ahead EPEX and Nord Pool power auctions).
- **Settlement Periods:** 48 half-hour settlement periods per day (SP 01 to SP 48).

---

## 2. Daily Trading Desk Operations Workflow

### 2.1 Point-in-Time Day-Ahead Evaluation
Every morning at 09:00 UK time:
1. Navigate to the web dashboard at `http://localhost:5173/` or run the CLI:
   ```bash
   python -m backend.cli evaluate --date 2026-02-01 --cutoff 09:00
   ```
2. Review:
   - **Peak Forecast (MW):** Identifies highest anticipated transmission dispatch.
   - **P10–P90 Risk Envelope (MW):** Defines the 80% empirical confidence interval.
   - **Net Cashflow Exposure (£):** Estimated balancing cashout liability if outturn matches forecast deviation trends.
3. Export resolved dispatch data for day-ahead auction bid curves:
   ```bash
   python -m backend.cli export --date 2026-02-01 --cutoff 09:00 --out day_ahead_auction.csv
   ```

### 2.2 Sensitivity Analysis (Cutoff Scrubbing)
To assess how forecast accuracy evolves as the auction cutoff approaches:
- Adjust the D-1 Cutoff slider on the frontend between `01:00` and `23:00`.
- Notice that forecast error systematically narrows as gate closure nears (-20.5% error reduction from early D-1 cycles to final physical notification).

---

## 3. Data Pipeline & Snapshot Refresh

The ingestion service pulls raw records from Elexon BMRS Open APIs (`https://data.elexon.co.uk/bmrs/api/v1`):

```bash
# Re-fetch live BMRS records into Parquet and SQLite snapshot
.venv\Scripts\python backend/ingest.py
```

### Data Storage Architecture:
- `backend/data/actuals.parquet`: Metered outturn actuals from `FUELHH` (fuelType = `WIND`).
- `backend/data/forecasts.parquet`: Time-series forecast curve runs from `WINDFOR`.
- `backend/data/bmrs.db`: Embedded SQLite database for relational and audit queries.

---

## 4. Financial Balancing Mechanism (BSC) Cashout Rules

- **Short Position (Forecast > Actual):**
  - Desk has sold more power than delivered.
  - Shortfall volume (MWh) must be bought back at the System Buy Price (SBP) / cashout price.
  - Imbalance Liability (£) = `(Forecast MW - Actual MW) * 0.5 hours * SBP`.
- **Long Position (Forecast < Actual):**
  - Desk has delivered more power than sold.
  - Surplus volume (MWh) is credited at the System Sell Price (SSP).
- **Hedge Value:** Trading with the P10–P90 risk buffer prevents catastrophic balancing cashout losses during rapid wind drop-offs.

---

## 5. Troubleshooting & Health Checks

| Symptom | Diagnostic Step | Resolution |
| :--- | :--- | :--- |
| **API shows Degraded** | Query `GET /api/health` | Verify snapshot files exist in `backend/data/`. Run `python backend/ingest.py`. |
| **Gaps in Forecast** | Check period index in `/api/forecast` | If no forecast was published before cutoff, field is strictly `None` (not 0 MW). This is expected under BMRS rules. |
| **Port Conflict (:8000 / :5173)** | Run `netstat -ano \| findstr 8000` | Terminate dangling process or configure alternative port via `--port`. |
