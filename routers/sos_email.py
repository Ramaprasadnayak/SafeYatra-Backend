import os
import smtplib
from email.message import EmailMessage
from fastapi import APIRouter, Depends, Header, HTTPException
from firebase_admin import auth as fb_auth
from config.db import users_collection
from schemas.sos_email import EmailIn, SosAlertIn


router = APIRouter(prefix="/sos", tags=["sos"])

SENDER_EMAIL = "safeyatra.alerts@gmail.com"
SENDER_APP_PASSWORD = os.getenv("SAFETYTRA_GMAIL_PASSWORD")

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
def add_sos_email(
    body: EmailIn,
    uid: str = Depends(current_uid)
):
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
def get_sos_emails(
    uid: str = Depends(current_uid)
):
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
def send_email(
    receiver: str,
    username: str,
    alert: SosAlertIn
):
    if not SENDER_APP_PASSWORD:
        raise Exception(
            "SAFETYTRA_GMAIL_APP_PASSWORD environment variable is not configured"
        )
    message = EmailMessage()
    message["From"] = SENDER_EMAIL
    message["To"] = receiver
    message["Subject"] = "🚨 SafeYatra SOS Emergency Alert"
    body = f"""
🚨 SAFETYTRA SOS ALERT 🚨

An emergency SOS alert has been triggered from the SafeYatra application.

User:
{username}

Location:
{alert.locality}

District:
{alert.district}

Coordinates:
{alert.coordinates}

Latitude:
{alert.latitude}

Longitude:
{alert.longitude}


Please contact the user immediately if necessary.

This is an automated emergency alert from SafeYatra.
"""

    message.set_content(body)
    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    ) as smtp:
        smtp.login(SENDER_EMAIL,SENDER_APP_PASSWORD)
        smtp.send_message(message)

@router.post("/send-alert")
def send_sos_alert(body: SosAlertIn,uid: str = Depends(current_uid)):
    user = users_collection.find_one(
        {
            "firebase_uid": uid
        },
        {
            "_id": 0,
            "username": 1,
            "sos_emails": 1,
        },
    )
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    username = user.get(
        "username",
        "SafeYatra User"
    )
    sos_emails = user.get(
        "sos_emails",
        []
    )
    if not sos_emails:
        raise HTTPException(
            status_code=400,
            detail="No SOS email addresses configured",
        )

    sent_to = 0
    failed_emails = []
    for receiver in sos_emails:
        receiver = receiver.strip().lower()
        if not receiver:
            continue
        try:
            send_email(
                receiver=receiver,
                username=username,
                alert=body
            )
            sent_to += 1
        except Exception as e:
            print(
                f"Failed to send SOS email to {receiver}: {e}"
            )
            failed_emails.append(receiver)
    if sent_to == 0:
        raise HTTPException(
            status_code=500,
            detail="Failed to send SOS email",
        )
    return {
        "success": True,
        "message": "SOS alert sent successfully",
        "sent_to": sent_to,
        "failed": failed_emails,
    }