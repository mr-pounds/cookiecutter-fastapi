"""
应用配置模块

该模块定义了应用的所有配置项，包括应用信息、数据库连接、Redis连接、
跨域配置和错误码前缀等配置。使用 Pydantic Settings 进行配置管理，
支持从环境变量和 .env 文件读取配置。

Example:
    >>> from app.common.config import settings
    >>> print(settings.APPLICATION_NAME)
    'My Application'
"""

from typing import Annotated, Any, Literal

from pydantic import AnyUrl, BeforeValidator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str]:
    """
    解析 CORS 配置值

    将字符串格式的 CORS 配置转换为列表，支持逗号分隔的字符串格式和列表格式的输入。

    Args:
        v: CORS 配置值，可以是字符串或列表

    Returns:
        解析后的 CORS 源列表

    Raises:
        ValueError: 当输入格式不正确时
    """
    if isinstance(v, str):
        if v.startswith("[") and v.endswith("]"):
            # 尝试解析JSON格式的字符串
            import json

            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # 如果解析失败，将其视为普通字符串
                return [v.strip()]
        # 处理逗号分隔的字符串
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list):
        return v
    raise ValueError(f"无效的CORS配置格式: {v}")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env.dev",
        env_ignore_empty=True,
        extra="ignore",
    )

    # 应用信息配置
    APPLICATION_CODE: str = ""
    APPLICATION_NAME: str = ""

    # API版本控制
    API_VERSION_STR: str = "/api/v1"

    # 环境配置
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    # CORS配置
    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field
    @property
    def all_cors_origins(self) -> list[str]:
        """
        获取所有 CORS 源的字符串列表

        将 CORS 配置转换为去除末尾斜杠的字符串列表，
        便于在响应头中使用。

        Returns:
            CORS 源字符串列表
        """
        cors_origins = self.BACKEND_CORS_ORIGINS
        result: list[str] = []

        if isinstance(cors_origins, list):
            for origin in cors_origins:
                result.append(str(origin).rstrip("/"))
        elif isinstance(cors_origins, str):
            # 处理字符串类型的情况（虽然parse_cors应该返回列表）
            result.append(cors_origins.rstrip("/"))

        return result

    # 数据库配置
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_ECHO: bool = False
    DATABASE_POOL_ECHO: bool = False

    # Redis配置
    PYTHON_REDIS_HOST: str
    PYTHON_REDIS_PORT: int
    PYTHON_REDIS_PASSWORD: str
    PYTHON_REDIS_DATABASE: int
    PYTHON_REDIS_TIMEOUT: int

    # 错误码配置
    ERROR_CODE_PREFIX_AA: str = ""
    ERROR_CODE_PREFIX_BB: str = ""

    # 短信服务配置
    SMS_API_URL: str = ""
    SMS_TEMPLATE_CODE: str = ""

    # 验证码配置
    VERIFICATION_CODE_LENGTH: int = 6
    VERIFICATION_CODE_EXPIRE_MINUTES: int = 6
    VERIFICATION_CODE_INTERVAL_MINUTES: int = 5

    # Token 配置
    TOKEN_EXPIRE_DAYS: int = 2

    # 日志（文件）
    LOG_ACCESS_FILENAME: str
    LOG_ERROR_FILENAME: str


# 全局配置实例
# 在应用启动时加载，贯穿整个应用生命周期
settings = Settings()  # type: ignore
