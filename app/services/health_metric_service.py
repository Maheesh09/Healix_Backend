from sqlalchemy.orm import Session
from app.repo.health_metric_repo import HealthMetricRepo, MetricReferenceRepo
from app.schemas.health_metric import HealthMetricCreate, HealthMetricUpdate, MetricReferenceBase
from app.models.health_metric import HealthMetric, AnatomyCategory, HealthAssessment
from uuid import UUID
from typing import List, Optional
from fastapi import HTTPException, status

class HealthMetricService:
    @staticmethod
    def calculate_assessment(db: Session, metric_name: str, value: float) -> str:
        ref = MetricReferenceRepo.get_by_name(db, metric_name)
        if not ref:
            return HealthAssessment.UNKNOWN
            
        # If no thresholds are defined at all
        if all(t is None for t in [ref.threshold_1, ref.threshold_2, ref.threshold_3, ref.threshold_4]):
            return HealthAssessment.NONE
        
        # 1. Check Lower Critical Range (LEVEL_1)
        if ref.threshold_1 is not None and value < ref.threshold_1:
            return HealthAssessment.LEVEL_1
            
        # 2. Check Upper Critical Range (LEVEL_5)
        if ref.threshold_4 is not None and value > ref.threshold_4:
            return HealthAssessment.LEVEL_5
            
        # 3. Check Optimal Range (LEVEL_3)
        # If both T2 and T3 exist, it's a bounded range.
        if ref.threshold_2 is not None and ref.threshold_3 is not None:
            if ref.threshold_2 <= value <= ref.threshold_3:
                return HealthAssessment.LEVEL_3
        # If only T2 exists (minimum target)
        elif ref.threshold_2 is not None and ref.threshold_3 is None:
            if value >= ref.threshold_2:
                return HealthAssessment.LEVEL_3
        # If only T3 exists (maximum target)
        elif ref.threshold_3 is not None and ref.threshold_2 is None:
            if value <= ref.threshold_3:
                return HealthAssessment.LEVEL_3
                
        # 4. Check Low Range (LEVEL_2)
        # If we reached here and there's a T2, and value is less than it...
        if ref.threshold_2 is not None and value < ref.threshold_2:
            return HealthAssessment.LEVEL_2
            
        # 5. Check High Range (LEVEL_4)
        # If we reached here and there's a T3, and value is greater than it...
        if ref.threshold_3 is not None and value > ref.threshold_3:
            return HealthAssessment.LEVEL_4
            
        # Fallback for metrics with only T1/T4 or partial definitions
        return HealthAssessment.LEVEL_3

    @staticmethod
    def create_metric(db: Session, metric_in: HealthMetricCreate) -> HealthMetric:
        ref = MetricReferenceRepo.get_by_name(db, metric_in.metric_name)
        
        # Start with request data
        metric_data = metric_in.model_dump()
        
        # Auto-detect unit if missing
        if metric_data.get("unit") is None and ref:
            metric_data["unit"] = ref.unit
        elif metric_data.get("unit") is None:
            metric_data["unit"] = "unknown" # Fallback
            
        # Auto-detect category if missing
        if metric_data.get("anatomy_category") is None and ref and ref.anatomy_category:
            metric_data["anatomy_category"] = ref.anatomy_category
        elif metric_data.get("anatomy_category") is None:
            metric_data["anatomy_category"] = AnatomyCategory.GENERAL
            
        # Calculate assessment
        assessment = HealthMetricService.calculate_assessment(db, metric_in.metric_name, metric_in.value)
        
        db_metric = HealthMetric(**metric_data)
        db_metric.health_assessment = assessment
        
        db.add(db_metric)
        db.commit()
        db.refresh(db_metric)
        return db_metric

    @staticmethod
    def get_metric(db: Session, metric_id: UUID) -> HealthMetric:
        db_metric = HealthMetricRepo.get_by_id(db, metric_id)
        if not db_metric:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Health metric not found"
            )
        return db_metric

    @staticmethod
    def get_user_metrics(
        db: Session, 
        user_id: UUID, 
        anatomy_category: Optional[AnatomyCategory] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[HealthMetric]:
        return HealthMetricRepo.get_multi(db, user_id, anatomy_category, skip, limit)

    @staticmethod
    def update_metric(db: Session, metric_id: UUID, metric_in: HealthMetricUpdate) -> HealthMetric:
        db_metric = HealthMetricService.get_metric(db, metric_id)
        
        # Capture current values to see if they change
        new_value = metric_in.value if metric_in.value is not None else db_metric.value
        new_name = metric_in.metric_name if metric_in.metric_name is not None else db_metric.metric_name
        
        # Recalculate assessment
        db_metric.health_assessment = HealthMetricService.calculate_assessment(db, new_name, new_value)
        
        return HealthMetricRepo.update(db, db_metric, metric_in)

    @staticmethod
    def seed_references(db: Session):
        from app.models.health_metric import AnatomyCategory
        refs = [
            # --- FULL 5-TIER CLINICAL (4 Thresholds) ---
            MetricReferenceBase(metric_name="Heart Rate", threshold_1=40.0, threshold_2=60.0, threshold_3=100.0, threshold_4=140.0, unit="bpm", anatomy_category=AnatomyCategory.CHEST),
            MetricReferenceBase(metric_name="Systolic BP", threshold_1=70.0, threshold_2=90.0, threshold_3=120.0, threshold_4=160.0, unit="mmHg", anatomy_category=AnatomyCategory.CHEST),
            MetricReferenceBase(metric_name="Diastolic BP", threshold_1=40.0, threshold_2=60.0, threshold_3=80.0, threshold_4=110.0, unit="mmHg", anatomy_category=AnatomyCategory.CHEST),
            MetricReferenceBase(metric_name="SpO2", threshold_1=80.0, threshold_2=92.0, threshold_3=100.0, threshold_4=None, unit="%", anatomy_category=AnatomyCategory.CHEST),
            MetricReferenceBase(metric_name="Blood Glucose", threshold_1=50.0, threshold_2=70.0, threshold_3=99.0, threshold_4=180.0, unit="mg/dL", anatomy_category=AnatomyCategory.ABDOMEN),
            MetricReferenceBase(metric_name="Body Temp", threshold_1=35.0, threshold_2=36.1, threshold_3=37.2, threshold_4=39.5, unit="C", anatomy_category=AnatomyCategory.GENERAL),
            
            # --- STANDARD 3-TIER (2 Thresholds: T2 & T3) ---
            MetricReferenceBase(metric_name="Vision (L)", threshold_2=0.7, threshold_3=1.5, unit="score", anatomy_category=AnatomyCategory.HEAD),
            MetricReferenceBase(metric_name="Vision (R)", threshold_2=0.7, threshold_3=1.5, unit="score", anatomy_category=AnatomyCategory.HEAD),
            MetricReferenceBase(metric_name="Intraocular Pressure", threshold_2=10.0, threshold_3=21.0, unit="mmHg", anatomy_category=AnatomyCategory.HEAD),
            MetricReferenceBase(metric_name="Hearing Level", threshold_2=0.0, threshold_3=25.0, unit="dB", anatomy_category=AnatomyCategory.HEAD),
            MetricReferenceBase(metric_name="ALT", threshold_2=7.0, threshold_3=55.0, unit="U/L", anatomy_category=AnatomyCategory.ABDOMEN),
            MetricReferenceBase(metric_name="AST", threshold_2=8.0, threshold_3=48.0, unit="U/L", anatomy_category=AnatomyCategory.ABDOMEN),
            MetricReferenceBase(metric_name="Bilirubin", threshold_2=0.1, threshold_3=1.2, unit="mg/dL", anatomy_category=AnatomyCategory.ABDOMEN),
            MetricReferenceBase(metric_name="BMI", threshold_2=18.5, threshold_3=24.9, unit="kg/m2", anatomy_category=AnatomyCategory.GENERAL),
            MetricReferenceBase(metric_name="Sleep Hours", threshold_2=7.0, threshold_3=9.0, unit="hours", anatomy_category=AnatomyCategory.GENERAL),
            MetricReferenceBase(metric_name="Grip Strength", threshold_2=30.0, threshold_3=60.0, unit="kg", anatomy_category=AnatomyCategory.LIMBS),
            MetricReferenceBase(metric_name="Respiratory Rate", threshold_2=12.0, threshold_3=20.0, unit="breaths/min", anatomy_category=AnatomyCategory.CHEST),

            # --- TRACKING ONLY (0 Thresholds) ---
            MetricReferenceBase(metric_name="Step Count", unit="steps", anatomy_category=AnatomyCategory.GENERAL),
            MetricReferenceBase(metric_name="Calories Burned", unit="kcal", anatomy_category=AnatomyCategory.GENERAL),
            MetricReferenceBase(metric_name="Weight", unit="kg", anatomy_category=AnatomyCategory.GENERAL),
            MetricReferenceBase(metric_name="Height", unit="cm", anatomy_category=AnatomyCategory.GENERAL),
            MetricReferenceBase(metric_name="Waist Circumference", unit="cm", anatomy_category=AnatomyCategory.ABDOMEN),
            MetricReferenceBase(metric_name="Calf Circumference", unit="cm", anatomy_category=AnatomyCategory.LIMBS),
            MetricReferenceBase(metric_name="Arm Circumference", unit="cm", anatomy_category=AnatomyCategory.LIMBS),
            MetricReferenceBase(metric_name="Hand Strength", unit="kg", anatomy_category=AnatomyCategory.LIMBS),
            MetricReferenceBase(metric_name="Reaction Time", unit="sec", anatomy_category=AnatomyCategory.HEAD),
            MetricReferenceBase(metric_name="Peak Flow", unit="L/min", anatomy_category=AnatomyCategory.CHEST),
            MetricReferenceBase(metric_name="Knee Reflex", unit="scale", anatomy_category=AnatomyCategory.LIMBS),
        ]
        for ref in refs:
            MetricReferenceRepo.create_or_update(db, ref)

    @staticmethod
    def delete_metric(db: Session, metric_id: UUID) -> None:
        success = HealthMetricRepo.delete(db, metric_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Health metric not found"
            )
