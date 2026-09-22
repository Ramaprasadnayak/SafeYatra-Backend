from geopy.geocoders import Nominatim
from fastapi import APIRouter, status, HTTPException
from schemas.cordinates import CoordinatesRequest

router = APIRouter(
    prefix="/getdistrict",
    tags=["geocode"]
)

geolocator = Nominatim(
    user_agent="SafeYatra/1.0 (tourist-safety-app)",
    timeout=10
)

@router.post("/")
def geocode(location: CoordinatesRequest):
    try:
        result = geolocator.reverse(
            (location.latitude, location.longitude),
            language="en",
            addressdetails=True
        )
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Location could not be determined"
            )
        address = result.raw.get("address", {})
        district = (
            address.get("state_district")
            or address.get("county")
            or address.get("city_district")
        )
        if not district:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="District not found for this location"
            )
        return {
            "message": "Retrieved district",
            "district": district
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Geocoding service unavailable: {str(e)}"
        )