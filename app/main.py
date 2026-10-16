from fastapi import FastAPI

from app.api.routers import menu_routers, restaurant_routers

app = FastAPI(title="COSC 310 Food Delivery API")

app.include_router(restaurant_routers.router)
app.include_router(menu_routers.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}