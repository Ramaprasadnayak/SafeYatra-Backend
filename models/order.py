from sqlalchemy import Column,Integer,ForeignKey,String
from config.db import Base
class Address(Base):
    __tablename__ = "address"
    addressid = Column(Integer, primary_key=True, index=True)
    usr_id = Column(Integer, ForeignKey("customers.usr_id"), nullable=False)
    address=Column(String,default="No address saved yet.",nullable=False)