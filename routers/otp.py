import re
from fastapi import APIRouter, HTTPException
from twilio.base.exceptions import TwilioRestException
from config.twilio_client import verify_service
from schemas.otp import VerifyOtpRequest,SendOtpRequest

router = APIRouter(prefix="/otp", tags=["OTP"])
E164 = re.compile(r"^\+[1-9]\d{7,14}$")


def _check_phone(phone: str) -> None:
    if not E164.match(phone):
        raise HTTPException(status_code=400, detail="Invalid phone number")

@router.post("/send/")
def send_otp(body: SendOtpRequest):
    _check_phone(body.phone)
    try:
        verification = verify_service.verifications.create(
            to=body.phone, channel="sms"
        )
        return {"message": "OTP sent", "status": verification.status}
    except TwilioRestException as e:
        if e.code == 60203:  # max send attempts reached
            raise HTTPException(
                status_code=429, detail="Too many attempts. Try again later."
            )
        raise HTTPException(status_code=400, detail=e.msg or "Could not send OTP")

@router.post("/verify/")
def verify_otp(body: VerifyOtpRequest):
    _check_phone(body.phone)
    if not re.fullmatch(r"\d{4,10}", body.code):
        raise HTTPException(status_code=400, detail="Invalid code format")
    try:
        check = verify_service.verification_checks.create(
            to=body.phone, code=body.code
        )
    except TwilioRestException as e:
        if e.code == 20404:  
            raise HTTPException(
                status_code=400, detail="OTP expired. Request a new one."
            )
        if e.code == 60202: 
            raise HTTPException(
                status_code=429, detail="Too many attempts. Request a new OTP."
            )
        raise HTTPException(status_code=400, detail=e.msg or "Verification failed")
    if check.status == "approved":
        return {"message": "OTP verified"}

    raise HTTPException(status_code=400, detail="Incorrect OTP")