import requests
from fastapi import APIRouter, Depends, Header, HTTPException
from firebase_admin import auth as fb_auth
from config.db import users_collection
from config.settings import (
    MAILJET_API_KEY,
    MAILJET_SECRET_KEY,
)
from schemas.sos_email import EmailIn, SosAlertIn

router = APIRouter(
    prefix="/sos",
    tags=["sos"],
)

SENDER_EMAIL = "SafeYatra.alerts@gmail.com"
SENDER_NAME = "SafeYatra"
MAILJET_URL = "https://api.mailjet.com/v3.1/send"
MAX_SOS_EMAILS = 2

if not MAILJET_API_KEY or not MAILJET_SECRET_KEY:
    print(
        "WARNING: Mailjet credentials are not configured"
    )

def current_uid(
    authorization: str = Header(...)
) -> str:

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing authorization header",
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header",
        )

    token = authorization[
        len("Bearer "):
    ].strip()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing authentication token",
        )

    try:
        decoded_token = fb_auth.verify_id_token(
            token
        )

        uid = decoded_token.get("uid")

        if not uid:
            raise HTTPException(
                status_code=401,
                detail="Invalid Firebase token",
            )

        return uid

    except HTTPException:
        raise
    except Exception as e:
        print(
            "Firebase authentication error:",
            e,
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

@router.get("/emails")
def get_sos_emails(
    uid: str = Depends(current_uid),
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

    emails = [
        email.strip().lower()
        for email in emails
        if isinstance(email, str)
        and email.strip()
    ]
    emails = list(
        dict.fromkeys(emails)
    )[:MAX_SOS_EMAILS]

    return {
        "emails": emails,
    }


@router.post("/add-email")
def add_sos_email(
    body: EmailIn,
    uid: str = Depends(current_uid),
):

    email = body.email.strip().lower()

    if not email:
        raise HTTPException(
            status_code=400,
            detail="Email cannot be empty",
        )

    user = users_collection.find_one(
        {
            "firebase_uid": uid
        },
        {
            "sos_emails": 1,
        },
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    sos_emails = user.get(
        "sos_emails",
        []
    )

    # Clean existing emails
    sos_emails = [
        item.strip().lower()
        for item in sos_emails
        if isinstance(item, str)
        and item.strip()
    ]

    # Check duplicate
    if email in sos_emails:
        raise HTTPException(
            status_code=400,
            detail="Email already added",
        )

    # Check maximum
    if len(sos_emails) >= MAX_SOS_EMAILS:
        raise HTTPException(
            status_code=400,
            detail=(
                "You can add a maximum of "
                f"{MAX_SOS_EMAILS} SOS emails"
            ),
        )

    users_collection.update_one(
        {
            "firebase_uid": uid
        },
        {
            "$push": {
                "sos_emails": email
            }
        },
    )

    return {
        "message": "Email added successfully",
        "email": email,
    }

@router.delete("/delete-email")
def delete_sos_email(
    body: EmailIn,
    uid: str = Depends(current_uid),
):

    email = body.email.strip().lower()

    if not email:
        raise HTTPException(
            status_code=400,
            detail="Email cannot be empty",
        )

    user = users_collection.find_one(
        {
            "firebase_uid": uid
        },
        {
            "sos_emails": 1,
        },
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    sos_emails = user.get(
        "sos_emails",
        []
    )

    cleaned_emails = [
        item.strip().lower()
        for item in sos_emails
        if isinstance(item, str)
    ]

    if email not in cleaned_emails:
        raise HTTPException(
            status_code=404,
            detail="Email not found",
        )

    users_collection.update_one(
        {
            "firebase_uid": uid
        },
        {
            "$pull": {
                "sos_emails": email
            }
        },
    )

    return {
        "message": "Email deleted successfully",
        "email": email,
    }
def send_email(
    receiver: str,
    username: str,
    alert: SosAlertIn,
):
    if not MAILJET_API_KEY:
        raise Exception(
            "MAILJET_API_KEY is not configured"
        )

    if not MAILJET_SECRET_KEY:
        raise Exception(
            "MAILJET_SECRET_KEY is not configured"
        )
    html_body = f"""
    <html>
        <body>

            <h2>
                🚨 SafeYatra SOS Emergency Alert
            </h2>

            <p>
                An emergency SOS alert has been
                triggered from the SafeYatra application.
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

            <strong>
                Please contact the user immediately
                if necessary.
            </strong>

            <p>
                This is an automated emergency
                alert from SafeYatra.
            </p>

        </body>
    </html>
    """
    payload = {
        "Messages": [
            {
                "From": {
                    "Email": SENDER_EMAIL,
                    "Name": SENDER_NAME,
                },
                "To": [
                    {
                        "Email": receiver,
                    }
                ],
                "Subject": (
                    "🚨 SafeYatra SOS Emergency Alert"
                ),
                "HTMLPart": html_body,
            }
        ]
    }
    try:
        response = requests.post(
            MAILJET_URL,
            auth=(
                MAILJET_API_KEY,
                MAILJET_SECRET_KEY,
            ),
            json=payload,
            timeout=30,
        )
        print(
            "Mailjet status:",
            response.status_code,
        )
        print(
            "Mailjet response:",
            response.text,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(
            "Mailjet request failed:",
            e,
        )

        raise Exception(
            "Failed to send SOS email"
        )
@router.post("/trigger")
def trigger_sos(
    alert: SosAlertIn,
    uid: str = Depends(current_uid),
):
    user = users_collection.find_one(
        {
            "firebase_uid": uid
        },
        {
            "_id": 0,
            "username": 1,
            "name": 1,
            "email": 1,
            "sos_emails": 1,
        },
    )
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    username = (
        user.get("username")
        or user.get("name")
        or user.get("email")
        or "SafeYatra User"
    )

    sos_emails = user.get(
        "sos_emails",
        []
    )

    sos_emails = [
        email.strip().lower()
        for email in sos_emails
        if isinstance(email, str)
        and email.strip()
    ]
    sos_emails = list(
        dict.fromkeys(sos_emails)
    )
    sos_emails = sos_emails[:MAX_SOS_EMAILS]
    if not sos_emails:
        raise HTTPException(
            status_code=400,
            detail=(
                "No SOS email addresses configured. "
                "Please add an SOS email first."
            ),
        )
    sent_emails = []
    failed_emails = []
    for receiver in sos_emails:
        try:
            send_email(
                receiver=receiver,
                username=username,
                alert=alert,
            )
            sent_emails.append(receiver)
        except Exception as e:
            print(
                f"Failed to send SOS email "
                f"to {receiver}: {e}"
            )
            failed_emails.append(receiver)
    if not sent_emails:

        raise HTTPException(
            status_code=502,
            detail=(
                "SOS was triggered, but the "
                "emergency email could not be sent."
            ),
        )
    return {
        "success": True,
        "message": "SOS alert sent successfully",
        "sent_to": sent_emails,
        "failed": failed_emails,
    }