from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException
from uvicorn.protocols.http.h11_impl import STATUS_PHRASES

from app.common.config import settings
from app.common.exception.errors import BaseExceptionError
from app.common.exception.pydantic_error import PYDANTIC_VALIDATION_ERROR_MESSAGES
from app.common.response.response_code import CustomResponseCode
from app.common.response.response_schema import response_base


def _get_exception_code(status_code: int) -> int:
    """
    获取返回状态码（可用状态码基于 RFC 定义）

    `python 状态码标准支持 <https://github.com/python/cpython/blob/6e3cc72afeaee2532b4327776501eb8234ac787b/Lib/http/__init__.py#L7>`__

    `IANA 状态码注册表 <https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml>`__

    :param status_code: HTTP 状态码
    :return:
    """
    try:
        STATUS_PHRASES[status_code]
    except Exception:
        return status.HTTP_400_BAD_REQUEST

    return status_code


async def _validation_exception_handler(exc: RequestValidationError | ValidationError):
    """
    数据验证异常处理

    :param exc: 验证异常
    :return:
    """
    errors = []
    for error in exc.errors():
        if error["type"] not in PYDANTIC_VALIDATION_ERROR_MESSAGES:
            continue
        custom_message = PYDANTIC_VALIDATION_ERROR_MESSAGES[error["type"]]
        if custom_message:
            error_ctx = error.get("ctx")
            if not error_ctx:
                error["msg"] = custom_message
            else:
                e = error_ctx.get("error")
                if e:
                    error["msg"] = custom_message.format(**error_ctx)
                    error["ctx"]["error"] = (
                        e.__str__().replace("'", '"')
                        if isinstance(e, Exception)
                        else None
                    )
        errors.append(error)
    error = errors[0]
    if error.get("type") == "json_invalid":
        message = "json解析失败"
    else:
        error_input = error.get("input")
        field = str(error.get("loc")[-1])
        error_msg = error.get("msg")
        message = (
            f"{field} {error_msg}，输入：{error_input}"
            if settings.ENVIRONMENT == "dev"
            else error_msg
        )
    msg = f"请求参数非法: {message}"
    data = {"errors": errors} if settings.ENVIRONMENT == "dev" else None
    content = {
        "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "msg": msg,
        "data": data,
        "success": False,
    }
    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


def register_exception(app: FastAPI) -> None:  # noqa: C901
    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException):
        """
        全局 HTTP 异常处理

        :param request: FastAPI 请求对象
        :param exc: HTTP 异常
        :return:
        """
        content = {
            "code": exc.status_code,
            "msg": exc.detail,
            "data": None,
            "success": False,
        }
        return JSONResponse(
            status_code=_get_exception_code(exc.status_code),
            content=content,
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def fastapi_validation_exception_handler(
        _: Request, exc: RequestValidationError
    ):
        """
        FastAPI 数据验证异常处理

        :param request: FastAPI 请求对象
        :param exc: 验证异常
        :return:
        """
        return await _validation_exception_handler(exc)

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(_: Request, exc: ValidationError):
        """
        Pydantic 数据验证异常处理

        :param request: 请求对象
        :param exc: 验证异常
        :return:
        """
        return await _validation_exception_handler(exc)

    @app.exception_handler(AssertionError)
    async def assertion_error_handler(_: Request, exc: AssertionError):
        """
        断言错误处理

        :param request: FastAPI 请求对象
        :param exc: 断言错误
        :return:
        """
        if settings.ENVIRONMENT == "dev":
            content = {
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "msg": str("".join(exc.args) if exc.args else exc.__doc__),
                "data": None,
                "success": False,
            }
        else:
            res = response_base.fail(res=CustomResponseCode.HTTP_500)
            content = res.model_dump()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=content,
        )

    @app.exception_handler(BaseExceptionError)
    async def custom_exception_handler(_: Request, exc: BaseExceptionError):
        """
        全局自定义异常处理

        :param request: FastAPI 请求对象
        :param exc: 自定义异常
        :return:
        """
        content = {
            "code": exc.code,
            "msg": str(exc.msg),
            "data": exc.data or None,
            "success": False,
        }
        return JSONResponse(
            status_code=_get_exception_code(exc.code),
            content=content,
        )

    @app.exception_handler(Exception)
    async def all_unknown_exception_handler(_: Request, exc: Exception):
        """
        全局未知异常处理

        :param request: FastAPI 请求对象
        :param exc: 未知异常
        :return:
        """
        if settings.ENVIRONMENT == "dev":
            content = {
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "msg": str(exc),
                "data": None,
                "success": False,
            }
        else:
            res = response_base.fail(res=CustomResponseCode.HTTP_500)
            content = res.model_dump()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=content,
        )
