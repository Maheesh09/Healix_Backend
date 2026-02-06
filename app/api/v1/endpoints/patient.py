# app/api/v1/endpoints/patient.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.patient import PatientCreate, PatientOut
from app.services.patientService import (
    create_patient as service_create_patient,
    get_patient_by_id,
    list_patients,
    update_patient_service,
    delete_patient_service
)
from app.core.database import get_db

router = APIRouter(prefix="/patients", tags=["Patients"])

# Create
@router.post("/create", response_model=PatientOut)
def create(patient: PatientCreate, db: Session = Depends(get_db)):
    return service_create_patient(db, patient)

# Read single
@router.get("/{patient_id}", response_model=PatientOut)
def read(patient_id: int, db: Session = Depends(get_db)):
    patient = get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

# Read all
@router.get("/", response_model=list[PatientOut])
def read_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return list_patients(db, skip, limit)

# Update
@router.put("/{patient_id}", response_model=PatientOut)
def update(patient_id: int, updates: PatientCreate, db: Session = Depends(get_db)):
    patient = get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return update_patient_service(db, patient, updates)

# Delete
@router.delete("/{patient_id}")
def delete(patient_id: int, db: Session = Depends(get_db)):
    patient = get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return delete_patient_service(db, patient)
