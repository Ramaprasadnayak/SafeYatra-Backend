from fastapi import FastAPI
from routers import translate

app = FastAPI(
    title="SafeYatra API",
    version="1.0.0"
)

# routers
app.include_router(translate.router)


# Testing endpoint
@app.get("/")
def root():
    return {
        "message": "SafeYatra API is running"
    }