from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # Read EIA_API_KEY from the process environment. The MCP entry point does
    # not auto-load .env; SecretStr masks normal representations of the value.
    model_config = SettingsConfigDict(extra="ignore")
    eia_api_key: SecretStr = SecretStr("")


# Settings are captured at import time. Launchers must configure the environment
# before importing the service/client modules.
settings = Settings()
