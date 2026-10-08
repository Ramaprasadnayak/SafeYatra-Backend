import html
import requests

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from firebase_admin import auth as fb_auth

from config.db import users_collection
from config.settings import MAILJET_API_KEY, MAILJET_SECRET_KEY
from schemas.sos_email import EmailIn, SosAlertIn


router = APIRouter(prefix="/sos", tags=["sos"])


# ============================================================
# CONFIGURATION
# ============================================================

SENDER_EMAIL = "SafeYatra.alerts@gmail.com"
SENDER_NAME = "SafeYatra"

MAILJET_URL = "https://api.mailjet.com/v3.1/send"

MAX_SOS_EMAILS = 2


# ============================================================
# FIREBASE AUTHENTICATION
# ============================================================

# This creates the Bearer authentication scheme in Swagger.
security = HTTPBearer()


def current_uid(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:

    # HTTPBearer automatically removes:
    #
    # Authorization: Bearer
    #
    # and gives us only the token here.
    token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing authentication token",
        )

    try:
        # Verify Firebase ID token
        decoded = fb_auth.verify_id_token(token)

    except Exception as e:
        print("Firebase auth error:", e)

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired Firebase token",
        )

    # Firebase normally provides uid.
    uid = (
        decoded.get("uid")
        or decoded.get("user_id")
        or decoded.get("sub")
    )

    if not uid:
        raise HTTPException(
            status_code=401,
            detail="Invalid Firebase token: UID not found",
        )

    print("Authenticated Firebase UID:", uid)

    return uid


# ============================================================
# MONGODB UID FILTER
# ============================================================

def uid_filter(uid: str) -> dict:
    """
    Supports either:
        firebase_uid
    or:
        uid
    in the MongoDB document.
    """

    return {
        "$or": [
            {"firebase_uid": uid},
            {"uid": uid},
        ]
    }


# ============================================================
# EMAIL CLEANING
# ============================================================

def clean_emails(raw) -> list[str]:

    if not isinstance(raw, list):
        return []

    cleaned = [
        email.strip().lower()
        for email in raw
        if isinstance(email, str) and email.strip()
    ]

    # Remove duplicates while preserving order
    cleaned = list(dict.fromkeys(cleaned))

    # Maximum 2 emails
    return cleaned[:MAX_SOS_EMAILS]


# ============================================================
# GET SOS EMAILS
# ============================================================

@router.get("/emails")
def get_sos_emails(
    uid: str = Depends(current_uid),
):

    print("Getting SOS emails for UID:", uid)

    user = users_collection.find_one(
        uid_filter(uid),
        {
            "_id": 0,
            "sos_emails": 1,
        },
    )

    return {
        "emails": clean_emails(
            (user or {}).get("sos_emails", [])
        )
    }


# ============================================================
# ADD SOS EMAIL
# ============================================================

@router.post("/add-email")
def add_sos_email(
    body: EmailIn,
    uid: str = Depends(current_uid),
):

    email = body.email.strip().lower()

    if not email or "@" not in email:
        raise HTTPException(
            status_code=400,
            detail="Enter a valid email address",
        )

    print("Adding SOS email:", email)
    print("For Firebase UID:", uid)

    user = users_collection.find_one(
        uid_filter(uid),
        {
            "sos_emails": 1,
        },
    )

    existing = clean_emails(
        (user or {}).get("sos_emails", [])
    )

    # Prevent duplicate email
    if email in existing:
        raise HTTPException(
            status_code=400,
            detail="Email already added",
        )

    # Maximum 2 emails
    if len(existing) >= MAX_SOS_EMAILS:
        raise HTTPException(
            status_code=400,
            detail=f"You can add a maximum of {MAX_SOS_EMAILS} SOS emails",
        )

    users_collection.update_one(
        uid_filter(uid),
        {
            "$addToSet": {
                "sos_emails": email
            },
            "$setOnInsert": {
                "firebase_uid": uid
            },
        },
        upsert=True,
    )

    return {
        "message": "Email added successfully",
        "email": email,
    }


# ============================================================
# DELETE SOS EMAIL
# ============================================================

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

    print("Deleting SOS email:", email)
    print("For Firebase UID:", uid)

    result = users_collection.update_one(
        uid_filter(uid),
        {
            "$pull": {
                "sos_emails": email
            }
        },
    )

    if result.modified_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Email not found",
        )

    return {
        "message": "Email deleted successfully",
        "email": email,
    }


# ============================================================
# BUILD SOS EMAIL HTML
# ============================================================

