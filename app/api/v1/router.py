from fastapi import APIRouter, Depends
from app.api.v1.endpoints import doctor, hospital
from sqlalchemy.orm import Session

router = APIRouter()
router.include_router(doctor.router)
router.include_router(hospital.router)