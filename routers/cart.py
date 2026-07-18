from fastapi import APIRouter, Depends, status, HTTPException
from config.db import get_db
from sqlalchemy.orm import Session
from models.cart import Cart
from models.medicine import Medicine
from schemas.cart_schemas import CartRequest,CartQuantityRequest

router = APIRouter(prefix="/cart", tags=["cartQuery"])

# return all items of requested uid
@router.get("/userid/{usrid}")
def cartFunction(usrid: int, db: Session = Depends(get_db)):
    try:
        cart_items = (
            db.query(
                Medicine.med_id,
                Medicine.medicine_name,
                Medicine.category,
                Medicine.price,
                Medicine.stock,
                Medicine.image_url,
                Cart.quantity,
                (Medicine.price * Cart.quantity).label("total")
            ).join(Medicine, Cart.med_id == Medicine.med_id)
            .filter(Cart.usr_id == usrid)
            .all()
        )
        data = [{
            "medid":item.med_id,
            "medicine_name": item.medicine_name,
            "category": item.category,
            "price": float(item.price),
            "stock": item.stock,
            "image_url": item.image_url,
            "quantity": item.quantity,
            "total":item.total
            }
            for item in cart_items
        ]

        return {
            "status": 200,
            "message": "Retrieved cart info",
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# add to cart for requested uid
@router.post("/addtocart")
def addToCart(request: CartRequest, db: Session = Depends(get_db)):
    try:
        duplicate_entry=db.query(Cart).filter(Cart.usr_id==request.usrid,Cart.med_id==request.medid).first()
        if duplicate_entry:
            duplicate_entry.quantity+=1
        else:
            item=Cart(
                usr_id=request.usrid,
                med_id=request.medid,
                quantity=1
            )
            db.add(item)
        db.commit()
        return {
            "status": 200,
            "message": "Added to cart"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# alter the quantity of medicines
@router.post("/addtocart/quantity")
def alter_quantity(request:CartQuantityRequest,db: Session = Depends(get_db)):
    try:
        entry = (
            db.query(Cart).filter(Cart.usr_id == request.usrid,Cart.med_id == request.medid).first()
        )
        if entry is None:
            raise HTTPException(
                status_code=404,
                detail="Cart item not found"
            )
        if request.action == 1:
            entry.quantity += 1
        elif request.action == 0:
            if entry.quantity > 1:
                entry.quantity -= 1
            else:
                db.delete(entry)   
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid action"
            )
        db.commit()
        return {
            "status": 200,
            "message": "Quantity updated"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# delete the product from cart of requested uid
@router.delete("/deletefromcart")
def delete_from_cart(request: CartRequest, db: Session = Depends(get_db)):
    try:
        available_entry = db.query(Cart).filter(Cart.usr_id == request.usrid,Cart.med_id == request.medid).first()
        if not available_entry:
            return {
                "status": 404,
                "message": "Item not found"
            }
        db.delete(available_entry)
        db.commit()
        return {
            "status": 200,
            "message": "Deleted from cart"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )