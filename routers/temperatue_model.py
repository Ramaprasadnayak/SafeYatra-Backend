import requests
import time
from threading import Lock
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from fastapi import HTTPException, Query, APIRouter
from models.temperature_model import SafeYatraTemperatureModel
from schemas.temperature_model import TemperatureRiskResponse

router = APIRouter(prefix="/ml", tags=["machine_learning"])

temperature_model = SafeYatraTemperatureModel()

weather_cache = {}
CACHE_TTL = 1800
MAX_CACHE_SIZE = 500
cache_lock = Lock()

def get_weather(latitude, longitude):
    cache_key = (round(latitude, 3), round(longitude, 3))
    with cache_lock:
        cached = weather_cache.get(cache_key)
        if cached and time.time() - cached["time"] < CACHE_TTL:
            return cached["data"]
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max",
        "forecast_days": 2,
        "timezone": "Asia/Kolkata"
    }
    for attempt in range(3):
        try:
            response = requests.get(
                url,
                params=params,
                timeout=15
            )
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                try:
                    delay = min(float(retry_after), 5) if retry_after else 2 ** attempt
                except ValueError:
                    delay = 2 ** attempt
                if attempt < 2:
                    time.sleep(delay)
                    continue
                raise HTTPException(
                    status_code=503,
                    detail="Weather API rate limit exceeded. Please try again later."
                )
            if response.status_code >= 500:
                if attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
                raise HTTPException(
                    status_code=503,
                    detail="Weather service is temporarily unavailable."
                )
            response.raise_for_status()
            data = response.json()
            if "daily" not in data:
                raise HTTPException(
                    status_code=502,
                    detail="Invalid weather data received."
                )
            with cache_lock:
                now = time.time()
                expired_keys = [
                    key for key, value in weather_cache.items()
                    if now - value["time"] >= CACHE_TTL
                ]
                for key in expired_keys:
                    weather_cache.pop(key, None)
                if len(weather_cache) >= MAX_CACHE_SIZE:
                    oldest_key = min(
                        weather_cache,
                        key=lambda k: weather_cache[k]["time"]
                    )
                    weather_cache.pop(oldest_key)
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
                detail="Unable to connect to the weather service."
            )
@router.get("/temperature-risk",response_model=TemperatureRiskResponse)
def get_temperature_risk(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180)):
    try:
        data = get_weather(latitude, longitude)
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

    except HTTPException:
        raise

    except (KeyError, IndexError, TypeError):
        raise HTTPException(
            status_code=502,
            detail="Unexpected weather data format."
        )
