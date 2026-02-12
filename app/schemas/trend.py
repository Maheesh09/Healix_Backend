from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class BiomarkerDataPoint(BaseModel):
    date: datetime
    value: float
    unit: Optional[str] = None
    flag: Optional[str] = None

class BiomarkerTrend(BaseModel):
    name: str
    data_points: List[BiomarkerDataPoint]
    unit: Optional[str] = None
    ref_min: Optional[float] = None
    ref_max: Optional[float] = None
