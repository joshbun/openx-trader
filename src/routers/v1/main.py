from fastapi import APIRouter
from .health import HealthRouter
from .wallets import WalletsRouter
from .orders import OrdersRouter

V1Router = APIRouter()
V1Router.include_router(HealthRouter, tags=["Health"])
V1Router.include_router(WalletsRouter, tags=["Wallets"])
V1Router.include_router(OrdersRouter, tags=["Orders"])
