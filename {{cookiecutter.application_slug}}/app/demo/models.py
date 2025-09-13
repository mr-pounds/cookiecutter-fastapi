"""
Name         :
Description  :
Version      : 1.0.1
Author       : zzz
Date         : 2025-05-28 15:20:03
LastEditors  : zzz
LastEditTime : 2025-09-13 14:57:12
"""

from datetime import datetime

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel


class PydanticModelDemo(BaseModel):
    industryCode: str
    industryName: str
    productCategoryCode: str
    productCategoryName: str
    similarity: float



class SqlModelDemo1(SQLModel, table=True):
    __tablename__ = "demo1_table_name"

    rowid: int | None = Field(default=None, primary_key=True)
    id: str = Field(nullable=False)
    industry_name: str = Field(nullable=False)
    create_time: datetime = Field(default_factory=datetime.now)
    update_time: datetime = Field(default_factory=datetime.now)
    products: list["SqlModelDemo2"] = Relationship(back_populates="industry")


class SqlModelDemo2(SQLModel, table=True):
    __tablename__ = "demo2_table_name"

    rowid: int | None = Field(default=None, primary_key=True)
    id: str = Field(nullable=False)
    product_name: str = Field(nullable=False)
    industry: SqlModelDemo1 = Relationship(back_populates="products")
    create_time: datetime = Field(default_factory=datetime.now)
    update_time: datetime = Field(default_factory=datetime.now)


