import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from fastapi import HTTPException, Query, APIRouter
from models.temperature_model import SafeYatraTemperatureModel
from schemas.temperature_model import TemperatureRiskResponse

router = APIRouter(prefix="/ml",tags=["machine_learning"])

temperature_model = SafeYatraTemperatureModel()

@router.get("/temperature-risk",response_model=TemperatureRiskResponse)
def get_temperature_risk(latitude: float = Query(..., ge=-90, le=90),longitude: float = Query(..., ge=-180, le=180)):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max",
        "forecast_days": 2,
        "timezone": "Asia/Kolkata"
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        dates = data["daily"]["time"]
        temperatures = data["daily"]["temperature_2m_max"]
        tomorrow = (
            datetime.now(ZoneInfo("Asia/Kolkata")).date()
            + timedelta(days=1)
        ).isoformat()
        if tomorrow not in dates:
            raise HTTPException(
                status_code=503,
                detail="Tomorrow's temperature forecast is unavailable."
            )
        index = dates.index(tomorrow)
        predicted_temp = temperatures[index]
        if predicted_temp is None:
            raise HTTPException(
                status_code=503,
                detail="Temperature forecast is unavailable."
            )
        result = temperature_model.predict(predicted_temp)
        return TemperatureRiskResponse(
            latitude=latitude,
            longitude=longitude,
            date=tomorrow,
            predicted_max_temperature=result["predicted_max_temperature"],
            risk_label=result["risk_label"],
            risk_score=result["risk_score"],
            source="Open-Meteo + ML Model"
        )

    except requests.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Weather API request failed: {str(e)}"
        )
