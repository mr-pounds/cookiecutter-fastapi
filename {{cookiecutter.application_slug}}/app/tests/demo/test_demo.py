"""
Description  : 
Version      : 1.0.1
Author       : zzz
Date         : 2025-09-13 13:50:01
LastEditors  : zzz
LastEditTime : 2025-09-13 13:53:19
"""
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.demo.models import SqlModelDemo1
from app.config import settings


def test_get_invoice_list(client: TestClient, session: Session) -> None:
    response = client.get(f"{settings.API_V1_STR}/demo")
    assert response.status_code == 200
    statement = select(SqlModelDemo1).where(SqlModelDemo1.industry_name == "demo")
    data_from_db = session.exec(statement).all()
    data = response.json()
    assert data["data"]["list"] == data_from_db
    