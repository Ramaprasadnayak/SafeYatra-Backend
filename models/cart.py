from sqlalchemy import Column,Integer,ForeignKey
from config.db import Base
class Cart(Base):
    __tablename__ = "cart"
    cart_id = Column(Integer, primary_key=True, index=True)
    usr_id = Column(Integer, ForeignKey("customers.usr_id"), nullable=False)
    med_id=Column(Integer,ForeignKey("medicines.med_id"),nullable=False)
    quantity = Column(Integer, nullable=False)