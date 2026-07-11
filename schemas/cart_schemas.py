# validate incomming raw json
from pydantic import BaseModel


class CartRequest(BaseModel):
    usrid: int
    medid: int

class CartQuantityRequest(BaseModel):
    usrid: int
    medid: int
    action: int
