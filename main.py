import argparse
import sys
import uvicorn
from fastapi import FastAPI

from src.core.config import get_config
from src.core.log_config import setup_logging
from src.clients.mobee.main import MobeeOpenApi
from src.routers.main import MainRouter
from src.utils.logger import set_logger

setup_logging()
logger = set_logger(__file__)

app = FastAPI(title="OpenX Trader")
app.include_router(MainRouter)


def _build_mobee_client() -> MobeeOpenApi:
    cfg = get_config().external.mobee
    return MobeeOpenApi(API_KEY=cfg.api_key, API_SECRET=cfg.secret_key)


# --- CLI ---


def cli_balance(args: argparse.Namespace):
    client = _build_mobee_client()
    result = client.get_balance(args.currency)
    print(result)


def cli_order(args: argparse.Namespace):
    client = _build_mobee_client()
    result = client.create_new_order(
        side=args.side,
        market=args.market,
        trade=args.trade,
        type=args.type,
        volume=args.volume,
    )
    print(result.json())


def cli_serve(args: argparse.Namespace):
    uvicorn.run("main:app", host=args.host, port=args.port, reload=args.reload)


def main():
    parser = argparse.ArgumentParser(description="OpenX Trader")
    sub = parser.add_subparsers(dest="command")

    serve_p = sub.add_parser("serve", help="Start the FastAPI server")
    serve_p.add_argument("--host", default="0.0.0.0")
    serve_p.add_argument("--port", type=int, default=8000)
    serve_p.add_argument("--reload", action="store_true")

    bal_p = sub.add_parser("balance", help="Check wallet balance")
    bal_p.add_argument("currency", help="Currency code (e.g. BTC, USDT)")

    ord_p = sub.add_parser("order", help="Create a new order")
    ord_p.add_argument("--side", required=True, choices=["buy", "sell"])
    ord_p.add_argument("--market", required=True)
    ord_p.add_argument("--trade", required=True)
    ord_p.add_argument("--type", required=True)
    ord_p.add_argument("--volume", required=True, type=float)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    handlers = {
        "serve": cli_serve,
        "balance": cli_balance,
        "order": cli_order,
    }
    handlers[args.command](args)


if __name__ == "__main__":
    main()
