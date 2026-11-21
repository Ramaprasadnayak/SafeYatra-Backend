from pydantic import BaseModel, Field
from typing import Optional


class TemperatureRiskResponse(BaseModel):
    latitude: float
    longitude: float
    date: str
    predicted_max_temperature: float
    risk_label: str
    risk_score: Optional[float] = None
    source: str
