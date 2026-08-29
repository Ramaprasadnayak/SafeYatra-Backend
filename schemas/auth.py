from pydantic import BaseModel

class RegisterRequest(BaseModel):
    username:str
    Firebaseid: str
    
class Verifyuser(BaseModel):
    username:str