from fastapi import APIRouter, Depends, Header, HTTPException
from firebase_admin import auth as fb_auth
from config.db import users_collection
from schemas.sos_email import EmailIn

router = APIRouter(prefix="/sos", tags=["sos"])

def current_uid(authorization: str = Header(...)) -> str:
    try:
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization header",
            )
        token = authorization.replace("Bearer ", "", 1).strip()
        if not token:
            raise HTTPException(
                status_code=401,
                detail="Missing authentication token",
            )
        decoded_token = fb_auth.verify_id_token(token)
        return decoded_token["uid"]
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

@router.post("/add-email")
def add_sos_email(body: EmailIn,uid: str = Depends(current_uid)):
    email = body.email.strip().lower()
    result = users_collection.update_one(
        {"firebase_uid": uid},
        {
            "$addToSet": {
                "sos_emails": email
            }
        },
    )
    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    if result.modified_count == 0:
        raise HTTPException(
            status_code=400,
            detail="Email already added",
        )
    return {
        "message": "Email added",
        "email": email,
    }

@router.get("/emails")
def get_sos_emails(uid: str = Depends(current_uid)):
    user = users_collection.find_one(
        {"firebase_uid": uid},
        {
            "_id": 0,
            "sos_emails": 1,
        },
    )
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    emails = user.get("sos_emails", [])
    return {
        "emails": emails,
    }