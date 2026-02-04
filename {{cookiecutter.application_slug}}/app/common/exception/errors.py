from typing import Any

from fastapi import HTTPException, status

from app.common.response.response_code import CustomErrorCode


class BaseExceptionError(Exception):
    """基础异常混入类"""

    code: int

    def __init__(
        self, *, msg: str | None = None, data: Any = None, success: bool = False
    ) -> None:
        self.msg = msg
        self.data = data


class HTTPError(HTTPException):
    """HTTP 异常"""

    def __init__(
        self, *, code: int, msg: Any = None, headers: dict[str, Any] | None = None
    ) -> None:
        super().__init__(status_code=code, detail=msg, headers=headers)


class CustomError(BaseExceptionError):
    """自定义异常"""

    def __init__(
        self,
        *,
        error: CustomErrorCode,
        data: Any = None,
    ) -> None:
        self.code = error.code
        super().__init__(msg=error.msg, data=data)


class RequestError(BaseExceptionError):
    """请求异常"""

    def __init__(
        self,
        *,
        code: int = status.HTTP_400_BAD_REQUEST,
        msg: str = "Bad Request",
        data: Any = None,
    ) -> None:
        self.code = code
        super().__init__(msg=msg, data=data)


class ForbiddenError(BaseExceptionError):
    """禁止访问异常"""

    code = status.HTTP_403_FORBIDDEN

    def __init__(
        self,
        *,
        msg: str = "Forbidden",
        data: Any = None,
    ) -> None:
        super().__init__(msg=msg, data=data)


class NotFoundError(BaseExceptionError):
    """资源不存在异常"""

    code = status.HTTP_404_NOT_FOUND

    def __init__(
        self,
        *,
        msg: str = "资源不存在",
        data: Any = None,
    ) -> None:
        super().__init__(msg=msg, data=data)


class ServerError(BaseExceptionError):
    """服务器异常"""

    code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self,
        *,
        msg: str = "Internal Server Error",
        data: Any = None,
    ) -> None:
        super().__init__(msg=msg, data=data)


class GatewayError(BaseExceptionError):
    """网关异常"""

    code = status.HTTP_502_BAD_GATEWAY

    def __init__(
        self,
        *,
        msg: str = "Bad Gateway",
        data: Any = None,
    ) -> None:
        super().__init__(msg=msg, data=data)


class AuthorizationError(BaseExceptionError):
    """授权异常"""

    code = status.HTTP_403_FORBIDDEN

    def __init__(
        self,
        *,
        msg: str = "Permission Denied",
        data: Any = None,
    ) -> None:
        super().__init__(msg=msg, data=data)


class TokenError(HTTPError):
    """Token 异常"""

    code = status.HTTP_401_UNAUTHORIZED

    def __init__(
        self, *, msg: str = "未认证", headers: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            code=self.code, msg=msg, headers=headers or {"WWW-Authenticate": "Bearer"}
        )


class ConflictError(BaseExceptionError):
    """资源冲突异常"""

    code = status.HTTP_409_CONFLICT

    def __init__(
        self,
        *,
        msg: str = "Conflict",
        data: Any = None,
    ) -> None:
        super().__init__(msg=msg, data=data)


class VerificationCodeIntervalError(BaseExceptionError):
    """验证码发送间隔限制"""

    code = status.HTTP_403_FORBIDDEN

    def __init__(
        self,
        *,
        remaining_seconds: int,
        msg: str | None = None,
        data: Any = None,
    ) -> None:
        if msg is None:
            msg = f"请等待{remaining_seconds}秒后重试"
        super().__init__(msg=msg, data=data)


class SMSServiceError(BaseExceptionError):
    """SMS服务市场"""

    code = status.HTTP_409_CONFLICT

    def __init__(
        self,
        *,
        remaining_seconds: int,
        msg: str | None = None,
        data: Any = None,
    ) -> None:
        if msg is None:
            msg = f"请等待{remaining_seconds}秒后重试"
        super().__init__(msg=msg, data=data)
