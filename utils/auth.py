from fastapi import Header,HTTPException
from firebase_admin import auth as fb_auth

def current_uid(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Invalid authorization header")
    token = authorization[len("Bearer "):].strip()
    if not token:
        raise HTTPException(401, "Missing authentication token")
    try:
        decoded = fb_auth.verify_id_token(token)
    except Exception as e:
        print("Firebase auth error:", e)
        raise HTTPException(401, "Invalid or expired token")
    uid = decoded.get("uid") or decoded.get("user_id") or decoded.get("sub")
    if not uid:
        raise HTTPException(401, "Invalid Firebase token")
    return uid

def uid_filter(uid: str) -> dict:
    return {"$or": [{"firebase_uid": uid}, {"uid": uid}]}
