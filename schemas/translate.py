from pydantic import BaseModel

class TranslateRequest(BaseModel):
    source: str
    target: str 