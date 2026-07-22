from fastapi import APIRouter, Depends, status, HTTPException
from config.db import get_db
from sqlalchemy.orm import Session
from models.medicine import Medicine
from models.cart import Cart
from schemas.order import AddressRequest,DeleteAddressRequest
from models.order import Address
from routers.refresh import get_current_user


router = APIRouter(prefix="/order", tags=["orderQuery"])


@router.get("/getaddress/{usrid}")
def getAddress(usrid: int,current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        addresses = db.query(Address).filter(Address.usr_id == usrid).all()
        if not addresses:
            addresses=[]
        return {
            "status": 200,
            "message": "Retrieved addresses",
            "data": [
                {
                    "addressid":address.addressid,
                    "address": address.address
                }
                for address in addresses
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/postaddress")
def post_address(query: AddressRequest,current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        address = Address(
            usr_id=query.userid,
            address=query.address
        )
        db.add(address)
        db.commit()
        db.refresh(address)

        return {
            "status": 200,
            "message": "Address saved successfully"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/getmedicine/{medid}/{usrid}")
def getMedicine(medid: int,usrid: int,current_user=Depends(get_current_user),db: Session = Depends(get_db)):
    try:
        medicine = (
            db.query(
                Medicine.med_id,
                Medicine.medicine_name,
                Medicine.price,
                Medicine.category,
                Cart.quantity,
                (Medicine.price * Cart.quantity).label("total")
            ).join(Cart, Cart.med_id == Medicine.med_id)
            .filter(Cart.med_id == medid,Cart.usr_id == usrid).first()
        )
        if medicine is None:
            cart=Cart(
                usr_id=usrid,
                med_id=medid,
                quantity=1
            )
            db.add(cart)
            db.commit()
            medicine = (
            db.query(
                Medicine.med_id,
                Medicine.medicine_name,
                Medicine.price,
                Medicine.category,
                Cart.quantity,
                (Medicine.price * Cart.quantity).label("total")
                ).join(Cart, Cart.med_id == Medicine.med_id)
                .filter(Cart.med_id == medid,Cart.usr_id == usrid).first()
            )
        return {
            "status": 200,
            "message": "Medicine retrieved",
            "data": {
                "medid": medicine.med_id,
                "medicine_name": medicine.medicine_name,
                "price": float(medicine.price),
                "category":medicine.category,
                "quantity": medicine.quantity,
                "total": float(medicine.total)
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
        
        
@router.delete("/deleteaddress")
def delete_address(address: DeleteAddressRequest,current_user=Depends(get_current_user),db: Session = Depends(get_db)):
    try:
        entry = (
            db.query(Address)
            .filter(
                Address.addressid == address.addressid,
                Address.usr_id == address.userid).first())
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found"
            )
        db.delete(entry)
        db.commit()
        return {
            "status": 200,
            "detail": "Address deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )