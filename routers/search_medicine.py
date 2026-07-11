from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.db import get_db
from models.medicine import Medicine
from schemas.medicine_schemas import CategoryResponse
from utils.category_map import CATEGORY_MAP


router = APIRouter(prefix="/medicines", tags=["SearchQuery"])

@router.get("/search/")
def search(query: str, db: Session = Depends(get_db)):
    try:
        from rapidfuzz import process
        medicine = db.query(Medicine).all()

        itemname = [p.medicine_name for p in medicine]
        matches = process.extract(query.upper(), itemname, limit=50)

        result = []
        for _, score, index in matches:
            med = medicine[index]
            result.append({
                "med_id": med.med_id,
                "medicine_name": med.medicine_name,
                "category": med.category,
                "price": med.price,
                "stock": med.stock,
                "image_url": med.image_url
            })

        return {
            "status": 200,
            "message": "Medicines fetched successfully",
            "data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/category/{category}", response_model=CategoryResponse)
def get_category(category: str, db: Session = Depends(get_db)):
    csv_categories = CATEGORY_MAP.get(category)

    if not csv_categories:
        return {
            "status": 404,
            "message": "Category not found",
            "data": []
        }
    medicines = (
        db.query(Medicine)
        .filter(Medicine.category.in_(csv_categories))
        .limit(50)
        .all()
    )
    return {
        "status": 200,
        "message": "Medicines fetched successfully",
        "data": medicines
    }

@router.get("/popular")
def popular_medicine(db: Session = Depends(get_db)):
    try:
        result = db.query(Medicine).order_by(Medicine.sales.desc()).limit(50).all()
        return {
            "status": 200,
            "message": "Medicines fetched successfully",
            "data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )