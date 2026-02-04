import dataclasses
from enum import Enum


class CustomCodeBase(Enum):
    """自定义状态码基类"""

    @property
    def code(self) -> int:
        """获取状态码"""
        return self.value[0]

    @property
    def msg(self) -> str:
        """获取状态码信息"""
        return self.value[1]


class CustomResponseCode(CustomCodeBase):
    """自定义响应状态码"""

    HTTP_200 = (200, "请求成功")
    HTTP_400 = (400, "请求错误")
    HTTP_500 = (500, "服务器内部错误")


class CustomErrorCode(CustomCodeBase):
    """自定义错误状态码"""

    CAPTCHA_ERROR = (30001, "验证码错误")
    USER_NOT_FOUND_ERROR = (30001, "用户不存在或已删除")
    INVALID_PHONE_NUMBER_ERROR = (30002, "手机号格式不正确")
    SMS_SERVICE_ERROR = (30003, "短信服务调用失败")

    AGENT_SESSION_ERROR = (40010, "会话不存在或已删除")
    AGENT_SESSION_QUOTA_ERROR = (40011, "会话额度为零，无法创建会话")
    AGENT_CHAT_QUOTA_ERROR = (40012, "对话次数已不足，无法继续对话")


@dataclasses.dataclass
class CustomResponse:
    """
    提供开放式响应状态码，而不是枚举，如果你想自定义响应信息，这可能很有用
    """

    code: int
    msg: str
