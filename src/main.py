from fastapi import FastAPI
from .routers.main import MainRouter


app = FastAPI(
    title="OpenX Trader API",
    description="API for OpenX Trader, a trading platform",
    version="1.0.0",
)
app.include_router(MainRouter)
