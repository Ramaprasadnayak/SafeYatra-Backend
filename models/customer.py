from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from config.db import Base

class Customer(Base):
    __tablename__ = "customers"

    usr_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    phone = Column(String(15), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())