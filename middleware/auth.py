from fastapi import Header, HTTPException
from firebase_admin import auth


def verify_firebase_token(authorization: str = Header(...)):
    try:
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization header"
            )
        token = authorization.split("Bearer ", 1)[1]
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except HTTPException:
        raise
    except Exception as e:
        print("Firebase verification error:", repr(e))
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )