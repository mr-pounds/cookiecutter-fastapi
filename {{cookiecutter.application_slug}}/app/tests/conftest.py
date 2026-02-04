"""
测试配置文件

提供测试所需的 fixtures 和配置
"""

import uuid
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database.db import sync_db_session
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    with sync_db_session() as session:
        yield session


@pytest.fixture(scope="function", autouse=True)
def uid() -> str:
    return uuid.uuid4().hex[:2]


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c
