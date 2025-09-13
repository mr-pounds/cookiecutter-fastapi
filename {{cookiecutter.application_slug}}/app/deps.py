"""
Name         :
Description  :
Version      : 1.0.1
Author       : zzz
Date         : 2025-04-28 19:35:21
LastEditors  : zzz
LastEditTime : 2025-06-19 10:27:04
"""

from collections.abc import Generator
from typing import Annotated

from app.db import engine
from fastapi import Depends
from sqlmodel import Session


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
