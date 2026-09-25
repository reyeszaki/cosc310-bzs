from fastapi import FastAPI
from app.routers import restaurants

app = FastAPI(title="COSC 310 Food Delivery API")

app.include_router(restaurants.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}