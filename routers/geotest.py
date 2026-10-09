import geopandas as gpd
from fastapi import APIRouter, HTTPException, status
from shapely.geometry import Point
from schemas.cordinates import CoordinatesRequest

router = APIRouter(prefix="/getdistrict", tags=["geocode"])

districts = gpd.read_file("data/india_districts.geojson").to_crs(4326)
_ = districts.sindex


@router.post("/")
def geocode(location: CoordinatesRequest):
    pt = Point(location.longitude, location.latitude)  # (lon, lat) order
    hits = districts.sindex.query(pt, predicate="intersects")
    if len(hits) == 0:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "District not found for this location"
        )
    row = districts.iloc[hits[0]]
    return {
        "message": "Retrieved district",
        "district": row["district"],
        "state": row["st_nm"],
    }