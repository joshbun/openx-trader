from fastapi import APIRouter
from .health import HealthRouter

V1Router = APIRouter()
V1Router.include_router(HealthRouter, tags=["Health"])
