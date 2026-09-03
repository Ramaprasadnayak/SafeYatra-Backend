from fastapi import HTTPException, APIRouter
from config.db import districts_collection
from rapidfuzz import process, fuzz
from utils.districts import all_districts

router = APIRouter(
    prefix="/api",
    tags=["boundary"]
)


@router.get("/districts/{district_name}/coordinates")
async def get_district_coordinates(district_name: str):
    matches = process.extract(
        district_name,
        [district["district"] for district in all_districts],
        scorer=fuzz.ratio,
        limit=1
    )
    if not matches:
        raise HTTPException(
            status_code=404,
            detail="District not found"
        )
    matched_name, score, index = matches[0]
    # Reject bad fuzzy matches
    if score < 70:
        raise HTTPException(
            status_code=404,
            detail="District not found"
        )
    matched_district = all_districts[index]
    district_code = matched_district["district_code"]
    district = districts_collection.find_one(
        {
            "district_code": district_code
        },
        {
            "_id": 0,
            "district": 1,
            "state": 1,
            "district_code": 1,
            "geometry": 1
        }
    )
    if not district:
        raise HTTPException(
            status_code=404,
            detail="District not found"
        )
    geometry = district["geometry"]
    polygons = []
    for polygon in geometry["coordinates"]:
        for ring in polygon:
            converted_ring = []
            for coordinate in ring:
                longitude = coordinate[0]
                latitude = coordinate[1]
                converted_ring.append({
                    "lat": latitude,
                    "lng": longitude
                })
            polygons.append(converted_ring)
    return {
        "message": "retrieved boundary successfully",
        "district": district["district"],
        "state": district["state"],
        "district_code": district["district_code"],
        "geometry_type": geometry["type"],
        "polygons": polygons
    }