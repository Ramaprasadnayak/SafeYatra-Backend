# validate incomming raw json
from pydantic import BaseModel


class RegisterRequest(BaseModel):
    username: str
    password: str
    phone: str


class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str