"""
认证模块Schema

提供用户认证相关的请求和响应数据结构定义。
包括登录请求、Token响应、服务层数据模型等。
"""

from datetime import datetime

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """登录请求数据模型

    用于用户登录时提交手机号和验证码。

    Attributes:
        phone: 手机号码（中国大陆格式，11位以1开头的数字）
        verification_code: 6位数字验证码
    """

    phone: str = Field(
        ...,
        description="手机号码",
        min_length=11,
        max_length=11,
        examples=["13800138000"],
    )
    verification_code: str = Field(
        ...,
        description="6位数字验证码",
        min_length=6,
        max_length=6,
        examples=["888888"],
    )


class LoginResponse(BaseModel):
    """登录响应数据模型

    登录成功时返回的响应数据结构。

    Attributes:
        success: 是否登录成功
        message: 结果消息
        user_id: 用户ID
        user_name: 用户名称
    """

    phone: str


class TokenInfo(BaseModel):
    """Token信息数据模型

    用于服务层返回Token相关信息。

    Attributes:
        user_id: 用户ID
        phone: 用户手机号
        token: 认证令牌
        created_at: Token创建时间
        expires_at: Token过期时间
    """

    user_id: str
    phone: str
    token: str
    created_at: datetime
    expires_at: datetime


class LoginResult(BaseModel):
    """登录结果数据模型

    服务层登录函数返回的完整结果。

    Attributes:
        success: 是否登录成功
        message: 结果消息
        user_id: 用户ID
        user_name: 用户名称
        token_info: Token详细信息
    """

    success: bool
    message: str
    user_id: str
    user_name: str
    token_info: TokenInfo
    phone: str


class PhoneResponse(BaseModel):
    """手机号响应数据模型

    根据token获取用户手机号的响应数据结构。

    Attributes:
        phone: 用户手机号
    """

    phone: str


class SendVerificationCodeResponse(BaseModel):
    success: bool
    msg: str
    phone: str
    expire_minutes: int


class SendVerificationCodeHandlerBody(BaseModel):
    phone: str = Field(
        ...,
        description="手机号码",
        min_length=11,
        max_length=11,
        examples=["13800138000"],
    )
