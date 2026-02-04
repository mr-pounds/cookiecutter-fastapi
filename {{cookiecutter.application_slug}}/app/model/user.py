"""
用户模型模块

该模块定义了用户相关的数据库模型，对应 users 表。
"""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.db import Base


class UserORM(Base):
    """用户数据库模型

    对应用户表，存储用户的基本信息。

    Attributes:
        id: 主键
        user_id: 用户ID（唯一）
        user_name: 用户名称
        phone: 手机号码
        left_session_num: 剩余会话次数
        created_at: 创建时间
        updated_at: 更新时间
    """

    __tablename__ = "users"

    # 所有没有默认值的属性必须放在前面
    user_id: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, comment="用户ID"
    )
    user_name: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="用户名称"
    )
    phone: Mapped[str] = mapped_column(String(20), nullable=False, comment="手机号码")
    # 有默认值的属性放在后面
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        unique=True,
        index=True,
        init=False,
        autoincrement=True,
        comment="主键",
    )
    left_session_num: Mapped[int] = mapped_column(
        Integer, default=4, comment="剩余会话次数"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default_factory=datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default_factory=datetime.now, comment="更新时间"
    )
