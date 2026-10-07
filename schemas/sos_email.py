from pydantic import BaseModel, EmailStr
from typing import Optional

class EmailIn(BaseModel):
    email: EmailStr

class SosAlertIn(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    locality: str = ""
    district: str = ""
    coordinates: str = ""