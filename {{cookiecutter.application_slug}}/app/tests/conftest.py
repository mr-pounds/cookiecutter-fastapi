"""
Name         :
Description  :
Version      : 1.0.1
Author       : zzz
Date         : 2025-04-30 16:30:22
LastEditors  : zzz
LastEditTime : 2025-09-13 13:48:30
"""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.db import engine
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c

