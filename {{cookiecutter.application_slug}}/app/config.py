"""
Description  : 
Version      : 1.0.1
Author       : zzz
Date         : 2025-09-13 12:33:26
LastEditors  : zzz
LastEditTime : 2025-09-13 14:54:30
"""
from typing import Annotated, Any, Literal

from pydantic import AnyUrl, BeforeValidator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env.dev",
        env_ignore_empty=True,
        extra="ignore",
    )
    
    APPLICATION_CODE: str = ""
    APPLICATION_NAME: str = ""

    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS]

    DATABASE_TYPE: Literal["postgres", "mysql", None] = "sqlite3"
    POSTGRES_SERVER: str = ""
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""
    MYSQL_SERVER: str = ""
    MYSQL_PORT: int = 8066
    MYSQL_DB: str = ""
    MYSQL_USER: str = ""
    MYSQL_PASSWORD: str = ""

    ERROR_CODE_PREFIX_AA: str = ""
    ERROR_CODE_PREFIX_BB: str = ""



settings = Settings()  # type: ignore
