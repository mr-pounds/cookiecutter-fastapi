from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

from app.common.response.response_code import CustomResponse, CustomResponseCode

SchemaT = TypeVar("SchemaT")


class ResponseBaseModel(BaseModel):
    """
    不包含返回数据 schema 的通用型统一返回模型

    示例::

        @router.get('/test', response_model=ResponseModel)
        def test():
            return ResponseModel(data={'test': 'test'})


        @router.get('/test')
        def test() -> ResponseModel:
            return ResponseModel(data={'test': 'test'})


        @router.get('/test')
        def test() -> ResponseModel:
            res = CustomResponseCode.HTTP_200
            return ResponseModel(code=res.code, msg=res.msg, data={'test': 'test'})
    """

    success: bool = Field(True, description="返回数据")
    code: int = Field(CustomResponseCode.HTTP_200.code, description="返回状态码")
    msg: str = Field(CustomResponseCode.HTTP_200.msg, description="返回信息")
    data: Any | None = Field(None, description="返回数据")


class ListSchema(BaseModel, Generic[SchemaT]):
    list: list[SchemaT]
    total: int


class ResponseSchema(ResponseBaseModel, Generic[SchemaT]):
    """
    包含返回数据 schema 的通用型统一返回模型

    示例::

        @router.get('/test', response_model=ResponseSchemaModel[GetApiDetail])
        def test():
            return ResponseSchemaModel[GetApiDetail](data=GetApiDetail(...))


        @router.get('/test')
        def test() -> ResponseSchemaModel[GetApiDetail]:
            return ResponseSchemaModel[GetApiDetail](data=GetApiDetail(...))


        @router.get('/test')
        def test() -> ResponseSchemaModel[GetApiDetail]:
            res = CustomResponseCode.HTTP_200
            return ResponseSchemaModel[GetApiDetail](code=res.code, msg=res.msg, data=GetApiDetail(...))
    """

    data: SchemaT


class ListResponseSchema(ResponseBaseModel, Generic[SchemaT]):
    """
    包含返回数据 schema 的通用型统一返回模型
    """

    data: ListSchema[SchemaT]


class ResponseBase:
    """统一返回方法"""

    @staticmethod
    def __response(
        *,
        res: CustomResponseCode | CustomResponse,
        success: bool,
        data: Any | None,
    ) -> ResponseBaseModel | ResponseSchema:
        """
        请求返回通用方法

        :param res: 返回信息
        :param data: 返回数据
        :return:
        """
        return ResponseBaseModel(code=res.code, msg=res.msg, success=success, data=data)

    def success(
        self,
        *,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_200,
        data: Any | None = None,
    ) -> ResponseBaseModel | ResponseSchema:
        """
        成功响应

        :param res: 返回信息
        :param data: 返回数据
        :return:
        """
        return self.__response(res=res, success=True, data=data)

    def fail(
        self,
        *,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_400,
        data: Any = None,
    ) -> ResponseBaseModel | ResponseSchema:
        """
        失败响应

        :param res: 返回信息
        :param data: 返回数据
        :return:
        """
        return self.__response(res=res, success=False, data=data)


response_base: ResponseBase = ResponseBase()
