from geopy.geocoders import Nominatim
from fastapi import APIRouter, status, HTTPException
from schemas.cordinates import CoordinatesRequest

router = APIRouter(
    prefix="/getdistrict",
    tags=["geocode"]
)

@router.post("/")
def geocode(location: CoordinatesRequest):
    try:
        geolocator = Nominatim(user_agent="safeyatra")
        location = geolocator.reverse((location.latitude, location.longitude), language="en")
        address = location.raw.get("address", {})
        return {
            "message" : "retrived district",
            "district" : address.get("state_district") or address.get("county") or address.get("city_district")
        }
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
