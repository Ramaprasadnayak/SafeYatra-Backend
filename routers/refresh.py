from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from config.security import (verify_token,create_access_token)
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

@router.post("/refresh")
def refresh_token(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)

    if payload["type"] != "refresh":
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    access_token = create_access_token(
        data={"sub": payload["sub"]}
    )

    return {
        "access_token": access_token
    }