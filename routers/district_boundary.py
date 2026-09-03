from fastapi import HTTPException, APIRouter
from config.db import districts_collection
from rapidfuzz import process, fuzz

router = APIRouter(
    prefix="/api",
    tags=["boundary"]
)

@router.get("/districts/{district_name}/coordinates")
async def get_district_coordinates(district_name: str):
    district_list = list(
        districts_collection.find(
            {},
            {
                "_id": 0,
                "district": 1,
                "district_code": 1
            }
        )
    )
    if not district_list:
        raise HTTPException(
            status_code=404,
            detail="No districts found"
        )
    district_names = [
        item["district"]
        for item in district_list
    ]
    matches = process.extract(
        district_name,
        district_names,
        scorer=fuzz.ratio,
        limit=1
    )
    if not matches:
        raise HTTPException(
            status_code=404,
            detail="District not found"
        )
    matched_name, score, index = matches[0]
    if score < 55:
        raise HTTPException(
            status_code=404,
            detail="District not found"
        )
    matched_district = district_list[index]
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
            "geometry": 1,
            "center":1
        }
    )
    if not district:
        raise HTTPException(
            status_code=404,
            detail="District not found"
        )
    geometry = district["geometry"]
    polygons = []
    if geometry["type"] == "MultiPolygon":
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
    elif geometry["type"] == "Polygon":
        for ring in geometry["coordinates"]:
            converted_ring = []
            for coordinate in ring:
                longitude = coordinate[0]
                latitude = coordinate[1]
                converted_ring.append({
                    "lat": latitude,
                    "lng": longitude
                })
            polygons.append(converted_ring)
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Unsupported geometry type: {geometry['type']}"
        )
    return {
        "message": "retrieved boundary successfully",
        "district": district["district"],
        "matched_name":matched_name,
        "state": district["state"],
        "district_code": district["district_code"],
        "geometry_type": geometry["type"],
        "polygons": polygons,
        "center": district["center"]
    }