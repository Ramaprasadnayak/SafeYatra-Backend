from pydantic import BaseModel, EmailStr

class EmailIn(BaseModel):
    email: EmailStr