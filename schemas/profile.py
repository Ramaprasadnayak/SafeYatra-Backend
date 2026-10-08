from pydantic import BaseModel

class ProfilePicIn(BaseModel):
    url: str