from sqlalchemy import Column,String,Integer,Boolean,DECIMAL
from config.db import Base
class Medicine(Base):
    __tablename__ = "medicines"

    med_id = Column(Integer, primary_key=True, index=True)
    medicine_name = Column(String(255), nullable=False)
    category=Column(String(255),nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    stock = Column(Boolean, default=True)
    sales = Column(Integer,nullable=False,default=0)
    image_url = Column(String(255))  