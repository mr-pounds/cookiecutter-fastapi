"""
Name         :
Description  :
Version      : 1.0.1
Author       : zzz
Date         : 2025-05-28 15:08:51
LastEditors  : zzz
LastEditTime : 2025-09-13 15:11:50
"""

from fastapi import APIRouter
from sqlmodel import select

from app.demo.models import SqlModelDemo1
from app.deps import SessionDep
from app.response import ListDataModel, ListResponseModel

router = APIRouter(prefix="/demo", tags=["demo"])

@router.get("/demo")
def api_demo(
    session: SessionDep
) -> ListResponseModel[SqlModelDemo1]:
    statement = select(SqlModelDemo1).where(SqlModelDemo1.industry_name == "demo")
    results = session.exec(statement).all()
    return ListResponseModel(
        data=ListDataModel(
            list=results,
            total=len(results),
        )
    )
