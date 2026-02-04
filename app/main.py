from fastapi import FastAPI

from app.api.v1.endpoints import doctor, hospital, lab

app = FastAPI(title="Healix Backend API")

app.include_router(doctor.router)
app.include_router(hospital.router)
app.include_router(lab.router)