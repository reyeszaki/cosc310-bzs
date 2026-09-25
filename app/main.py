from fastapi import FastAPI

from app.api.routers import restaurant_routers

app = FastAPI(title="COSC 310 Food Delivery API")

app.include_router(restaurant_routers.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}