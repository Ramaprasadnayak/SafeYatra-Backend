from fastapi import FastAPI
from routers import translate, geocode, auth, district_boundary
import config.firebase

app = FastAPI(
    title="SafeYatra API",
    version="1.0.0"
)

app.include_router(translate.router)
app.include_router(geocode.router)
app.include_router(auth.router)
app.include_router(district_boundary.router)


@app.get("/")
def root():
    return {
        "message": "SafeYatra API is running"
    }