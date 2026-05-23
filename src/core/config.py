from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
from pydantic import BaseModel, Field, ValidationError
import yaml
from src.utils.logger import set_logger

logger = set_logger(__file__)


class ExchangeConfig(BaseModel):
    base_url: str = Field(..., alias="BaseUrl")
    api_key: str = Field(..., alias="ApiKey")
    secret_key: str = Field(..., alias="SecretKey")


class InternalConfig(BaseModel):
    app_name: str = Field(..., alias="AppName")


class ExternalConfig(BaseModel):
    mobee: ExchangeConfig = Field(..., alias="Mobee")


class Config(BaseModel):
    internal: InternalConfig = Field(..., alias="InternalConfig")
    external: ExternalConfig = Field(..., alias="ExternalConfig")

    @classmethod
    def load_from_file(cls, yaml_path: Path = Path("src/core/config.yaml")) -> Config:
        if not yaml_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {yaml_path}")

        with open(yaml_path, "r") as f:
            data: Dict[str, Any] = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {yaml_path}")

        try:
            return cls.model_validate(data)
        except ValidationError as e:
            logger.error(e.json(indent=2))
            raise


_config: Config | None = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config.load_from_file()
    return _config
