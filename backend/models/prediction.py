from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from pydantic import BaseModel
from datetime import datetime
from database import Base

class Prediction(Base):
    """
    SQLAlchemy ORM model for storing sentiment analysis predictions.
    """
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    input_text = Column(String, nullable=False)
    sentiment = Column(String, nullable=False)  # Positive, Negative, Neutral
    confidence = Column(Float, nullable=False)
    pos_prob = Column(Float, nullable=False)
    neg_prob = Column(Float, nullable=False)
    neu_prob = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# ─── Pydantic Schemas For Validation ─────────────────────────────

class PredictionBase(BaseModel):
    input_text: str

class PredictionCreate(PredictionBase):
    pass

class PredictionResponse(BaseModel):
    id: int
    user_id: int
    input_text: str
    sentiment: str
    confidence: float
    pos_prob: float
    neg_prob: float
    neu_prob: float
    created_at: datetime

    class Config:
        from_attributes = True

# Response schemas for paginated history and dashboard statistics
from typing import List

class HistoryResponse(BaseModel):
    total: int
    page: int
    limit: int
    results: List[PredictionResponse]

class KPIModel(BaseModel):
    total: int
    positive_count: int
    positive_pct: float
    negative_count: int
    negative_pct: float
    neutral_count: int
    neutral_pct: float

class PieChartModel(BaseModel):
    positive: int
    negative: int
    neutral: int

class BarChartItem(BaseModel):
    date: str
    count: int

class TrendChartItem(BaseModel):
    date: str
    sentiment_score: float

class StatsResponse(BaseModel):
    kpis: KPIModel
    pie_chart: PieChartModel
    bar_chart: List[BarChartItem]
    trend_chart: List[TrendChartItem]
    recent_activity: List[PredictionResponse]

