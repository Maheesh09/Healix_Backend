# app/services/patientService.py
from sqlalchemy.orm import Session
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientOut
from app.repo.patientRepo import (
    create_patient as repo_create_patient,
    get_patient as repo_get_patient,
    get_patients as repo_get_patients,
    update_patient as repo_update_patient,
    delete_patient as repo_delete_patient
)

def create_patient(db: Session, patient: PatientCreate) -> PatientOut:
    db_patient = Patient(
        fname=patient.fname,
        lname=patient.lname,
        dob=patient.dob,
        phone=patient.phone
    )
    return repo_create_patient(db, db_patient)

def get_patient_by_id(db: Session, patient_id: int) -> PatientOut | None:
    return repo_get_patient(db, patient_id)

def list_patients(db: Session, skip: int = 0, limit: int = 100):
    return repo_get_patients(db, skip, limit)

def update_patient_service(db: Session, patient: Patient, updates: PatientCreate) -> PatientOut:
    updates_dict = updates.dict(exclude_unset=True)
    return repo_update_patient(db, patient, updates_dict)

def delete_patient_service(db: Session, patient: Patient):
    return repo_delete_patient(db, patient)
