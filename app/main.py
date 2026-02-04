from fastapi import FastAPI
from app.api.v1 import health_metrics
from app.core.database import engine, Base, SessionLocal
from app.services.health_metric_service import HealthMetricService

# Create tables and seed data if they don't exist
Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    HealthMetricService.seed_references(db)

app = FastAPI(title="Healix Backend API")

app.include_router(health_metrics.router, prefix="/api/v1")

@app.get("/")
def health_check():
    return {"status": "Healix backend running"}
