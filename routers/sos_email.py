from fastapi import APIRouter, Depends, Header, HTTPException
from firebase_admin import auth as fb_auth
from config.db import users_collection
from schemas.sos_email import EmailIn

router = APIRouter(prefix="/sos", tags=["sos"])

def current_uid(authorization: str = Header(...)) -> str:
    try:
        token = authorization.split("Bearer ")[1]
        return fb_auth.verify_id_token(token)["uid"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.post("/add-email")
def add_sos_email(body: EmailIn, uid: str = Depends(current_uid)):
    email = body.email.lower()
    result = users_collection.update_one(
        {"firebase_uid": uid},         
        {"$addToSet": {"sos_emails": email}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Email already added")
    return {"message": "Email added", "email": email}