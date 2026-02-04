"""
会话模型模块

该模块定义了会话相关的数据库模型，对应 sessions 表。
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.db import Base


class SessionORM(Base):
    """会话数据库模型

    对应用户会话表，存储用户的会话信息。

    Attributes:
        id: 主键
        user_id: 用户ID
        session_id: 会话唯一标识
        session_name: 会话名称
        material_url: 材料文件OSS地址
        paper_url: 原纸文件OSS地址
        integrate_gear: 整合强度
        left_chat_num: 剩余对话次数
        report: 会话报告
        app_name: 应用名称
        is_delete: 是否删除
        created_at: 创建时间
        updated_at: 更新时间
    """

    __tablename__ = "session_records"

    # 所有没有默认值的属性必须放在前面
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, comment="用户ID")
    session_id: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, comment="会话唯一标识"
    )
    session_name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="会话名称"
    )
    material_url: Mapped[str] = mapped_column(
        String(1024), nullable=False, comment="材料文件OSS地址"
    )
    app_name: Mapped[str] = mapped_column(String(100), comment="应用名称")
    integrate_gear: Mapped[int] = mapped_column(Integer, default=1, comment="整合强度")
    factory_name: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        default=None,
        comment="工厂名称",
    )
    factory_address: Mapped[str] = mapped_column(
        String(300), nullable=True, default=None, comment="工厂地址"
    )
    product_line_num: Mapped[int] = mapped_column(
        Integer, nullable=True, default=None, comment="产线数量"
    )
    avg_product_width: Mapped[float] = mapped_column(
        Float, nullable=True, default=None, comment="平均门幅"
    )

    # 有默认值的属性放在后面
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        init=False,
        unique=True,
        index=True,
        autoincrement=True,
        comment="主键",
    )
    left_chat_num: Mapped[int] = mapped_column(
        Integer, default=10, comment="剩余对话次数"
    )
    report: Mapped[str] = mapped_column(String, default="", comment="会话报告")
    is_delete: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否删除")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default_factory=datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default_factory=datetime.now, comment="更新时间"
    )
