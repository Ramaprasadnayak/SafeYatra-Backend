from pydantic import BaseModel

class RegisterRequest(BaseModel):
    firebaseid: str 
    username:str
    email: str    
    phno:str
    
class Verifyuser(BaseModel):
    username:str