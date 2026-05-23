from fastapi import APIRouter, HTTPException

from src.core.config import get_config
from src.clients.mobee.main import MobeeOpenApi

WalletsRouter = APIRouter(prefix="/wallets")


def _build_mobee_client() -> MobeeOpenApi:
    cfg = get_config().external.mobee
    return MobeeOpenApi(API_KEY=cfg.api_key, API_SECRET=cfg.secret_key)


@WalletsRouter.get("/balance/{currency}")
async def get_balance(currency: str):
    client = _build_mobee_client()
    try:
        return client.get_balance(currency)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
