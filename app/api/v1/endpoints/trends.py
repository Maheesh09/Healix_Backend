from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.health_metric import HealthMetric
from app.schemas.trend import BiomarkerTrend, BiomarkerDataPoint

# Mapping from health_metrics metric_name to the standardized biomarker names
# so both sources can be combined under the same trend
HEALTH_METRIC_TO_BIOMARKER = {
    "Blood Glucose": "Fasting Plasma Glucose",
    "Fasting Plasma Glucose": "Fasting Plasma Glucose",
    "Total Cholesterol": "Total Cholesterol",
    "Systolic BP": "Systolic BP",
    "Diastolic BP": "Diastolic BP",
}

router = APIRouter(prefix="/trends", tags=["Trends"])

@router.get("/names", response_model=List[str])
def get_biomarker_names(
    patient_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get list of available biomarker names for a patient based on manually entered health metrics.
    """
    hm_results = (
        db.query(HealthMetric.metric_name)
        .filter(HealthMetric.user_id == patient_id)
        .distinct()
        .all()
    )

    names = set(r[0] for r in hm_results)
    return sorted(list(names))

@router.get("/data", response_model=BiomarkerTrend)
def get_biomarker_data(
    patient_id: UUID,
    name: str,
    db: Session = Depends(get_db)
):
    """
    Get trend data for a specific biomarker based solely on manually entered health metrics.
    Supports alias mapping so frontend queries like "Fasting Plasma Glucose" also match
    entries like "Blood Glucose".
    """
    data_points: List[BiomarkerDataPoint] = []
    last_unit = None

    # Match by exact metric_name, or by known aliases
    metric_names_to_query = [name]
    for hm_name, bio_name in HEALTH_METRIC_TO_BIOMARKER.items():
        if bio_name == name and hm_name not in metric_names_to_query:
            metric_names_to_query.append(hm_name)
        if hm_name == name and bio_name not in metric_names_to_query:
            metric_names_to_query.append(bio_name)

    hm_results = (
        db.query(HealthMetric)
        .filter(
            HealthMetric.user_id == patient_id,
            HealthMetric.metric_name.in_(metric_names_to_query)
        )
        .order_by(desc(HealthMetric.recorded_at))
        .all()
    )

    for hm in hm_results:
        date_val = hm.recorded_at or hm.created_at
        data_points.append(BiomarkerDataPoint(
            date=date_val,
            value=hm.value,
            unit=hm.unit,
            flag=hm.flag
        ))
        if last_unit is None and hm.unit:
            last_unit = hm.unit

    if not data_points:
        return BiomarkerTrend(name=name, data_points=[])

    # Deduplicate data points based on date (to the minute) and value
    unique_points = {}
    for p in data_points:
        date_key = p.date.strftime("%Y-%m-%d %H:%M")
        key = (date_key, p.value)
        if key not in unique_points:
            unique_points[key] = p
        else:
            existing = unique_points[key]
            if not existing.unit and p.unit:
                unique_points[key] = p

    data_points = list(unique_points.values())

    # Sort by date ascending for chart
    data_points.sort(key=lambda x: x.date)

    return BiomarkerTrend(
        name=name,
        data_points=data_points,
        unit=last_unit,
        ref_min=None,
        ref_max=None
    )
