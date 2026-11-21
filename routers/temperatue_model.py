import requests
import time
from threading import Lock
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from fastapi import HTTPException, Query, APIRouter
from models.temperature_model import SafeYatraTemperatureModel
from schemas.temperature_model import TemperatureRiskResponse

router = APIRouter(
    prefix="/ml",
    tags=["machine_learning"]
)

temperature_model = SafeYatraTemperatureModel()
weather_cache = {}
CACHE_TTL = 1800
MAX_CACHE_SIZE = 500
cache_lock = Lock()

def get_weather(latitude, longitude):
    cache_key = (
        round(latitude, 3),
        round(longitude, 3)
    )
    with cache_lock:
        cached = weather_cache.get(cache_key)
        if cached and time.time() - cached["time"] < CACHE_TTL:
            return cached["data"]
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max",
        "past_days": 30,
        "forecast_days": 2,
        "timezone": "Asia/Kolkata"
    }
    for attempt in range(3):
        try:
            response = requests.get(
                url,
                params=params,
                timeout=30
            )
            if response.status_code == 429:
                if attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
                raise HTTPException(
                    status_code=503,
                    detail="Weather API rate limit exceeded."
                )
            if response.status_code >= 500:
                if attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
                raise HTTPException(
                    status_code=503,
                    detail="Weather service unavailable."
                )
            response.raise_for_status()
            data = response.json()
            if "daily" not in data:
                raise HTTPException(
                    status_code=502,
                    detail="Invalid weather data."
                )
            with cache_lock:
                now = time.time()
                expired = [
                    key for key, value in weather_cache.items()
                    if now - value["time"] >= CACHE_TTL
                ]
                for key in expired:
                    weather_cache.pop(key, None)
                if len(weather_cache) >= MAX_CACHE_SIZE:
                    oldest = min(
                        weather_cache,
                        key=lambda k: weather_cache[k]["time"]
                    )
                    weather_cache.pop(oldest)
                weather_cache[cache_key] = {
                    "data": data,
                    "time": now
                }
            return data
        except HTTPException:
            raise
        except requests.RequestException:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise HTTPException(
                status_code=503,
                detail="Unable to connect to Open-Meteo."
            )

@router.get("/temperature-risk",response_model=TemperatureRiskResponse)
def get_temperature_risk(latitude: float = Query(..., ge=-90, le=90),longitude: float = Query(..., ge=-180, le=180)):
    try:
        data = get_weather(latitude, longitude)
        dates = data["daily"]["time"]
        temperatures = data["daily"]["temperature_2m_max"]
        weather_history = dict(zip(dates, temperatures))
        today = datetime.now(
            ZoneInfo("Asia/Kolkata")
        ).date()
        tomorrow = today + timedelta(days=1)
        required_dates = [
            (tomorrow - timedelta(days=i)).isoformat()
            for i in range(30, 0, -1)
        ]
        missing_dates = [
            d for d in required_dates
            if d not in weather_history
            or weather_history[d] is None
        ]
        if missing_dates:
            raise HTTPException(
                status_code=503,
                detail={
                    "message": "30 days of complete weather history unavailable.",
                    "missing_dates": missing_dates
                }
            )
        historical_temperatures = [
            float(weather_history[d])
            for d in required_dates
        ]
        limits = temperature_model.preprocessing.get(
            "plausible_range_c", [-20, 55]
        )
        for temp in historical_temperatures:
            if not limits[0] <= temp <= limits[1]:
                raise HTTPException(
                    status_code=422,
                    detail="Historical temperature outside valid range."
                )
        max_jump = temperature_model.preprocessing.get(
            "max_day_to_day_jump_c", 20
        )
        for previous, current in zip(
            historical_temperatures[:-1],
            historical_temperatures[1:]
        ):
            if abs(current - previous) > max_jump:
                raise HTTPException(
                    status_code=422,
                    detail="Unusual day-to-day temperature change detected."
                )
        result = temperature_model.predict(
            latitude=latitude,
            longitude=longitude,
            target_date=tomorrow,
            temperatures=historical_temperatures
        )
        return TemperatureRiskResponse(
            latitude=latitude,
            longitude=longitude,
            date=tomorrow.isoformat(),
            predicted_max_temperature=result[
                "predicted_max_temperature"
            ],
            risk_label=result["risk_label"],
            risk_score=result["risk_score"],
            source="Open-Meteo + XGBoost"
        )
    except HTTPException:
        raise
    except (KeyError, IndexError, TypeError, ValueError) as e:
        raise HTTPException(
            status_code=500,
            detail=f"Temperature prediction error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal temperature model error: {str(e)}"
        )