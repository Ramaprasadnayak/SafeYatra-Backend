from fastapi import APIRouter, Depends, HTTPException
from schemas.profile import ProfilePicIn
from config.db import users_collection
from utils.auth import current_uid, uid_filter 

router = APIRouter(prefix="/profile", tags=["profile"])
ALLOWED_PREFIX = "https://res.cloudinary.com/"


@router.get("/pic")
def get_profile_pic(uid: str = Depends(current_uid)):
    user = users_collection.find_one(uid_filter(uid), {"profile_pic_url": 1})
    if user is None:
        raise HTTPException(404, "User not found")
    return {"url": user.get("profile_pic_url")}


@router.put("/pic")
def save_profile_pic(body: ProfilePicIn, uid: str = Depends(current_uid)):
    url = body.url.strip()
    if not url:
        raise HTTPException(400, "URL cannot be empty")
    if not url.startswith(ALLOWED_PREFIX):
        raise HTTPException(400, "Invalid image URL")

    result = users_collection.update_one(
        uid_filter(uid), {"$set": {"profile_pic_url": url}}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "User not found")
    return {"message": "Profile picture updated successfully", "url": url}


@router.delete("/pic")
def reset_profile_pic(uid: str = Depends(current_uid)):
    result = users_collection.update_one(
        uid_filter(uid), {"$unset": {"profile_pic_url": ""}}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "User not found")
    return {"message": "Profile picture reset to default"}