"""
会话模型模块

该模块定义了会话相关的数据库模型，对应 sessions 表。
"""

import hashlib
import time
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.model.session import SessionORM
from app.schema.session import CreateSessionSchema


class SessionCRUD:
    """会话数据访问对象类

    提供会话数据的增删改查操作。

    Methods:
        create: 创建新会话
        update: 更新会话信息
        delete: 删除会话
        get_session: 根据会话ID获取会话
        get_all_sessions: 获取用户的所有会话
    """

    def create(
        self,
        db_session: Session,
        obj: CreateSessionSchema,
    ) -> SessionORM:
        session_id, session_name = self._create_session_id_and_name(obj.user_id)
        obj_data = obj.model_dump()
        obj_data["session_id"] = session_id
        obj_data["session_name"] = session_name
        ins = SessionORM(**obj_data)
        db_session.add(ins)
        return ins

    def _create_session_id_and_name(self, user_id: str) -> tuple[str, str]:
        """生成唯一会话ID

        使用用户ID、时间戳和UUID生成唯一的会话标识符，
        并通过MD5哈希进行简化。

        Args:
            user_id: 用户ID

        Returns:
            生成的会话ID字符串
        """
        timestamp = str(int(time.time() * 1000))
        data = f"{user_id}-{timestamp}-{uuid.uuid4().hex[:8]}"
        md5_str = hashlib.md5(data.encode()).hexdigest()
        session_id = md5_str[:24]
        session_name = f"{datetime.now().strftime('%Y-%m-%d')}-{md5_str[:6]}"
        return session_id, session_name

    def update(self, db_session: Session, session: SessionORM) -> None:
        """更新会话信息

        Args:
            db_session: 数据库会话
            session: 要更新的会话对象
        """
        session.updated_at = datetime.now()
        db_session.add(session)

    def delete(self, db_session: Session, session_id: str) -> None:
        """删除会话

        Args:
            db_session: 数据库会话
            session_id: 要删除的会话ID
        """
        db_session.delete(self.get_session(db_session, session_id))

    def get_session(self, db_session: Session, session_id: str) -> SessionORM | None:
        """根据会话ID获取会话

        Args:
            db_session: 数据库会话
            session_id: 会话ID

        Returns:
            会话对象

        Raises:
            NoResultFound: 未找到对应会话
        """
        statement = select(SessionORM).where(
            SessionORM.session_id == session_id,
            SessionORM.is_delete == False,  # noqa: E712
        )
        return db_session.scalar(statement)

    def get_all_sessions(self, db_session: Session, user_id: str) -> list[SessionORM]:
        """获取用户的所有会话

        Args:
            db_session: 数据库会话
            user_id: 用户ID

        Returns:
            该用户的所有未删除会话列表
        """
        statement = (
            select(SessionORM)
            .where(
                SessionORM.user_id == user_id,
                SessionORM.is_delete == False,  # noqa: E712
            )
            .order_by(SessionORM.created_at.desc())
        )
        return list(db_session.scalars(statement).all())  # 使用 scalars() 获取多个结果


session_dao = SessionCRUD()
