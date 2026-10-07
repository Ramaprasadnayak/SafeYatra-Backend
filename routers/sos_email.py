import os
import resend
from fastapi import APIRouter, Depends, Header, HTTPException
from firebase_admin import auth as fb_auth
from config.db import users_collection
from schemas.sos_email import EmailIn, SosAlertIn

router = APIRouter(prefix="/sos", tags=["sos"])

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
if not RESEND_API_KEY:
    print("WARNING: RESEND_API_KEY is not configured")
resend.api_key = RESEND_API_KEY

# This works for testing with Resend's provided sender.
#
# For production, verify your own domain in Resend and change
# this to something like:
#
# alerts@yourdomain.com

SENDER_EMAIL = "SafeYatra <onboarding@resend.dev>"

def current_uid(authorization: str = Header(...)) -> str:
    try:
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization header",
            )
        token = authorization.replace(
            "Bearer ",
            "",
            1
        ).strip()
        if not token:
            raise HTTPException(
                status_code=401,
                detail="Missing authentication token",
            )
        decoded_token = fb_auth.verify_id_token(token)
        return decoded_token["uid"]
    except HTTPException:
        raise
    except Exception as e:
        print("Firebase authentication error:", e)
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
        {
            "firebase_uid": uid
        },
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
        {
            "firebase_uid": uid
        },
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
    emails = user.get(
        "sos_emails",
        []
    )
    return {
        "emails": emails,
    }

def send_email(
    receiver: str,
    username: str,
    alert: SosAlertIn
):
    if not RESEND_API_KEY:
        raise Exception(
            "RESEND_API_KEY is not configured"
        )
    html_body = f"""
    <html>
        <body>

            <h2>🚨 SafeYatra SOS Emergency Alert</h2>

            <p>
                An emergency SOS alert has been triggered
                from the SafeYatra application.
            </p>

            <hr>

            <h3>User Information</h3>

            <p>
                <strong>User:</strong>
                {username}
            </p>

            <h3>Location Information</h3>

            <p>
                <strong>Locality:</strong>
                {alert.locality}
            </p>

            <p>
                <strong>District:</strong>
                {alert.district}
            </p>

            <p>
                <strong>Coordinates:</strong>
                {alert.coordinates}
            </p>

            <p>
                <strong>Latitude:</strong>
                {alert.latitude}
            </p>

            <p>
                <strong>Longitude:</strong>
                {alert.longitude}
            </p>

            <hr>

            <p>
                <strong>
                    Please contact the user immediately
                    if necessary.
                </strong>
            </p>

            <p>
                This is an automated emergency alert
                from SafeYatra.
            </p>

        </body>
    </html>
    """
    params = {
        "from": SENDER_EMAIL,
        "to": [
            receiver
        ],
        "subject": "🚨 SafeYatra SOS Emergency Alert",
        "html": html_body,
    }
    response = resend.Emails.send(params)
    print(
        f"SOS email sent to {receiver}: {response}"
    )
    return response

@router.post("/send-alert")
def send_sos_alert(
    body: SosAlertIn,
    uid: str = Depends(current_uid)
):
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
                f"Failed to send email to {receiver}: {e}"
            )
            failed_emails.append({
                "email": receiver,
                "error": str(e)
            })
    if sent_to == 0:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to send SOS email",
                "failed": failed_emails
            }
        )
    return {
        "success": True,
        "message": "SOS alert sent successfully",
        "sent_to": sent_to,
        "failed": failed_emails,
    }