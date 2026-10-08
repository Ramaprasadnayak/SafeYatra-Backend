# schemas/sos_email.py
from typing import Optional
from pydantic import BaseModel

class EmailIn(BaseModel):
    email: str

class SosAlertIn(BaseModel):
    locality: str = ""
    district: str = ""
    coordinates: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None