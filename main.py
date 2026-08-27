from fastapi import FastAPI
from routers import translate , geocode

app = FastAPI(
    title="SafeYatra API",
    version="1.0.0"
)

app.include_router(translate.router)
app.include_router(geocode.router)



@app.get("/")
def root():
    return {
        "message": "SafeYatra API is running"
    }