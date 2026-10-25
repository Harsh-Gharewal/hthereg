"""FastAPI Application entry point for Great Britain Wind Forecast Analysis."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routers import accuracy, export, forecast, health
from backend.app.services.data_store import data_store


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan event handler for warm startup caching."""
    if data_store.has_snapshot():
        # Warm caches in memory so the first user query is instant
        data_store.get_actuals()
        data_store.get_forecasts()
        data_store.get_historical_band_map()
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="GB Wind Power Forecast Evaluation Service",
        description=(
            "Decision-time wind power forecast resolution and accuracy evaluation service "
            "for Great Britain settlement periods (Elexon BMRS data)."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Enable CORS for web clients
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers with /api prefix
    app.include_router(health.router, prefix="/api")
    app.include_router(forecast.router, prefix="/api")
    app.include_router(accuracy.router, prefix="/api")
    app.include_router(export.router, prefix="/api")

    return app


app = create_app()
