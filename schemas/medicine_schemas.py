from pydantic import BaseModel, ConfigDict
from decimal import Decimal

class MedicineResponse(BaseModel):
    med_id: int
    medicine_name: str
    category: str
    price: Decimal
    stock: bool
    image_url: str | None

    model_config = ConfigDict(from_attributes=True)

class CategoryResponse(BaseModel):
    status: int
    message: str
    data: list[MedicineResponse]