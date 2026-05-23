from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.core.config import get_config
from src.clients.mobee.main import MobeeOpenApi

OrdersRouter = APIRouter(prefix="/orders")


def _build_mobee_client() -> MobeeOpenApi:
    cfg = get_config().external.mobee
    return MobeeOpenApi(API_KEY=cfg.api_key, API_SECRET=cfg.secret_key)


class CreateOrderRequest(BaseModel):
    side: str
    market: str
    trade: str
    type: str
    volume: float


@OrdersRouter.post("")
async def create_order(req: CreateOrderRequest):
    client = _build_mobee_client()
    try:
        res = client.create_new_order(
            side=req.side,
            market=req.market,
            trade=req.trade,
            type=req.type,
            volume=req.volume,
        )
        return res.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
