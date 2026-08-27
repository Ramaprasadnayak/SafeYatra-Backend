from pydantic import BaseModel

class CoordinatesRequest(BaseModel):
    latitude: float
    longitude: float 