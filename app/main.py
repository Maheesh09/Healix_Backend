
from fastapi import FastAPI
from app.api.v1 import health_metrics, report_extracted_data, users
from app.core.database import engine
# from app.db.base_class import Base
from app.api.v1.endpoints import doctor, hospital, lab, patient

# Create tables
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Healix Backend API")

app.include_router(users.router)
app.include_router(doctor.router)
app.include_router(hospital.router)
app.include_router(lab.router)
app.include_router(patient.router)
app.include_router(health_metrics.router)
app.include_router(report_extracted_data.router)

@app.get("/")
def health_check():
    return {"status": "Healix backend running"}
