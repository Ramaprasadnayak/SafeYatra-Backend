from pydantic import BaseModel

class TemperatureRiskResponse(BaseModel):
    latitude: float
    longitude: float
    date: str
    predicted_max_temperature: float
    risk_label: str
    risk_score: float
    source: str
