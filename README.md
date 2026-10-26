# 🌬️ WindWise

> **Enterprise-grade forecasting and decision-time accuracy platform for Great Britain wholesale day-ahead power trading desks.**

WindWise is a full-stack financial-grade forecasting and decision-support platform that evaluates **GB national wind generation forecasts at actual trading decision time**.

Powered by official **Elexon BMRS** data (`WINDFOR` and `FUELHH`), WindWise resolves point-in-time forecasts at the **D-1 09:00 UK cutoff**, compares them against actual metered generation, quantifies forecast error across all **744 settlement periods of January 2026**, models **Balancing Mechanism cashflow exposure**, and presents the results through a modern trader-focused SaaS interface.

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Technology Stack](#️-technology-stack)
- [System Architecture](#️-system-architecture)
- [Project Structure](#-project-structure)
- [How WindWise Works](#-how-windwise-works)
- [Dashboard](#-dashboard)
- [January 2026 Results](#-january-2026-results)
- [Quick Start](#-quick-start)
- [Backend Setup](#-backend-setup)
- [Frontend Setup](#-frontend-setup)
- [Run the Complete Application](#-run-the-complete-application)
- [Trader CLI](#-trader-cli)
- [Docker Deployment](#-docker-deployment)
- [Testing](#-testing)
- [API](#-api)
- [AI Tool Disclosure](#-ai-tool-disclosure)
- [Development Workflow](#-development-workflow)
- [Important Files](#-important-files)
- [Quick Command Reference](#-quick-command-reference)

---

# 📖 Overview

WindWise is designed around a critical requirement in energy trading analytics:

> **Only information available at the actual trading decision time should be used when evaluating a forecast.**

The platform uses official **Elexon BMRS** data from:

- `WINDFOR` — Wind generation forecasts
- `FUELHH` — Actual half-hourly generation data

WindWise resolves the correct forecast available at or before the configured **D-1 09:00 UK cutoff**, compares it with actual generation, calculates statistical accuracy metrics, and translates forecast deviations into potential financial exposure.

The platform provides three major capabilities:

```text
┌──────────────────────────────────────────────────────────────┐
│                         WINDWISE                             │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Forecast Resolution                                         │
│          ↓                                                   │
│  Forecast Accuracy                                           │
│          ↓                                                   │
│  Financial Exposure                                          │
│          ↓                                                   │
│  Trader Dashboard + CLI + Scheduler                          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

# 🌟 Key Features

## 1. ⏱️ Strict Decision-Time Resolution

WindWise resolves point-in-time forecasts published **at or before the configured D-1 cutoff time**.

This prevents **future knowledge contamination** and ensures that forecast evaluation reflects the information that would genuinely have been available to a trader at decision time.

---

## 2. 📊 Comprehensive Accuracy Metrics Engine

WindWise calculates multiple forecast performance metrics:

| Metric | Result |
|---|---:|
| **Mean Absolute Error (MAE)** | **2,022 MW** |
| **Mean Directional Bias** | **+1,746 MW** |
| **Root Mean Square Error (RMSE)** | **2,497 MW** |
| **Normalized MAE (nMAE)** | **17.92%** |
| **P10** | **-426 MW** |
| **P90** | **+4,154 MW** |

The platform also provides distribution, horizon, and hour-based analysis.

---

## 3. 💷 Balancing Mechanism Financial Modeling

WindWise translates forecast deviations into potential **GBP (£) imbalance exposure** based on Elexon cashout settlement rules.

This allows users to move beyond statistical forecast accuracy and understand the potential **financial impact of forecast error**.

```text
Forecast
    ↓
Actual Generation
    ↓
Forecast Deviation
    ↓
Cashout / Settlement Rules
    ↓
GBP Exposure
```

---

## 4. 🎨 WindWise SaaS Frontend

A clean, high-contrast light-mode interface built with:

- React
- Vite
- Recharts
- Google Fonts
  - Plus Jakarta Sans
  - JetBrains Mono

The dashboard provides multiple interactive views for analyzing forecast performance.

---

## 5. 🖥️ Trader CLI & Scheduler

WindWise includes terminal tools for:

- Single-day evaluation
- Multi-day backtesting
- CSV exports
- Automated gate-closure evaluation routines

---

## 6. 🐳 Docker Production Deployment

The complete platform can be launched using a single Docker Compose command.

The production setup includes:

- FastAPI backend
- React/Vite frontend
- Nginx reverse proxy
- Multi-stage Docker builds
- Docker Compose orchestration

---

# 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | React |
| **Build Tool** | Vite |
| **Charts** | Recharts |
| **Backend** | FastAPI |
| **Language** | Python 3.12+ |
| **Validation** | Pydantic |
| **Data Storage** | Parquet + SQLite |
| **Data Source** | Elexon BMRS |
| **Testing** | Pytest |
| **Web Server** | Nginx |
| **Containerization** | Docker |
| **Orchestration** | Docker Compose |
| **Fonts** | Plus Jakarta Sans + JetBrains Mono |

---

# 🏗️ System Architecture

```text
                         ┌───────────────────────┐
                         │      Elexon BMRS      │
                         │                       │
                         │  WINDFOR    FUELHH    │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │    Data Ingestion     │
                         │       ingest.py       │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │       Data Store      │
                         │    Parquet + SQLite   │
                         │      data_store.py    │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │ Decision-Time Resolver│
                         │      resolver.py      │
                         │                       │
                         │      D-1 09:00        │
                         └───────────┬───────────┘
                                     │
                   ┌─────────────────┴─────────────────┐
                   │                                   │
                   ▼                                   ▼
       ┌───────────────────────┐           ┌───────────────────────┐
       │   Accuracy Metrics    │           │   Cashflow / Risk     │
       │        Engine         │           │        Engine         │
       │                       │           │                       │
       │ MAE / RMSE / Bias     │           │ Imbalance Exposure    │
       │ nMAE / Percentiles    │           │ GBP Cashflow Model    │
       └───────────┬───────────┘           └───────────┬───────────┘
                   │                                   │
                   └─────────────────┬─────────────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │       FastAPI API     │
                         │                       │
                         │ /api/forecast         │
                         │ /api/accuracy         │
                         │ /api/cashflow         │
                         │ /api/export           │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │     React Frontend    │
                         │                       │
                         │ Forecast              │
                         │ Summary               │
                         │ Horizon               │
                         │ Hour                  │
                         │ Distribution          │
                         └───────────────────────┘
```

---

# 📁 Project Structure

The project is organized into separate **backend, frontend, deployment, testing, and documentation** layers.

```text
d:\REint\
│
├── 📁 backend/
│   │
│   ├── 📁 app/
│   │   │
│   │   ├── 📄 config.py
│   │   │   └── Timezone, settlement periods, and paths
│   │   │
│   │   ├── 📄 dependencies.py
│   │   │   └── FastAPI dependency injection
│   │   │
│   │   ├── 📄 main.py
│   │   │   └── FastAPI app factory, CORS, and warm lifespan
│   │   │
│   │   ├── 📁 schemas/
│   │   │   └── Pydantic models
│   │   │       ├── Domain models
│   │   │       ├── API models
│   │   │       ├── Metrics
│   │   │       └── Cashflow
│   │   │
│   │   ├── 📁 services/
│   │   │   │
│   │   │   ├── 📄 data_store.py
│   │   │   │   └── High-performance Parquet & SQLite singleton
│   │   │   │
│   │   │   ├── 📄 resolver.py
│   │   │   │   └── D-1 09:00 decision-time point-in-time resolver
│   │   │   │
│   │   │   ├── 📄 metrics.py
│   │   │   │   └── Statistical error metrics engine
│   │   │   │
│   │   │   └── 📄 cashflow.py
│   │   │       └── Imbalance cashflow & risk modeling
│   │   │
│   │   └── 📁 routers/
│   │       └── REST API endpoints
│   │           ├── /api/forecast
│   │           ├── /api/accuracy
│   │           ├── /api/cashflow
│   │           └── /api/export
│   │
│   ├── 📄 cli.py
│   │   └── Trader command-line interface
│   │
│   ├── 📄 scheduler.py
│   │   └── Automated background scheduler
│   │
│   ├── 📄 ingest.py
│   │   └── Elexon BMRS REST API ingestion pipeline
│   │
│   ├── 📄 Dockerfile
│   │   └── Production Python 3.12 container
│   │
│   └── 📁 tests/
│       └── 31 unit, integration, and E2E tests
│
├── 📁 frontend/
│   │
│   ├── 📁 src/
│   │   │
│   │   ├── 📁 components/
│   │   │   └── WindWise UI
│   │   │       ├── Header
│   │   │       ├── NavTabs
│   │   │       ├── Controls
│   │   │       └── Recharts
│   │   │
│   │   ├── 📁 views/
│   │   │   └── 5 interactive views
│   │   │       ├── Forecast
│   │   │       ├── Summary
│   │   │       ├── Horizon
│   │   │       ├── Hour
│   │   │       └── Distribution
│   │   │
│   │   ├── 📁 styles/
│   │   │   └── CSS Modules & WindWise design tokens
│   │   │
│   │   └── 📁 api/
│   │       └── 📄 client.js
│   │           └── Typed fetch client
│   │
│   ├── 📄 nginx.conf
│   │   └── Production reverse proxy and static cache
│   │
│   └── 📄 Dockerfile
│       └── Multi-stage Vite build + Nginx Alpine
│
├── 📄 docker-compose.yml
│   └── 1-command container orchestration
│
└── 📁 docs/
    └── 📄 RUNBOOK.md
        └── Trading desk operational procedures
```

---

# 🔄 How WindWise Works

WindWise follows a strict evaluation pipeline.

```text
              Elexon BMRS
                   │
          ┌────────┴────────┐
          │                 │
          ▼                 ▼
       WINDFOR            FUELHH
          │                 │
          │                 │
          ▼                 ▼
      Forecast            Actual
          │                 │
          └────────┬────────┘
                   │
                   ▼
          Decision-Time Resolver
                   │
             D-1 09:00 UK
                   │
                   ▼
          Forecast vs Actual
                   │
           ┌───────┴───────┐
           │               │
           ▼               ▼
      Accuracy         Cashflow
       Metrics          Modeling
           │               │
           └───────┬───────┘
                   │
                   ▼
             FastAPI API
                   │
                   ▼
            WindWise UI
```

---

# 📊 Dashboard

WindWise provides five interactive dashboard views.

| View | Purpose |
|---|---|
| **Forecast** | Explore wind forecasts and actual generation |
| **Summary** | View overall forecast accuracy |
| **Horizon** | Analyze performance across forecast horizons |
| **Hour** | Analyze forecast behavior by hour |
| **Distribution** | Examine forecast error distribution and tail behavior |

The frontend is designed as a modern, high-contrast light-mode SaaS interface using **Plus Jakarta Sans** and **JetBrains Mono**.

---

# 📈 January 2026 Results

WindWise evaluates **all 744 settlement periods of January 2026**.

## Core Metrics

| Metric | Value |
|---|---:|
| **MAE** | **2,022 MW** |
| **Mean Directional Bias** | **+1,746 MW** |
| **RMSE** | **2,497 MW** |
| **nMAE** | **17.92%** |
| **P10** | **-426 MW** |
| **P90** | **+4,154 MW** |

### Forecast Bias

The results indicate a systematic **positive directional bias**, with the forecast overestimating generation on average.

The P10/P90 range provides visibility into the distribution of forecast deviations and tail behavior.

---

# 💷 Balancing Mechanism Cashflow

WindWise converts forecast deviations into potential **£ GBP imbalance exposure**.

```text
Forecast
   │
   ▼
Actual Generation
   │
   ▼
Forecast Deviation
   │
   ▼
Elexon Cashout / Settlement Rules
   │
   ▼
GBP Exposure
```

This connects:

**Forecast Accuracy → Physical Deviation → Financial Risk**

---

# 🚀 Quick Start

## Prerequisites

Before running WindWise locally, install:

- **Python 3.12+**
- **Node.js 20+**
- **Git**
- **Docker Desktop** *(optional — only required for Docker deployment)*

---

# 🐍 Backend Setup

Open a terminal in the project root:

```bash
cd d:\REint
```

## 1. Create a Virtual Environment

```bash
python -m venv .venv
```

## 2. Activate the Virtual Environment

On Windows:

```bash
.venv\Scripts\activate
```

You should see:

```text
(.venv) d:\REint>
```

## 3. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

---

# 🧪 Testing

Before starting the application, verify that the backend is working correctly:

```bash
pytest backend/tests -v
```

Expected result:

```text
======================= 31 passed, 1 warning in 13.06s ========================
```

The test suite covers:

- Data storage
- Domain resolution rules
- Accuracy formulas
- Financial cashflows
- End-to-end API workflows

---

# ⚡ Start the Backend

Run:

```bash
uvicorn backend.app.main:app --reload --port 8000
```

The backend will be available at:

```text
http://localhost:8000
```

## 📚 FastAPI Swagger Documentation

Open:

```text
http://localhost:8000/docs
```

This provides an interactive interface for exploring and testing the API.

---

# 🎨 Frontend Setup

Open a **second terminal**.

Navigate to the frontend:

```bash
cd d:\REint\frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The dashboard will be available at:

```text
http://localhost:5173/
```

---

# 🖥️ Run the Complete Application

During normal local development, use **two terminals**.

## Terminal 1 — Backend

```bash
cd d:\REint

.venv\Scripts\activate

uvicorn backend.app.main:app --reload --port 8000
```

## Terminal 2 — Frontend

```bash
cd d:\REint\frontend

npm install
npm run dev
```

Then open:

### 🌬️ WindWise Dashboard

```text
http://localhost:5173/
```

### 📚 API Documentation

```text
http://localhost:8000/docs
```

---

# 🖥️ Trader CLI

WindWise provides command-line tools for traders and analysts.

## Evaluate a Single Delivery Day

Evaluate a single delivery day using the D-1 09:00 cutoff:

```bash
python -m backend.cli evaluate --date 2026-02-01 --cutoff 09:00
```

---

## Run a Multi-Day Backtest

Run a backtest across January 2026:

```bash
python -m backend.cli backtest --from 2026-01-02 --to 2026-02-01 --cutoff 09:00
```

---

## Export Evaluated Data

Export evaluated data directly to CSV:

```bash
python -m backend.cli export --from 2026-01-02 --to 2026-02-01 --cutoff 09:00 --out january_wind.csv
```

---

# 🐳 Docker Deployment

WindWise can be launched as a complete production-style stack using Docker Compose.

## Start the Application

From the project root:

```bash
docker compose up --build
```

Docker will build and start the complete application.

### 🌐 Frontend

```text
http://localhost
```

### ⚡ Backend API

```text
http://localhost:8000
```

### 📚 Swagger API

```text
http://localhost:8000/docs
```

---

# 🔌 API

The FastAPI backend exposes REST endpoints for:

```text
/api/forecast
/api/accuracy
/api/cashflow
/api/export
```

Interactive API documentation is available at:

```text
http://localhost:8000/docs
```

---

# 🧩 Backend Architecture

The backend is built using **Python + FastAPI**.

## Core Services

| File | Responsibility |
|---|---|
| `data_store.py` | High-performance Parquet & SQLite data access |
| `resolver.py` | Point-in-time D-1 09:00 forecast resolution |
| `metrics.py` | Forecast accuracy calculations |
| `cashflow.py` | Imbalance cashflow and risk modeling |
| `ingest.py` | Elexon BMRS data ingestion |
| `cli.py` | Trader command-line operations |
| `scheduler.py` | Automated evaluation scheduling |

---

# 🎨 Frontend Architecture

The frontend uses:

- **React**
- **Vite**
- **Recharts**
- **CSS Modules**
- **Google Fonts**

## Design System

WindWise uses:

- High-contrast light mode
- Modern SaaS layout
- **Plus Jakarta Sans**
- **JetBrains Mono**
- Interactive charts
- Trader-focused information hierarchy

---

# 🧪 Test Coverage

The project includes **31 comprehensive tests** covering:

- Data storage
- Domain resolution rules
- Accuracy formulas
- Financial cashflows
- End-to-end API workflows

Run the complete test suite:

```bash
pytest backend/tests -v
```

Expected:

```text
======================= 31 passed, 1 warning in 13.06s ========================
```

---

# 🤖 AI Tool Disclosure

In accordance with the assignment requirements, the following AI tools were utilized during development.

## Google Stitch

Used at design-time to:

- Conceptualize UI layouts
- Extract modern SaaS design tokens
- Generate reference screen mockups

Design references are stored under:

```text
design/
├── prompts/
└── stitch/
```

## AI Coding Assistant

Used for:

- Pair-programming
- Writing test fixtures
- Accelerating boilerplate scaffolding across FastAPI and React

All architecture, domain resolver logic, Elexon BMRS ingestion, and financial metrics were strictly verified against official Elexon BSC specifications.

---

# 🔄 Development Workflow

For a new developer working on WindWise:

```text
1. Open the repository
        ↓
2. Create Python virtual environment
        ↓
3. Activate environment
        ↓
4. Install backend dependencies
        ↓
5. Run backend tests
        ↓
6. Start FastAPI
        ↓
7. Open a second terminal
        ↓
8. Install frontend dependencies
        ↓
9. Start React/Vite
        ↓
10. Open the WindWise dashboard
        ↓
11. Make changes
        ↓
12. Run tests again
```

---

# 📂 Important Files

If you're new to WindWise, these are the most important files to understand first.

## Backend

```text
backend/
│
├── ingest.py
│   └── Where BMRS data enters the system
│
├── cli.py
│   └── Trader-facing CLI
│
├── scheduler.py
│   └── Automated evaluation
│
└── app/
    │
    ├── main.py
    │   └── FastAPI application
    │
    └── services/
        │
        ├── resolver.py
        │   └── Decision-time logic
        │
        ├── metrics.py
        │   └── Forecast accuracy
        │
        ├── cashflow.py
        │   └── Financial modeling
        │
        └── data_store.py
            └── Data access
```

## Frontend

```text
frontend/
│
└── src/
    │
    ├── components/
    │   └── Reusable UI components
    │
    ├── views/
    │   └── Dashboard screens
    │
    ├── styles/
    │   └── Design system / CSS
    │
    └── api/
        └── client.js
            └── Backend API communication
```

## Deployment

```text
Dockerfile
docker-compose.yml
nginx.conf
```

These files control how WindWise is packaged and deployed.

---

# 🗺️ Where Should You Start?

If you're exploring the codebase for the first time, follow this order:

### 1️⃣ Understand the data

Start with:

```text
backend/ingest.py
```

Understand how Elexon BMRS data enters WindWise.

### 2️⃣ Understand decision-time resolution

Then inspect:

```text
backend/app/services/resolver.py
```

This is one of the most important domain components because it determines which forecast was actually available at the D-1 09:00 cutoff.

### 3️⃣ Understand accuracy calculations

Next:

```text
backend/app/services/metrics.py
```

This contains the statistical evaluation logic.

### 4️⃣ Understand financial modeling

Then:

```text
backend/app/services/cashflow.py
```

This connects forecast deviations to potential financial exposure.

### 5️⃣ Understand the API

Then explore:

```text
backend/app/routers/
backend/app/main.py
```

### 6️⃣ Understand the UI

Finally explore:

```text
frontend/src/components/
frontend/src/views/
frontend/src/api/
```

This gives you a logical path from:

**Data → Domain Logic → Metrics → Financial Model → API → Dashboard**

---

# 📋 Quick Command Reference

| Task | Command |
|---|---|
| Create virtual environment | `python -m venv .venv` |
| Activate environment | `.venv\Scripts\activate` |
| Install backend | `pip install -r backend/requirements.txt` |
| Run tests | `pytest backend/tests -v` |
| Start backend | `uvicorn backend.app.main:app --reload --port 8000` |
| Enter frontend | `cd frontend` |
| Install frontend | `npm install` |
| Start frontend | `npm run dev` |
| Start Docker | `docker compose up --build` |

---

# 🌐 Local URLs

Once WindWise is running:

| Service | URL |
|---|---|
| 🌬️ **WindWise Dashboard** | `http://localhost:5173/` |
| 🚀 **Production Dashboard** | `http://localhost` |
| ⚡ **FastAPI** | `http://localhost:8000` |
| 📚 **Swagger API Docs** | `http://localhost:8000/docs` |

---

# 📚 Documentation

Operational procedures for the trading desk are available in:

```text
docs/RUNBOOK.md
```

---

# 🏁 Project Summary

**WindWise** combines:

```text
Official Elexon BMRS Data
          ↓
Point-in-Time Decision Resolution
          ↓
Forecast Accuracy Analytics
          ↓
Balancing Mechanism Cashflow Modeling
          ↓
Trader-Focused SaaS Dashboard
          ↓
CLI + Automated Scheduling
          ↓
Docker Production Deployment
```

WindWise provides a complete workflow for evaluating **GB national wind power forecasts from a trading decision-time perspective**, connecting forecast performance directly to operational and financial risk.

---

# ⭐ Project Highlights

- ⏱️ Point-in-time D-1 09:00 forecast resolution
- 🌬️ Elexon BMRS `WINDFOR` + `FUELHH`
- 📊 MAE / RMSE / Bias / nMAE / percentile analysis
- 💷 Balancing Mechanism cashflow exposure modeling
- 📈 Interactive React + Recharts dashboard
- 🖥️ Trader CLI
- ⏰ Automated scheduler
- 🧪 31 automated tests
- 🐳 Docker production deployment
- 🚀 FastAPI backend
- 🎨 WindWise SaaS interface
- 📚 Operational runbook

---

## 🌬️ WindWise

**Forecast smarter. Evaluate precisely. Trade with better information.**