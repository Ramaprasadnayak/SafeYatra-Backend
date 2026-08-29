from fastapi import APIRouter
from config.db import users_collection
from schemas.auth import RegisterRequest, Verifyuser
from fastapi import HTTPException, status

router = APIRouter(prefix="/auth",tags=["Authentication"])
 


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
