import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.app.core.config import settings
from backend.app.api.v1.router import api_router
from backend.app.services.data_loader import data_loader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Environmental Operation System (OES) backend...")
    data_loader.load_data()
    val = data_loader.get_validation_summary()
    logger.info(f"Dataset status: {val.get('total_rows')} rows loaded. Passed: {val.get('validation_passed')}")
    yield
    logger.info("Shutting down backend.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Evidence to Action: Environmental decision-support and CPCB criteria evaluation engine for Bhopal's idol immersion ghats (Bhopal Impact Lab 2026, Track 2).",
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "tagline": settings.TAGLINE,
        "version": settings.VERSION,
        "api_v1_docs": "/docs",
        "health_check": f"{settings.API_V1_STR}/health",
        "ranking_endpoint": f"{settings.API_V1_STR}/ghats/ranking",
        "scope": "7 Standardised Bhopal Ghats (2023–2025 MPPCB Reports)",
        "disclaimer": "Historical MPPCB monitoring data from 2023–2025. This application does not provide live water-quality measurements."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
