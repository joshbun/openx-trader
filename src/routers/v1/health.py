from fastapi import APIRouter
from fastapi.responses import JSONResponse

HealthRouter = APIRouter()


@HealthRouter.get("/health")
async def health_check():
    return JSONResponse(
        content={
            "is_success": True,
            "status": 200,
            "data": "Service is running smoothly",
        }
    )


@HealthRouter.get("/healthz")
async def healthz_check():
    return JSONResponse(
        content={"is_success": True, "status": 200, "data": "Service is healthy"}
    )


@HealthRouter.get("/ping")
async def ping():
    return JSONResponse(content={"is_success": True, "status": 200, "data": "pong"})
