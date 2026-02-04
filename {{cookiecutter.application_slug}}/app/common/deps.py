"""
依赖注入模块

该模块提供了 FastAPI 应用中常用的依赖注入函数和类型别名。
主要用于管理数据库会话、获取当前用户信息等跨请求的共享资源。

主要功能:
    - 数据库会话管理：通过 get_db() 提供请求级别的数据库会话
    - 用户依赖注入：通过 get_user() 获取当前用户信息（基于 Redis Token 验证）
    - 类型别名：提供 SessionDep 和 UserDep 方便在路由函数中使用
"""

from typing import Annotated

from app.common.exception import errors
from app.database.db import (get_db, get_db_sync, get_db_transaction,
                             get_db_transaction_sync)
from app.schema.auth import TokenInfo
from app.service.auth_service import auth_service
from fastapi import Depends, Request
from sqlalchemy.orm import Session

# adk tools 对于异步函数的支持不是很好，尽量用同步方式
DatabaseSyncSessionDep = Annotated[Session, Depends(get_db_sync)]
DatabaseSyncSessionTransactionDep = Annotated[Session, Depends(get_db_transaction_sync)]


DatabaseSessionDep = Annotated[Session, Depends(get_db)]
DatabaseSessionTransactionDep = Annotated[Session, Depends(get_db_transaction)]


async def get_user(request: Request) -> TokenInfo:
    """获取当前用户信息的依赖函数

    从请求 Cookie 中提取 Token，并在 Redis 中验证 Token 的有效性。
    如果 Token 无效或已过期，则抛出 401 异常。

    Token 验证流程：
    1. 从 Cookie 中获取名为 "token" 的值
    2. 调用 Redis 验证 Token 是否存在且有效
    3. 返回 Token 中存储的用户 ID

    Args:
        request: FastAPI Request 对象，用于获取 Cookie

    Returns:
        str: 当前用户的标识符（用户 ID）

    Raises:
        HTTPException: 401 - Token 无效或已过期
    """
    # 从 Cookie 中获取 Token
    token = request.cookies.get("token")
    if not token:
        raise errors.TokenError()

    token_info = await auth_service.validate_token(token)
    if token_info is None:
        raise errors.TokenError(msg="登录信息已失效，请重新登录")
    return token_info


# 用户依赖类型别名
# 用于需要用户身份的路由函数中
# 注意：由于 get_user 依赖于 Request 对象，
# 路由函数中需要注入 RequestDep 才能正确获取用户信息
TokenDep = Annotated[TokenInfo, Depends(get_user)]
