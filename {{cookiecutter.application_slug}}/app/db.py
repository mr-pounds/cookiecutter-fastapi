"""
Name         :
Description  :
Version      : 1.0.1
Author       : zzz
Date         : 2025-04-28 19:35:21
LastEditors  : zzz
LastEditTime : 2025-09-18 10:17:14
"""

from sqlalchemy.engine import URL
from sqlmodel import create_engine

from app.config import settings

match settings.DATABASE_TYPE:
    case "postgres":
        engine = create_engine(
            URL.create(
                "postgresql+psycopg",
                username=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                host=settings.POSTGRES_SERVER,
                port=settings.POSTGRES_PORT,
                database=settings.POSTGRES_DB,
            )
        )
    case "mysql":
        engine = create_engine(
            URL.create(
                "mysql+pymysql",
                username=settings.MYSQL_USER,
                password=settings.MYSQL_PASSWORD,
                host=settings.MYSQL_SERVER,
                port=settings.MYSQL_PORT,
                database=settings.MYSQL_DB,
            ),
        )
    case _:
        raise ValueError(f"Unknown database type: {settings.DATABASE_TYPE}")
