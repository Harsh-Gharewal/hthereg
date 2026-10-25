# GB Wind Power Forecast Evaluation Desk

An enterprise-grade forecasting and decision-time accuracy platform engineered for Great Britain wholesale day-ahead power trading desks.

Powered by official **Elexon BMRS** data (`WINDFOR` and `FUELHH`), this platform evaluates national wind generation forecasts at decision time (D-1 09:00 UK cutoff), quantifies forecast error across all 744 settlement periods of January 2026, models balancing mechanism cashflow exposure, and provides a modern SaaS web interface.

---

## 🌟 Key Features

1. **Strict Decision-Time Resolution**: Resolves point-in-time forecasts published at or before the configured D-1 cutoff time. Gaps remain unpolluted by future knowledge.
2. **Comprehensive Accuracy Metrics Engine**:
   - Mean Absolute Error (**MAE**: 2,022 MW)
   - Mean Directional Bias (**+1,746 MW** systematic over-forecasting)
   - Root Mean Square Error (**RMSE**: 2,497 MW)
   - Normalized MAE (**nMAE**: 17.92%)
   - Tail Risk Percentiles (**P10**: -426 MW, **P90**: +4,154 MW)
3. **Balancing Mechanism Financial Modeling**: Translates forecast deviations into £ (GBP) imbalance exposure based on Elexon cashout settlement rules.
4. **Bonsai SaaS Frontend**: Clean, high-contrast light-mode interface built with React, Vite, Recharts, and Google Fonts (`Plus Jakarta Sans` + `JetBrains Mono`).
5. **Trader CLI & Scheduler**: Terminal tools for fast backtesting and automated gate-closure evaluation routines.
6. **Docker Production Deployment**: Multi-stage container builds orchestrated via `docker-compose`.

---

## 🏗️ System Architecture

```
d:\REint\
├── backend/
│   ├── app/
│   │   ├── config.py             # Timezone, settlement periods, and paths
│   │   ├── dependencies.py       # FastAPI dependency injection
│   │   ├── main.py               # FastAPI app factory, CORS, and warm lifespan
│   │   ├── schemas/              # Pydantic models (domain, API, metrics, cashflow)
│   │   ├── services/
│   │   │   ├── data_store.py     # High-performance Parquet & SQLite singleton
│   │   │   ├── resolver.py       # D-1 09:00 decision-time point-in-time resolver
│   │   │   ├── metrics.py        # Statistical error metrics engine
│   │   │   └── cashflow.py       # Imbalance cashflow & risk modeling
│   │   └── routers/              # REST API endpoints (/api/forecast, /api/accuracy, /api/cashflow, /api/export)
│   ├── cli.py                    # Trader command-line interface
│   ├── scheduler.py              # Automated background scheduler
│   ├── ingest.py                 # Elexon BMRS REST API ingestion pipeline
│   ├── Dockerfile                # Production Python 3.12 container
│   └── tests/                    # 31 unit, integration, and E2E tests (pytest)
├── frontend/
│   ├── src/
│   │   ├── components/           # Bonsai UI (Header, NavTabs, Controls, Recharts)
│   │   ├── views/                # 5 interactive views (Forecast, Summary, Horizon, Hour, Distribution)
│   │   ├── styles/               # CSS Modules & Bonsai light design tokens
│   │   └── api/client.js         # Typed fetch client
│   ├── nginx.conf                # Production reverse proxy and static cache
│   └── Dockerfile                # Multi-stage Vite build + Nginx Alpine
├── docker-compose.yml            # 1-command container orchestration
└── docs/RUNBOOK.md               # Trading desk operational procedures
```

---

## 🚀 Quick Start (Local Development)

### 1. Prerequisites
- **Python 3.12+**
- **Node.js 20+**

### 2. Backend Setup
```bash
# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Run all 31 tests
pytest backend/tests -v

# Start FastAPI server (docs at http://localhost:8000/docs)
uvicorn backend.app.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
# Dashboard launches at http://localhost:5173/
```

---

## 💻 Trader CLI Usage

Energy traders can run evaluations and backtests directly from the terminal:

```bash
# Evaluate a single delivery day (D-1 09:00 cutoff)
python -m backend.cli evaluate --date 2026-02-01 --cutoff 09:00

# Run multi-day backtest across January 2026
python -m backend.cli backtest --from 2026-01-02 --to 2026-02-01 --cutoff 09:00

# Export evaluated data directly to CSV
python -m backend.cli export --from 2026-01-02 --to 2026-02-01 --cutoff 09:00 --out january_wind.csv
```

---

## 🐳 Docker Production Deployment

Launch the complete full-stack platform with a single command:

```bash
docker compose up --build
```

- **Frontend Application:** `http://localhost`
- **Backend API & Swagger:** `http://localhost:8000/docs`

---

## 🧪 Testing Verification

The project includes 31 comprehensive tests covering data storage, domain resolution rules, accuracy formulas, financial cashflows, and end-to-end API workflows:

```bash
.venv\Scripts\pytest backend/tests -v
```

```
======================= 31 passed, 1 warning in 13.06s ========================
```
