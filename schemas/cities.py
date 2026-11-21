from pydantic import BaseModel, Field
from typing import List

class CityRequest(BaseModel):
    district: str = Field(..., min_length=1)
    limit: int = Field(3, ge=1, le=20)


class CityOut(BaseModel):
    name: str
    latitude: float
    longitude: float
    population: int = 0


class CityResponse(BaseModel):
    message: str
    district: str
    state: str
    cities: List[CityOut]
