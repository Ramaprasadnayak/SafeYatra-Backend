# validate incomming raw json
from pydantic import BaseModel


class AddressRequest(BaseModel):
    userid:int
    address: str

class DeleteAddressRequest(BaseModel):
    userid:int
    addressid: int

