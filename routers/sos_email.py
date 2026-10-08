import html
import requests
from fastapi import APIRouter, Depends, HTTPException
from config.db import users_collection
from config.settings import MAILJET_API_KEY, MAILJET_SECRET_KEY
from schemas.sos_email import EmailIn, SosAlertIn
from utils.auth import current_uid, uid_filter

router = APIRouter(prefix="/sos", tags=["sos"])

SENDER_EMAIL = "SafeYatra.alerts@gmail.com"  
SENDER_NAME = "SafeYatra"
MAILJET_URL = "https://api.mailjet.com/v3.1/send"
MAX_SOS_EMAILS = 2



def clean_emails(raw) -> list[str]:
    if not isinstance(raw, list):
        return []
    cleaned = [e.strip().lower() for e in raw if isinstance(e, str) and e.strip()]
    return list(dict.fromkeys(cleaned))[:MAX_SOS_EMAILS]


@router.get("/emails")
def get_sos_emails(uid: str = Depends(current_uid)):
    user = users_collection.find_one(uid_filter(uid), {"_id": 0, "sos_emails": 1})
    # A missing user simply has no SOS emails yet.
    return {"emails": clean_emails((user or {}).get("sos_emails", []))}


@router.post("/add-email")
def add_sos_email(body: EmailIn, uid: str = Depends(current_uid)):
    email = body.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(400, "Enter a valid email address")

    user = users_collection.find_one(uid_filter(uid), {"sos_emails": 1})
    existing = clean_emails((user or {}).get("sos_emails", []))

    if email in existing:
        raise HTTPException(400, "Email already added")
    if len(existing) >= MAX_SOS_EMAILS:
        raise HTTPException(
            400, f"You can add a maximum of {MAX_SOS_EMAILS} SOS emails"
        )

    users_collection.update_one(
        uid_filter(uid),
        {
            "$addToSet": {"sos_emails": email},
            "$setOnInsert": {"firebase_uid": uid},
        },
        upsert=True,  # creates the doc if it didn't exist
    )
    return {"message": "Email added successfully", "email": email}


@router.delete("/delete-email")
def delete_sos_email(body: EmailIn, uid: str = Depends(current_uid)):
    email = body.email.strip().lower()
    if not email:
        raise HTTPException(400, "Email cannot be empty")

    result = users_collection.update_one(
        uid_filter(uid), {"$pull": {"sos_emails": email}}
    )
    if result.modified_count == 0:
        raise HTTPException(404, "Email not found")
    return {"message": "Email deleted successfully", "email": email}


def build_html(username: str, alert: SosAlertIn) -> str:
    e = lambda v: html.escape(str(v if v not in (None, "") else "Unknown"))
    maps_link = ""
    if alert.latitude is not None and alert.longitude is not None:
        url = f"https://www.google.com/maps?q={alert.latitude},{alert.longitude}"
        maps_link = f'<p><a href="{url}">Open location in Google Maps</a></p>'
    return f"""
    <html><body>
      <h2>🚨 SafeYatra SOS Emergency Alert</h2>
      <p>An emergency SOS alert was triggered from the SafeYatra app.</p>
      <hr>
      <p><strong>User:</strong> {e(username)}</p>
      <p><strong>Locality:</strong> {e(alert.locality)}</p>
      <p><strong>District:</strong> {e(alert.district)}</p>
      <p><strong>Coordinates:</strong> {e(alert.coordinates)}</p>
      <p><strong>Latitude:</strong> {e(alert.latitude)}</p>
      <p><strong>Longitude:</strong> {e(alert.longitude)}</p>
      {maps_link}
      <hr>
      <strong>Please contact the user immediately if necessary.</strong>
      <p>This is an automated emergency alert from SafeYatra.</p>
    </body></html>
    """


def send_emails(receivers: list[str], username: str, alert: SosAlertIn):
    """Returns (sent, failed). One Mailjet request, one message per receiver."""
    if not MAILJET_API_KEY or not MAILJET_SECRET_KEY:
        raise HTTPException(500, "Email service is not configured on the server")

    body = build_html(username, alert)
    payload = {
        "Messages": [
            {
                "From": {"Email": SENDER_EMAIL, "Name": SENDER_NAME},
                "To": [{"Email": r}],
                "Subject": "🚨 SafeYatra SOS Emergency Alert",
                "HTMLPart": body,
            }
            for r in receivers
        ]
    }

    try:
        resp = requests.post(
            MAILJET_URL,
            auth=(MAILJET_API_KEY, MAILJET_SECRET_KEY),
            json=payload,
            timeout=30,
        )
        print("Mailjet status:", resp.status_code, resp.text)
        data = resp.json()
    except (requests.RequestException, ValueError) as e:
        print("Mailjet request failed:", e)
        return [], list(receivers)

    results = data.get("Messages", []) if isinstance(data, dict) else []
    sent, failed = [], []
    for receiver, res in zip(receivers, results):
        (sent if res.get("Status") == "success" else failed).append(receiver)
    # Anything Mailjet didn't report on counts as failed.
    failed += [r for r in receivers if r not in sent and r not in failed]
    return sent, failed


@router.post("/trigger")
def trigger_sos(alert: SosAlertIn, uid: str = Depends(current_uid)):
    user = users_collection.find_one(
        uid_filter(uid),
        {"_id": 0, "username": 1, "name": 1, "email": 1, "sos_emails": 1},
    )
    if user is None:
        raise HTTPException(
            404, "Your profile was not found. Please log out and log in again."
        )

    username = (
        user.get("username") or user.get("name") or user.get("email") or "SafeYatra User"
    )
    receivers = clean_emails(user.get("sos_emails", []))
    if not receivers:
        raise HTTPException(
            400, "No SOS email addresses configured. Please add an SOS email first."
        )

    sent, failed = send_emails(receivers, username, alert)
    if not sent:
        raise HTTPException(502, "The emergency email could not be sent.")

    return {
        "success": True,
        "message": "SOS alert sent successfully",
        "sent_to": sent,
        "failed": failed,
    }