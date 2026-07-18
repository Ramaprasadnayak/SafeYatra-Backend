from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config.db import get_db
from config.security import (hash_password,verify_password,create_access_token,create_refresh_token)
from models.customer import Customer
from schemas.auth import (RegisterRequest,LoginRequest)
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
router = APIRouter(prefix="/auth",tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
 
@router.post("/register")
def register(user: RegisterRequest,db:Session=Depends(get_db)):
    # check if the user exists
    existing_user=db.query(Customer).filter(Customer.username == user.username).first()
    if existing_user:
        return {"message": "Username already exists"}
    existing_phno=db.query(Customer).filter(Customer.phone == user.phone).first()
    if existing_phno:
        return {"message": "Phone number already exists"}
    hashed_password=hash_password(user.password)

    new_user=Customer(
        username=user.username,
        password=hashed_password,
        phone=user.phone
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token = create_access_token({
        "sub": new_user.username,
        "id": new_user.usr_id
    })
    refresh_token=create_refresh_token({
        "sub":new_user.username,
        "id":new_user.usr_id
    })
    
    return {
        "message": "Registration Successful",
        "access_token": access_token,
        "refresh_token":refresh_token,
        "token_type": "bearer"
    }

@router.post("/login")
def login(user:LoginRequest,db:Session=Depends(get_db)):
    # check credentials
    user_exists=db.query(Customer).filter(Customer.username==user.username).first()
    if not user_exists:
        raise HTTPException(status_code=404,detail="User not found")
    given_password=verify_password(user.password,user_exists.password)
    if not given_password:
        raise HTTPException(status_code=401,detail="Invalid username or password")
    access_token=create_access_token({
        "sub":user_exists.username,
        "id":user_exists.usr_id
    })
    refresh_token=create_refresh_token({
        "sub":user_exists.username,
        "id":user_exists.usr_id
    })
    return {
        "message": "Login Successful",
        "access_token": access_token,
        "refresh_token":refresh_token,
        "token_type": "bearer"
    }