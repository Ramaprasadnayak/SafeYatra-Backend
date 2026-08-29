from fastapi import APIRouter
from config.db import users_collection
from middleware.auth import verify_firebase_token
from schemas.auth import RegisterRequest, Verifyuser
from fastapi import HTTPException, status, Depends

router = APIRouter(prefix="/auth",tags=["Authentication"])

@router.get("/getinfo")
def get_user_info(decoded_token: dict = Depends(verify_firebase_token)):
    try:
        uid = decoded_token["uid"]
        user = users_collection.find_one({
            "firebase_uid": uid
        })
        if not user:
            return {
                "message": "User not found",
                "info": []
            }
        return {
            "message": "retrieved info",
            "info": [
                user.get("username"),
                user.get("phone"),
                user.get("email")
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
@router.post("/verifyuser")
def verifyuser(user: Verifyuser):
    try:
        existing_user = users_collection.find_one({"username": user.username})
        if existing_user:
            return {"message": "Username already exists"}
        else:
            return {"message": "Unique user"}
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
 
 
@router.post("/register")
def register(user: RegisterRequest):
    try:
        existing_user = users_collection.find_one({"username": user.username})
        if existing_user:
            return {"message": "Username already exists"}

        # create user
        users_collection.insert_one({
            "Firebaseid":user.Firebaseid,
            "username": user.username,
            "email": user.email
        })

        return {"message": "User registered"}
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
