from fastapi import APIRouter, Depends
from app.api.v1.endpoints import doctor, hospital, lab, patient
from sqlalchemy.orm import Session

router = APIRouter()
router.include_router(doctor.router)
router.include_router(hospital.router)
router.include_router(lab.router)
router.include_router(patient.router)