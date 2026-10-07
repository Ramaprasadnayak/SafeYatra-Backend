from pydantic import BaseModel


class EmailIn(BaseModel):
    email: str


class SosAlertIn(BaseModel):
    latitude: float | None = None
    longitude: float | None = None
    locality: str
    district: str
    coordinates: str