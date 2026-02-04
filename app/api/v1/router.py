from fastapi import APIRouter, Depends
from app.api.v1.endpoints import doctor
from sqlalchemy.orm import Session

router = APIRouter()
router.include_router(doctor.router)