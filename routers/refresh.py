from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from config.security import (verify_token,create_access_token)
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/refresh")
def refresh_token(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token, "refresh")
    access_token = create_access_token({
        "sub": payload["sub"],
        "id": payload["id"]
    })
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
    
def get_current_user(token: str = Depends(oauth2_scheme)):
    return verify_token(token, "access")