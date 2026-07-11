from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config.setting import (DB_HOST,DB_NAME,DB_PASSWORD,DB_PORT,DB_USER)
from urllib.parse import quote_plus
encoded_password = quote_plus(DB_PASSWORD)

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL,pool_pre_ping=True)


# a temporary connection between FastAPI server and MySQL like a waiter.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# it connects every table model which i define i.e every class must inherit it
Base = declarative_base()

# It's usually called inside route functions using Depends()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()