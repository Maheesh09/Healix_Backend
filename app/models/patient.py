# app/models/patient.py
from app.core.database import Base
from sqlalchemy import Column, Integer, String, Date

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    fname = Column(String, nullable=False)
    lname = Column(String, nullable=False)
    dob = Column(Date, nullable=False)
    phone = Column(String, nullable=False, unique=True)
