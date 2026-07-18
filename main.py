from fastapi import FastAPI
from config.db import Base, engine
# Import routers and Search medicine 
from routers import auth,search_medicine,cart,order,refresh
app = FastAPI(
    title="Maruthi Medical API",
    version="1.0.0"
)

# Create database tables (if they don't already exist)
Base.metadata.create_all(bind=engine)

# routers
app.include_router(auth.router)
app.include_router(search_medicine.router)
app.include_router(cart.router)
app.include_router(order.router)
app.include_router(refresh.router)

# Testing endpoint
@app.get("/")
def root():
    return {
        "message": "Maruthi Medical API is running"
    }