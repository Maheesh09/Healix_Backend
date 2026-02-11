from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.biomarker import Biomarker
from app.models.report import Report
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
    Get list of available biomarker names for a patient.
    Combines names from both report biomarkers and manually entered health metrics.
    """
    # Names from report biomarkers
    biomarker_results = (
        db.query(Biomarker.name)
        .join(Report)
        .filter(Report.patient_id == patient_id)
        .distinct()
        .all()
    )
    names = set(r[0] for r in biomarker_results)

    # Names from health_metrics (user_id == patient_id)
    hm_results = (
        db.query(HealthMetric.metric_name)
        .filter(HealthMetric.user_id == patient_id)
        .distinct()
        .all()
    )
    for r in hm_results:
        names.add(r[0])

    return sorted(list(names))

@router.get("/data", response_model=BiomarkerTrend)
def get_biomarker_data(
    patient_id: UUID,
    name: str,
    db: Session = Depends(get_db)
):
    """
    Get trend data for a specific biomarker.
    Merges data from report biomarkers and manually entered health metrics.
    """
    data_points = []
    last_unit = None
    last_ref_min = None
    last_ref_max = None

    # 1. Get data from report biomarkers
    results = (
        db.query(Biomarker, Report)
        .join(Report)
        .filter(Report.patient_id == patient_id, Biomarker.name == name)
        .order_by(desc(Report.created_at))
        .all()
    )

    for bookmark, report in results:
        date_val = report.sample_collected_at or report.created_at
        if bookmark.value is not None:
             data_points.append(BiomarkerDataPoint(
                date=date_val,
                value=bookmark.value,
                unit=bookmark.unit,
                flag=bookmark.flag
            ))
        if last_unit is None and bookmark.unit:
            last_unit = bookmark.unit
        if last_ref_min is None and bookmark.ref_min is not None:
            last_ref_min = bookmark.ref_min
        if last_ref_max is None and bookmark.ref_max is not None:
            last_ref_max = bookmark.ref_max

    # 2. Get data from health_metrics table
    # Match by exact metric_name, or by known aliases
    metric_names_to_query = [name]
    # Add reverse lookups: if querying "Fasting Plasma Glucose", also grab "Blood Glucose" etc.
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
    # This prevents showing duplicate points if data exists in both tables
    unique_points = {}
    for p in data_points:
        # Determine date key (round to minute to catch slight differences)
        date_key = p.date.strftime("%Y-%m-%d %H:%M")
        key = (date_key, p.value)
        
        # Prefer points with units/flags if existing one doesn't have them
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
        ref_min=last_ref_min,
        ref_max=last_ref_max
    )
