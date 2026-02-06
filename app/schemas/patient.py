# app/schemas/patient.py
from pydantic import BaseModel
from datetime import date

class PatientCreate(BaseModel):
    fname: str
    lname: str
    dob: date
    phone: str

class PatientOut(BaseModel):
    id: int
    fname: str
    lname: str
    dob: date
    phone: str

    class Config:
        orm_mode = True
