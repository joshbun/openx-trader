from fastapi import APIRouter
from .v1.main import V1Router

MainRouter = APIRouter()
MainRouter.include_router(V1Router, prefix="/v1")


@MainRouter.get("/", include_in_schema=False)
async def read_root():
    return {"message": "Welcome to the OpenX Trader API"}
