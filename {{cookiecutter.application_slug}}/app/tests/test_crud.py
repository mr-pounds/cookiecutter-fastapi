"""
CRUD操作测试
测试数据库CRUD操作的功能，包括用户、会话、材质和原纸的CRUD操作
"""

from app.crud.session import session_dao
from app.crud.user import user_dao
from app.schema.session import CreateSessionSchema
from sqlalchemy.orm import Session


class TestCRUD:
    """CRUD操作测试类"""

    def test_user_crud(self, db: Session):
        """测试用户CRUD操作"""
        # 测试创建用户
        user = user_dao.create(
            db_session=db, user_name="test_user", phone="13800138000"
        )
        db.commit()
        db.refresh(user)

        assert user is not None
        assert user.user_name == "test_user"
        assert user.phone == "13800138000"

        # 测试根据ID获取用户
        get_user = user_dao.get_user(db_session=db, user_id=user.user_id)
        assert get_user is not None
        assert get_user.user_id == user.user_id

        # 测试根据手机号获取用户
        get_user_by_phone = user_dao.get_user_by_phone(
            db_session=db, phone="13800138000"
        )
        assert get_user_by_phone is not None
        assert get_user_by_phone.phone == "13800138000"

        # 测试更新用户
        user.user_name = "updated_user"
        user_dao.update(db_session=db, user=user)
        db.commit()
        db.refresh(user)

        updated_user = user_dao.get_user(db_session=db, user_id=user.user_id)
        assert updated_user
        assert updated_user.user_name == "updated_user"

    def test_session_crud(self, db: Session):
        """测试会话CRUD操作"""
        # 先创建一个测试用户
        user = user_dao.create(
            db_session=db, user_name="test_user", phone="13800138001"
        )
        db.commit()
        db.refresh(user)

        # 测试创建会话
        session_schema = CreateSessionSchema(
            user_id=user.user_id,
            app_name="test_app",
            material_url="http://test.com/material",
            integrate_gear=1,
        )

        session = session_dao.create(db_session=db, obj=session_schema)
        db.commit()
        db.refresh(session)

        assert session is not None
        assert session.user_id == user.user_id
        assert session.app_name == "test_app"

        # 测试根据ID获取会话
        get_session = session_dao.get_session(
            db_session=db, session_id=session.session_id
        )
        assert get_session is not None
        assert get_session.session_id == session.session_id

        # 测试获取用户的所有会话
        all_sessions = session_dao.get_all_sessions(db_session=db, user_id=user.user_id)
        assert len(all_sessions) >= 1

        # 测试更新会话
        session.app_name = "updated_app"
        session_dao.update(db_session=db, session=session)
        db.commit()
        db.refresh(session)

        updated_session = session_dao.get_session(
            db_session=db, session_id=session.session_id
        )
        assert updated_session
        assert updated_session.app_name == "updated_app"

        # 测试删除会话
        session_dao.delete(db_session=db, session_id=session.session_id)
        db.commit()

        deleted_session = session_dao.get_session(
            db_session=db, session_id=session.session_id
        )
        assert deleted_session is None