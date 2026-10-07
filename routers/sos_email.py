from fastapi import APIRouter, Depends, Header, HTTPException
from firebase_admin import auth as fb_auth,firestore
from config.db import users_collection
from schemas.sos_email import EmailIn, SosAlertIn

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

def _queue_emails(recipients: list[str], subject: str, text: str, html: str) -> None:
    db = firestore.client()
    batch = db.batch()
    for to in recipients:
        batch.set(
            db.collection("mail").document(),
            {"to": [to], "message": {"subject": subject, "text": text, "html": html}},
        )
    batch.commit()


@router.post("/send-alert")
def send_sos_alert(body: SosAlertIn, uid: str = Depends(current_uid)):
    user = users_collection.find_one({"firebase_uid": uid})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    recipients = user.get("sos_emails", [])
    if not recipients:
        raise HTTPException(status_code=400, detail="No emergency emails saved")

    name = user.get("username", "A SafeYatra user")
    map_link = ""
    if body.latitude is not None and body.longitude is not None:
        map_link = f"https://www.google.com/maps?q={body.latitude},{body.longitude}"

    subject = f"🚨 EMERGENCY SOS from {name}"
    text = (
        f"{name} has triggered an Emergency SOS and may need help.\n\n"
        f"Location: {body.locality}\n"
        f"Area: {body.district}\n"
        f"Coordinates: {body.coordinates}\n"
        + (f"Map: {map_link}\n" if map_link else "")
        + "\nPlease contact them immediately or call 112.\n— Sent via SafeYatra"
    )
    html = (
        f"<h2>🚨 Emergency SOS from {name}</h2>"
        f"<p><b>Location:</b> {body.locality}<br>"
        f"<b>Area:</b> {body.district}<br>"
        f"<b>Coordinates:</b> {body.coordinates}</p>"
        + (f'<p><a href="{map_link}">Open in Google Maps</a></p>' if map_link else "")
        + "<p>Please contact them immediately or call 112.</p>"
    )

    try:
        _queue_emails(recipients, subject, text, html)
    except Exception:
        raise HTTPException(status_code=502, detail="Failed to queue emails")

    return {"message": "SOS alert queued", "sent_to": len(recipients)}