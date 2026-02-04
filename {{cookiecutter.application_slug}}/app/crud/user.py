"""
用户模型模块

该模块定义了用户相关的数据库模型，对应 users 表。
"""

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.model.user import UserORM


class UserCRUD:
    """用户数据访问对象类

    提供用户数据的增删改查操作。

    Methods:
        create: 创建新用户
        get_user_by_phone: 根据手机号获取用户
        get_user: 根据用户ID获取用户
        update: 更新用户信息
    """

    def create(self, db_session: Session, user_name: str, phone: str) -> UserORM:
        """创建新用户

        Args:
            db_session: 数据库会话
            user_name: 用户名称
            phone: 手机号码

        Returns:
            创建的用户对象
        """
        user_obj = UserORM(
            user_id=uuid.uuid4().hex[:8], user_name=user_name, phone=phone
        )
        db_session.add(user_obj)
        return user_obj

    def get_user_by_phone(self, db_session: Session, phone: str) -> UserORM | None:
        """根据手机号获取用户

        Args:
            db_session: 数据库会话
            phone: 手机号码

        Returns:
            用户对象

        Raises:
            NoResultFound: 未找到对应用户
        """
        statement = select(UserORM).where(UserORM.phone == phone)
        return db_session.scalar(statement)

    def get_user(self, db_session: Session, user_id: str) -> UserORM | None:
        """根据用户ID获取用户

        Args:
            db_session: 数据库会话
            user_id: 用户ID

        Returns:
            用户对象

        Raises:
            NoResultFound: 未找到对应用户
        """
        statement = select(UserORM).where(UserORM.user_id == user_id)
        return db_session.scalar(statement)

    def update(self, db_session: Session, user: UserORM) -> None:
        """更新用户信息

        Args:
            db_session: 数据库会话
            user: 要更新的用户对象
        """
        user.updated_at = datetime.now()
        db_session.add(user)


user_dao = UserCRUD()
