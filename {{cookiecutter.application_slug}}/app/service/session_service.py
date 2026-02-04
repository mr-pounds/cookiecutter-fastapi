from typing import Literal

from sqlalchemy.orm import Session

from app.common.exception import errors
from app.crud.session import session_dao
from app.crud.user import user_dao
from app.model.session import SessionORM
from app.schema.session import CreateSessionSchema


def create_session(
    db_session: Session,
    user_id: str,
    app_name: str,
    material_url: str,
    integrate_gear: Literal[1, 2, 3],
    factory_name: str | None = None,
    factory_address: str | None = None,
    product_line_num: int | None = None,
    avg_product_width: float | None = None,
) -> SessionORM:
    """创建会话

    业务逻辑：
    1. 验证用户是否存在
    2. 检查用户剩余会话次数是否充足
    3. 创建新会话
    4. 更新用户剩余会话次数
    5. 提交事务

    Args:
        db_session: 数据库会话
        user_id: 用户ID
        app_name: 应用名称
        material_url: 素材URL
        paper_url: 论文URL
        integrate_gear: 集成等级

    Returns:
        创建的会话对象

    Raises:
        UserNotFoundException: 用户不存在
        NoSessionQuota: 会话配额不足
        ValueError: 必要参数为空
    """
    # 参数验证
    if not all([user_id, app_name, material_url]):
        raise ValueError("Required parameters cannot be empty")

    # 1. 获取用户信息
    user_obj = user_dao.get_user(db_session, user_id)

    if user_obj is None:
        raise errors.CustomError(error=errors.CustomErrorCode.USER_NOT_FOUND_ERROR)

    # 2. 检查会话配额
    if user_obj.left_session_num <= 0:
        raise errors.CustomError(error=errors.CustomErrorCode.AGENT_SESSION_QUOTA_ERROR)

    # 3. 创建会话
    session_obj = CreateSessionSchema(
        user_id=user_id,
        app_name=app_name,
        material_url=material_url,
        integrate_gear=integrate_gear,
        factory_name=factory_name,
        factory_address=factory_address,
        product_line_num=product_line_num,
        avg_product_width=avg_product_width,
    )
    session_obj = session_dao.create(db_session=db_session, obj=session_obj)

    # 4. 更新用户剩余会话次数
    user_obj.left_session_num -= 1
    user_dao.update(db_session, user_obj)

    # 5. 提交事务
    # db_session.commit()

    return session_obj
