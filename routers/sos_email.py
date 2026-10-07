from config.settings import MAILJET_API_KEY,MAILJET_SECRET_KEY
from fastapi import APIRouter, Depends, Header, HTTPException
from firebase_admin import auth as fb_auth
from config.db import users_collection
from schemas.sos_email import EmailIn, SosAlertIn
import requests

router = APIRouter(prefix="/sos", tags=["sos"])

if not MAILJET_API_KEY or MAILJET_SECRET_KEY:
    print("WARNING: API_KEY is not configured")

SENDER_EMAIL = "SafeYatra.alerts@gmail.com"

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
    user = users_collection.find_one(
        {"firebase_uid": uid},
        {"sos_emails": 1}
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    sos_emails = user.get("sos_emails", [])
    sos_emails = [
        e.strip().lower()
        for e in sos_emails
        if isinstance(e, str) and e.strip()
    ]
    if len(sos_emails) >= 2:
        raise HTTPException(
            status_code=400,
            detail="You can add a maximum of 2 SOS emails",
        )

    if email in sos_emails:
        raise HTTPException(
            status_code=400,
            detail="Email already added",
        )
    users_collection.update_one(
        {"firebase_uid": uid},
        {
            "$push": {
                "sos_emails": email
            }
        }
    )

    return {
        "message": "Email added",
        "email": email,
    }
    
    
@router.delete("/delete-email")
def delete_sos_email(
    body: EmailIn,
    uid: str = Depends(current_uid)
):
    email = body.email.strip().lower()

    result = users_collection.update_one(
        {
            "firebase_uid": uid,
            "sos_emails": email
        },
        {
            "$pull": {
                "sos_emails": email
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="User or email not found",
        )

    if result.modified_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Email not found",
        )

    return {
        "message": "Email deleted",
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
            <p><strong>User:</strong> {username}</p>
            <h3>Location Information</h3>
            <p><strong>Locality:</strong> {alert.locality}</p>
            <p><strong>District:</strong> {alert.district}</p>
            <p><strong>Coordinates:</strong> {alert.coordinates}</p>
            <p><strong>Latitude:</strong> {alert.latitude}</p>
            <p><strong>Longitude:</strong> {alert.longitude}</p>
            <hr>
            <strong>
                Please contact the user immediately if necessary.
            </strong>
            <p>
                This is an automated emergency alert from SafeYatra.
            </p>
        </body>
    </html>
    """
    response = requests.post(
        "https://api.mailjet.com/v3.1/send",
        auth=(
            MAILJET_API_KEY,
            MAILJET_SECRET_KEY
        ),
        json={
            "Messages": [
                {
                    "From": {
                        "Email": SENDER_EMAIL,
                        "Name": "SafeYatra"
                    },
                    "To": [
                        {
                            "Email": receiver
                        }
                    ],
                    "Subject": "🚨 SafeYatra SOS Emergency Alert",
                    "HTMLPart": html_body
                }
            ]
        }
    )
    response.raise_for_status()
    return response.json()