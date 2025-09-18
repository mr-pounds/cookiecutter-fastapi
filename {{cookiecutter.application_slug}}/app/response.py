"""
Name         : 定义基本的响应模型
Version      : 1.0.1
Author       : zzz
Date         : 2022-10-22 09:30:44
LastEditors  : zzz
LastEditTime : 2025-09-18 10:17:34
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

from app.constants import error_code

DataType = TypeVar("DataType")


class ResponseModel(BaseModel, Generic[DataType]):
    success: bool = True
    code: str = error_code.HTTP_200_OK.code
    msg: str = error_code.HTTP_200_OK.message
    data: DataType


class ListDataModel(BaseModel, Generic[DataType]):
    list: list[DataType]
    total: int


class ListResponseModel(BaseModel, Generic[DataType]):
    success: bool = True
    code: str = error_code.HTTP_200_OK.code
    msg: str = error_code.HTTP_200_OK.message
    data: ListDataModel[DataType]
