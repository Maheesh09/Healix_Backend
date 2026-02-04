import uuid
from sqlalchemy import Column, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class AnatomyCategory(str, enum.Enum):
    HEAD = "HEAD"
    CHEST = "CHEST"
    ABDOMEN = "ABDOMEN"
    LIMBS = "LIMBS"
    GENERAL = "GENERAL"

class HealthAssessment(str, enum.Enum):
    LEVEL_1 = "LEVEL_1" # Critical Low
    LEVEL_2 = "LEVEL_2" # Low
    LEVEL_3 = "LEVEL_3" # Optimal
    LEVEL_4 = "LEVEL_4" # High
    LEVEL_5 = "LEVEL_5" # Critical High
    NONE = "NONE" # No assessment needed
    UNKNOWN = "UNKNOWN"

class MetricReference(Base):
    __tablename__ = "metric_references"

    metric_name = Column(String, primary_key=True)
    threshold_1 = Column(Float, nullable=True) # L1-L2 boundary
    threshold_2 = Column(Float, nullable=True) # L2-L3 (Optimal) boundary
    threshold_3 = Column(Float, nullable=True) # L3-L4 boundary
    threshold_4 = Column(Float, nullable=True) # L4-L5 boundary
    unit = Column(String, nullable=False)
    anatomy_category = Column(Enum(AnatomyCategory), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

class HealthMetric(Base):
    __tablename__ = "health_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # user_id is kept as a simple UUID for now since we don't have a full User model yet
    user_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    metric_name = Column(String, index=True, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    anatomy_category = Column(Enum(AnatomyCategory), nullable=False, default=AnatomyCategory.GENERAL)
    health_assessment = Column(String, nullable=False, default="UNKNOWN")
    
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
