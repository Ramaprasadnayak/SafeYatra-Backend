from fastapi import APIRouter, HTTPException, status
from models.ml_model import SafeYatraRiskModel
router = APIRouter(
    prefix="/ml",
    tags=["machine_learning"]
)

model = SafeYatraRiskModel()
@router.get("/predict/{district_name}")
def prediction(district_name: str):
    try:
        result = model.predict(district_name=district_name)
        return {
            "message":"Prediction Successful",
            "result":result,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to calculate district risk."
        )