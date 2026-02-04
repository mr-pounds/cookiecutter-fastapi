"""
Name         :
Description  :
Version      : 1.0.1
Author       : zzz
Date         : 2025-05-28 15:08:51
LastEditors  : zzz
LastEditTime : 2025-09-13 15:11:50
"""

from fastapi import APIRouter, Query, Response

from app.common.config import settings
from app.common.deps import DatabaseSessionDep, DatabaseSessionTransactionDep, TokenDep
from app.common.exception import errors
from app.common.response import (
    CustomErrorCode,
    ListResponseSchema,
    ListSchema,
    ResponseSchema,
)
from app.crud.session import session_dao
from app.crud.user import user_dao
from app.schema.auth import (
    LoginRequest,
    LoginResponse,
    PhoneResponse,
    SendVerificationCodeHandlerBody,
)
from app.schema.session import CreateSessionBody, SessionBaseInfoResponse
from app.service import session_service
from app.service.auth_service import auth_service

router = APIRouter(prefix="/api")


@router.post("/create_session", tags=["session"])
async def create_session(
    db_session: DatabaseSessionTransactionDep, user: TokenDep, body: CreateSessionBody
) -> ResponseSchema[SessionBaseInfoResponse]:
    """创建 AI Agent 会话接口
    为用户创建一个新的 AI Agent 会话，并返回会话信息

    Args:
        db_session (DatabaseSessionDep): 数据库会话依赖注入
        user (UserDep): 当前用户 ID 依赖注入

    Returns:
        ResponseModel: {
        }
    """
    # 在数据库中创建会话记录
    session = session_service.create_session(
        db_session=db_session,
        user_id=user.user_id,
        app_name=settings.APPLICATION_NAME,
        material_url=body.material_url,
        integrate_gear=body.integrate_gear,
        factory_name=body.factory_name,
        factory_address=body.factory_address,
        product_line_num=body.product_line_num,
        avg_product_width=body.avg_product_width,
    )
    # 返回会话访问地址
    return ResponseSchema(
        data=SessionBaseInfoResponse(
            session_id=session.session_id,
            session_name=session.session_name,
            material_url=session.material_url,
            integrate_gear=session.integrate_gear,
        )
    )


@router.get("/get_left_session_quota", tags=["session"])
def get_left_session_quota(
    db_session: DatabaseSessionDep, user: TokenDep
) -> ResponseSchema[int]:
    user_obj = user_dao.get_user(db_session, user.user_id)
    if user_obj is None:
        raise errors.CustomError(error=CustomErrorCode.USER_NOT_FOUND_ERROR)
    return ResponseSchema(data=user_obj.left_session_num)


@router.get("/get_history_sessions", tags=["session"])
def get_history_sessions(
    db_session: DatabaseSessionDep, user: TokenDep
) -> ListResponseSchema[SessionBaseInfoResponse]:
    history_sessions = session_dao.get_all_sessions(db_session, user.user_id)
    return ListResponseSchema(
        data=ListSchema(
            total=len(history_sessions),
            list=[
                SessionBaseInfoResponse(
                    session_id=session.session_id,
                    session_name=session.session_name,
                    material_url=session.material_url,
                    integrate_gear=session.integrate_gear,
                )
                for session in history_sessions
            ],
        )
    )


@router.get(
    "/get_left_chat_quota",
    tags=["session"],
)
def get_left_chat_quota(
    db_session: DatabaseSessionDep,
    _: TokenDep,
    session_id: str = Query(title="会话ID"),
) -> ResponseSchema[int]:
    session = session_dao.get_session(db_session, session_id)
    if session is None:
        raise errors.CustomError(error=CustomErrorCode.AGENT_SESSION_ERROR)
    return ResponseSchema(data=session.left_chat_num)


@router.post("/send_verification_code", tags=["auth"])
async def send_verification_code_handler(
    body: SendVerificationCodeHandlerBody,
) -> ResponseSchema[None]:
    """发送验证码接口

    向指定手机号发送6位数字验证码。

    功能流程：
    1. 校验手机号格式（中国大陆手机号）
    2. 检查发送间隔（5分钟内不能重复发送）
    3. 生成6位随机验证码并保存到Redis（6分钟过期）
    4. 调用短信服务API发送验证码

    Args:
        phone: 接收验证码的手机号（必填）

    Returns:
        ResponseModel: {
            "success": true,
            "message": "验证码发送成功",
            "phone": "13800138000",
            "expire_minutes": 6
        }

    Raises:
        400: 手机号格式不正确
        429: 发送过于频繁，请稍后重试
        500: 短信服务调用失败
    """
    result = await auth_service.send_verification_code(body.phone)
    return ResponseSchema(success=result.success, msg=result.msg, data=None)


@router.post("/login", tags=["auth"])
async def login_handler(
    db_session: DatabaseSessionTransactionDep, response: Response, body: LoginRequest
) -> ResponseSchema[LoginResponse]:
    """用户登录接口

    通过手机号和验证码进行用户登录认证。

    功能流程：
    1. 校验手机号格式（中国大陆手机号）
    2. 验证6位数字验证码是否正确
    3. 根据手机号查询用户信息
    4. 生成Token并存储到Redis（7天有效期）
    5. 将Token写入Cookie（HttpOnly, Secure）

    Cookie设置：
    - 名称: token
    - 路径: /
    - HttpOnly: true（防止XSS攻击）
    - Secure: true（仅HTTPS传输）
    - SameSite: Lax

    Args:
        db_session: 数据库会话依赖注入
        response: FastAPI Response对象，用于设置Cookie
        body: 登录请求体，包含手机号和验证码

    Returns:
        LoginResponse: {
            "success": true,
            "message": "登录成功",
            "user_id": "2fd2f6bb",
            "user_name": "用户名"
        }

    Raises:
        400: 手机号格式不正确
        401: 验证码错误或Token无效/已过期
        404: 用户不存在
        500: 服务器内部错误
    """
    # 执行登录逻辑
    result = await auth_service.login(db_session, body.phone, body.verification_code)

    # 获取Token信息
    token_info = result.token_info

    # 将Token写入Cookie（设置expires为UTC时间）
    response.set_cookie(
        key="token",
        value=token_info.token,
        path="/",
        httponly=True,
        secure=False,
        samesite=None,
        expires=token_info.expires_at,
    )

    # 返回登录结果
    return ResponseSchema(data=LoginResponse(phone=result.phone))


@router.get("/get_phone", tags=["auth"])
def get_phone_handler(user: TokenDep) -> ResponseSchema[PhoneResponse]:
    """获取当前用户手机号接口

    根据当前登录用户的token返回其手机号码。

    功能流程：
    1. 通过UserDep获取当前用户ID
    2. 根据用户ID查询用户信息
    3. 返回用户手机号

    Args:
        db_session: 数据库会话依赖注入
        user: 当前用户 ID 依赖注入

    Returns:
        PhoneResponse: {
            "success": true,
            "message": "获取成功",
            "data": {
                "phone": "13800138000"
            }
        }

    Raises:
        404: 用户不存在
    """
    return ResponseSchema(data=PhoneResponse(phone=user.phone))
