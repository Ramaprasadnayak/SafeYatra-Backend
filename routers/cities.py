import re
from fastapi import APIRouter, HTTPException
from config.db import city_collection  
from schemas.cities import CityOut,CityRequest,CityResponse

router = APIRouter(prefix="/cities", tags=["cities"])

def _find_district_doc(name: str):
    name = name.strip()
    base = re.sub(r"\s+district$", "", name, flags=re.IGNORECASE).strip()
    esc = re.escape(base)
    doc = city_collection.find_one(
        {"district": {"$regex": f"^{esc}( District)?$", "$options": "i"}},
        {"_id": 0},
    )
    if doc:
        return doc
    return city_collection.find_one(
        {"district": {"$regex": esc, "$options": "i"}},
        {"_id": 0},
    )

@router.post("/", response_model=CityResponse)
def get_major_cities(req: CityRequest):
    doc = _find_district_doc(req.district)
    if not doc:
        raise HTTPException(status_code=404, detail="District not found")
    best = {}
    for c in doc.get("cities", []):
        if "name" not in c or "latitude" not in c or "longitude" not in c:
            continue
        key = c["name"].strip().lower()
        if key not in best or (c.get("population") or 0) > (best[key].get("population") or 0):
            best[key] = c
    cities = sorted(best.values(), key=lambda c: c.get("population") or 0, reverse=True)
    cities = cities[: req.limit]
    return CityResponse(
        message="Cities fetched successfully",
        district=doc["district"],
        state=doc.get("state", ""),
        cities=[
            CityOut(
                name=c["name"],
                latitude=float(c["latitude"]),
                longitude=float(c["longitude"]),
                population=int(c.get("population") or 0),
            )
            for c in cities
        ],
    )