def build_html(
    username: str,
    alert: SosAlertIn,
) -> str:

    def escape(value):

        return html.escape(
            str(
                value
                if value not in (None, "")
                else "Unknown"
            )
        )

    maps_link = ""

    if (
        alert.latitude is not None
        and alert.longitude is not None
    ):

        url = (
            f"https://www.google.com/maps"
            f"?q={alert.latitude},{alert.longitude}"
        )

        maps_link = f"""
        <p>
            <a href="{url}">
                Open location in Google Maps
            </a>
        </p>
        """

    return f"""
    <html>
        <body>

            <h2>🚨 SafeYatra SOS Emergency Alert</h2>

            <p>
                An emergency SOS alert was triggered
                from the SafeYatra app.
            </p>

            <hr>

            <p>
                <strong>User:</strong>
                {escape(username)}
            </p>

            <p>
                <strong>Locality:</strong>
                {escape(alert.locality)}
            </p>

            <p>
                <strong>District:</strong>
                {escape(alert.district)}
            </p>

            <p>
                <strong>Coordinates:</strong>
                {escape(alert.coordinates)}
            </p>

            <p>
                <strong>Latitude:</strong>
                {escape(alert.latitude)}
            </p>

            <p>
                <strong>Longitude:</strong>
                {escape(alert.longitude)}
            </p>

            {maps_link}

            <hr>

            <strong>
                Please contact the user immediately if necessary.
            </strong>

            <p>
                This is an automated emergency alert
                from SafeYatra.
            </p>

        </body>
    </html>
    """


# ============================================================
# SEND EMAILS THROUGH MAILJET
# ============================================================

def send_emails(
    receivers: list[str],
    username: str,
    alert: SosAlertIn,
):

    if not MAILJET_API_KEY or not MAILJET_SECRET_KEY:

        raise HTTPException(
            status_code=500,
            detail="Email service is not configured on the server",
        )

    body = build_html(
        username,
        alert,
    )

    payload = {
        "Messages": [
            {
                "From": {
                    "Email": SENDER_EMAIL,
                    "Name": SENDER_NAME,
                },

                "To": [
                    {
                        "Email": receiver
                    }
                ],

                "Subject": (
                    "🚨 SafeYatra SOS Emergency Alert"
                ),

                "HTMLPart": body,
            }

            for receiver in receivers
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

        data = response.json()

    except requests.RequestException as e:

        print(
            "Mailjet request failed:",
            e,
        )

        return [], list(receivers)

    except ValueError as e:

        print(
            "Invalid Mailjet JSON response:",
            e,
        )

        return [], list(receivers)

    results = (
        data.get("Messages", [])
        if isinstance(data, dict)
        else []
    )

    sent = []
    failed = []

    for receiver, result in zip(
        receivers,
        results,
    ):

        if result.get("Status") == "success":

            sent.append(receiver)

        else:

            failed.append(receiver)

    # Anything not reported by Mailjet
    # is considered failed.
    failed += [
        receiver
        for receiver in receivers
        if receiver not in sent
        and receiver not in failed
    ]

    return sent, failed


# ============================================================
# TRIGGER SOS
# ============================================================

@router.post("/trigger")
def trigger_sos(
    alert: SosAlertIn,
    uid: str = Depends(current_uid),
):

    print("====================================")
    print("SOS TRIGGERED")
    print("Firebase UID:", uid)
    print("====================================")

    # Find the authenticated user's MongoDB document
    user = users_collection.find_one(
        uid_filter(uid),
        {
            "_id": 0,
            "username": 1,
            "name": 1,
            "email": 1,
            "sos_emails": 1,
        },
    )

    if user is None:

        print(
            "MongoDB user not found for UID:",
            uid,
        )

        raise HTTPException(
            status_code=404,
            detail=(
                "Your profile was not found. "
                "Please log out and log in again."
            ),
        )

    # Determine username
    username = (
        user.get("username")
        or user.get("name")
        or user.get("email")
        or "SafeYatra User"
    )

    # Get configured SOS emails
    receivers = clean_emails(
        user.get("sos_emails", [])
    )

    print("Username:", username)
    print("SOS receivers:", receivers)

    if not receivers:

        raise HTTPException(
            status_code=400,
            detail=(
                "No SOS email addresses configured. "
                "Please add an SOS email first."
            ),
        )

    # Send email
    sent, failed = send_emails(
        receivers,
        username,
        alert,
    )

    print("Sent:", sent)
    print("Failed:", failed)

    if not sent:

        raise HTTPException(
            status_code=502,
            detail=(
                "The emergency email could not be sent."
            ),
        )

    return {
        "success": True,
        "message": "SOS alert sent successfully",
        "sent_to": sent,
        "failed": failed,
    }