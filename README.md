# OpenX Trader

Personal trading bot and API server for crypto exchange integrations.

## Requirements

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/) package manager

## Setup

1. Install dependencies:

```bash
uv sync
```

2. Copy the example config and fill in your credentials:

```bash
cp src/core/example.config.yaml src/core/config.yaml
```

Edit `src/core/config.yaml` with your exchange API keys:

```yaml
InternalConfig:
  AppName: "OpenX Trader"

ExternalConfig:
  Mobee:
    BaseUrl: "https://api.mobee.com"
    ApiKey: "your-api-key"
    SecretKey: "your-secret-key"
```

## Usage

### API Server

```bash
uv run python main.py serve
uv run python main.py serve --port 3000 --reload
```

API docs available at `http://localhost:8000/docs` after starting the server.

### API Endpoints

| Method | Path                            | Description          |
|--------|---------------------------------|----------------------|
| GET    | `/`                             | Welcome message      |
| GET    | `/v1/health`                    | Health check         |
| GET    | `/v1/wallets/balance/{currency}`| Get wallet balance   |
| POST   | `/v1/orders`                    | Create a new order   |

### CLI

Check wallet balance:

```bash
uv run python main.py balance BTC
```

Create an order:

```bash
uv run python main.py order --side buy --market BTC --trade USDT --type limit --volume 0.5
```

## Project Structure

```
main.py                     # Entrypoint (FastAPI app + CLI)
src/
  core/
    config.py               # YAML config loader (Pydantic)
    log_config.py           # Structured JSON logging
    example.config.yaml     # Config template
  clients/
    mobee/
      main.py               # Mobee exchange API client
  routers/
    main.py                 # Root router
    v1/
      health.py             # Health check endpoints
      wallets.py            # Wallet endpoints
      orders.py             # Order endpoints
  utils/
    logger.py               # Logger helper
```
