from fastapi import APIRouter

from app.api.healthz.schemas import HealthResponse

health_router = APIRouter(tags=["healthz"])


@health_router.get("/healthz", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
    )