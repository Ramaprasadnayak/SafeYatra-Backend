from fastapi import HTTPException, APIRouter
import joblib

router = APIRouter(
    prefix="/ml",
    tags=["machine_learning"]
)

@router.get("/predict/{district_name}")
def prediction(district_name:str):
    