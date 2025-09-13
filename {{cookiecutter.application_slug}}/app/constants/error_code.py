from dataclasses import dataclass

from app.config import settings


@dataclass
class ErrorCode:
    code: str
    message: str

    def __init__(self, code: str, message: str):
        self.code = f"{settings.ERROR_CODE_PREFIX_AA}{settings.ERROR_CODE_PREFIX_BB}{code}"
        self.message = message


HTTP_200_OK = ErrorCode("200", "请求成功")
HTTP_201_CREATED = ErrorCode("201", "已创建")
HTTP_204_NO_CONTENT = ErrorCode("204", "无内容")
HTTP_400_BAD_REQUEST = ErrorCode("400", "请求错误")
HTTP_401_UNAUTHORIZED = ErrorCode("401", "未授权")
HTTP_403_FORBIDDEN = ErrorCode("403", "禁止访问")
HTTP_404_NOT_FOUND = ErrorCode("404", "未找到资源")
HTTP_405_METHOD_NOT_ALLOWED = ErrorCode("405", "不允许的方法")
HTTP_406_NOT_ACCEPTABLE = ErrorCode("406", "不可接受")
HTTP_409_CONFLICT = ErrorCode("409", "冲突")
HTTP_422_UNPROCESSABLE_ENTITY = ErrorCode("422", "不可处理的实体")
HTTP_500_INTERNAL_SERVER_ERROR = ErrorCode("500", "服务器内部错误")
HTTP_502_BAD_GATEWAY = ErrorCode("502", "网关错误")
HTTP_503_SERVICE_UNAVAILABLE = ErrorCode("503", "服务不可用")