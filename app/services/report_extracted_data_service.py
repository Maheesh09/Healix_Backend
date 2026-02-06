from sqlalchemy.orm import Session
from app.repo.report_extracted_data_repo import ReportExtractedDataRepo
from app.schemas.report_extracted_data import ReportExtractedDataCreate, ReportExtractedDataUpdate
from app.models.report_extracted_data import ReportExtractedData
from uuid import UUID
from typing import List, Optional
from fastapi import HTTPException, status

class ReportExtractedDataService:
    @staticmethod
    def create_report_data(db: Session, report_in: ReportExtractedDataCreate) -> ReportExtractedData:
        return ReportExtractedDataRepo.create(db, report_in)

    @staticmethod
    def get_report_data(db: Session, report_id: UUID) -> ReportExtractedData:
        db_report = ReportExtractedDataRepo.get_by_id(db, report_id)
        if not db_report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report extracted data not found"
            )
        return db_report

    @staticmethod
    def get_user_report_data(
        db: Session, 
        uhid: UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ReportExtractedData]:
        return ReportExtractedDataRepo.get_multi(db, uhid, skip, limit)

    @staticmethod
    def update_report_data(
        db: Session, 
        report_id: UUID, 
        report_in: ReportExtractedDataUpdate
    ) -> ReportExtractedData:
        db_report = ReportExtractedDataService.get_report_data(db, report_id)
        return ReportExtractedDataRepo.update(db, db_report, report_in)

    @staticmethod
    def delete_report_data(db: Session, report_id: UUID) -> None:
        success = ReportExtractedDataRepo.delete(db, report_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report extracted data not found"
            )
