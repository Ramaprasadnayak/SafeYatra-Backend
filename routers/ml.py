from fastapi import APIRouter, HTTPException, Query, status
from models.ml_model import SafeYatraRiskModel
router = APIRouter(
    prefix="/ml",
    tags=["machine_learning"]
)

model = SafeYatraRiskModel()
@router.get("/predict/{district_name}")
def prediction(district_name: str,state_name: str | None = Query(default=None)):
    try:
        result = model.predict(
            district_name=district_name,
            state_name=state_name
        )
        return result
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