from pathlib import Path

from fastapi import FastAPI, status
from fastapi.staticfiles import StaticFiles

from app.api.routers import menu_routers, restaurant_routers

app = FastAPI(
    title="COSC 310 Food Delivery API",
    description="Milestone 1 vertical slice for restaurant discovery, restaurant management, and menu management.",
    version="1.0.0",
)

app.include_router(restaurant_routers.router)
app.include_router(menu_routers.router)


@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    tags=["health"],
    summary="Health check",
    description="Verify that the API service is running and responsive.",
)
def health_check() -> dict[str, str]:
    return {"status": "ok"}

app.mount("/", StaticFiles(directory=Path(__file__).resolve().parents[1] / "static", html=True), name="static")
