
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.v1.endpoints import reports as ocr
from app.api.v1.endpoints import patient
from app.api.v1.endpoints import care_circle
from app.api.v1.endpoints import medication
from app.api.v1.endpoints import trends
from app.api.v1.endpoints import health_metrics
from app.core.database import engine, Base

# Import all models so Base.metadata knows about them
from app.models.health_metric import HealthMetric, MetricReference  # noqa: F401

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables that don't exist yet (safe – won't drop existing ones)
    Base.metadata.create_all(bind=engine)

    # Seed metric reference ranges (idempotent)
    from app.core.database import SessionLocal
    from app.services.health_metric_service import HealthMetricService
    db = SessionLocal()
    try:
        HealthMetricService.seed_references(db)
    except Exception as e:
        print(f"[startup] Warning – could not seed metric references: {e}")
    finally:
        db.close()

    yield  # application runs

app = FastAPI(
    title="Healix Backend API",
    description="AI-powered medical record system",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ocr.router, prefix="/api/v1/ocr", tags=["OCR"])
app.include_router(patient.router, prefix="/api/v1", tags=["Patients"])
app.include_router(care_circle.router, prefix="/api/v1", tags=["Care Circle"])
app.include_router(medication.router, prefix="/api/v1", tags=["Medications"])
app.include_router(trends.router, prefix="/api/v1", tags=["Trends"])
app.include_router(health_metrics.router, prefix="/api/v1", tags=["Health Metrics"])


