import sys
from collections.abc import AsyncGenerator, Generator

from app.common.config import settings
from app.common.log import log
from sqlalchemy import URL, Engine, create_engine
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.orm import (DeclarativeBase, MappedAsDataclass, Session,
                            declared_attr, sessionmaker)


class MappedBase(DeclarativeBase):
    """
    声明式基类, 作为所有基类或数据模型类的父类而存在

    `AsyncAttrs <https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#sqlalchemy.ext.asyncio.AsyncAttrs>`__

    `DeclarativeBase <https://docs.sqlalchemy.org/en/20/orm/declarative_config.html>`__

    `mapped_column() <https://docs.sqlalchemy.org/en/20/orm/mapping_api.html#sqlalchemy.orm.mapped_column>`__
    """

    @declared_attr.directive
    def __tablename__(self) -> str:
        """生成表名"""
        return self.__name__.lower()

    @declared_attr.directive
    def __table_args__(self) -> dict:
        """表配置"""
        return {"comment": self.__doc__ or ""}

    def to_dict(self) -> dict:
        """将表模型的每个字段转成字典格式

        Returns:
            dict: 包含所有字段名和对应值的字典
        """
        result = {}

        # 遍历所有映射的列
        for column in self.__table__.columns:
            column_name = column.name
            column_value = getattr(self, column_name, None)

            # 处理特殊类型的数据
            if hasattr(column_value, "isoformat"):
                # 处理 datetime 对象
                column_value = column_value.isoformat()
            elif isinstance(column_value, (list, dict)):
                # 处理 JSON 序列化的数据
                column_value = column_value

            result[column_name] = column_value

        return result


class Base(MappedAsDataclass, MappedBase):
    """
    声明性数据类基类, 带有数据类集成, 允许使用更高级配置, 但你必须注意它的一些特性, 尤其是和 DeclarativeBase 一起使用时

    `MappedAsDataclass <https://docs.sqlalchemy.org/en/20/orm/dataclasses.html#orm-declarative-native-dataclasses>`__
    """

    __abstract__ = True


def create_database_url(*, unittest: bool = False) -> URL:
    """
    创建数据库链接

    :param unittest: 是否用于单元测试
    :return:
    """
    url = URL.create(
        "postgresql+psycopg",
        username=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_SERVER,
        port=settings.POSTGRES_PORT,
        database=settings.POSTGRES_DB
        if not unittest
        else f"{settings.POSTGRES_DB}_test",
    )
    return url


def create_async_engine_and_session(
    url: str | URL,
) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    """
    创建数据库异步引擎和 Session

    :param url: 数据库连接 URL
    :return: (异步引擎, 异步会话工厂)
    """
    try:
        # 数据库异步引擎
        engine = create_async_engine(
            url,
            echo=settings.DATABASE_ECHO,
            echo_pool=settings.DATABASE_POOL_ECHO,
            future=True,
            # 连接池配置
            # pool_size: 池中保持的最小连接数
            pool_size=10,
            # max_overflow: 超出 pool_size 后允许创建的最大连接数
            max_overflow=20,
            # pool_timeout: 从池中获取连接的超时时间（秒）
            pool_timeout=30,
            # pool_recycle: 连接回收时间（秒），避免长时间闲置连接失效
            pool_recycle=3600,
            # pool_pre_ping: 每次从池中获取连接前先测试连接是否有效
            pool_pre_ping=True,
            # pool_use_lifo: 使用后进先出策略，更高效地复用连接
            pool_use_lifo=False,
        )
    except Exception as e:
        log.error("❌ 异步数据库链接失败 {}", e)
        sys.exit()
    else:
        db_session = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            autoflush=False,  # 禁用自动刷新
            expire_on_commit=False,  # 禁用提交时过期
        )
        return engine, db_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取异步数据库会话"""
    async with async_db_session() as session:
        yield session


async def get_db_transaction() -> AsyncGenerator[AsyncSession, None]:
    """获取带有事务的异步数据库会话"""
    async with async_db_session.begin() as session:
        yield session

async def create_tables() -> None:
    """创建数据库表"""
    async with async_engine.begin() as conn:
        await conn.run_sync(MappedBase.metadata.create_all)


async def drop_tables() -> None:
    """丢弃数据库表"""
    async with async_engine.begin() as conn:
        await conn.run_sync(MappedBase.metadata.drop_all)


def create_sync_engine_and_session(
    url: str | URL,
) -> tuple[Engine, sessionmaker[Session]]:
    """
    创建数据库同步引擎和 Session

    :param url: 数据库连接 URL
    :return: (同步引擎, 同步会话工厂)
    """
    try:
        # 数据库同步引擎
        engine = create_engine(
            url,
            echo=settings.DATABASE_ECHO,
            echo_pool=settings.DATABASE_POOL_ECHO,
            future=True,
            # 中等并发
            # 连接池配置
            # pool_size: 池中保持的最小连接数
            pool_size=10,
            # max_overflow: 超出 pool_size 后允许创建的最大连接数
            max_overflow=20,
            # pool_timeout: 从池中获取连接的超时时间（秒）
            pool_timeout=30,
            # pool_recycle: 连接回收时间（秒），避免长时间闲置连接失效
            pool_recycle=3600,
            # pool_pre_ping: 每次从池中获取连接前先测试连接是否有效
            pool_pre_ping=True,
            # pool_use_lifo: 使用后进先出策略，更高效地复用连接
            pool_use_lifo=False,
        )
    except Exception as e:
        log.error("❌ 同步数据库链接失败 {}", e)
        sys.exit()
    else:
        db_session = sessionmaker(
            bind=engine,
            class_=Session,
            autoflush=False,  # 禁用自动刷新
            expire_on_commit=False,  # 禁用提交时过期
        )
        return engine, db_session

def get_db_sync() -> Generator[Session, None, None]:
    """获取同步数据库会话"""
    with sync_db_session() as session:
        yield session


def get_db_transaction_sync() -> Generator[Session, None, None]:
    """获取带有事务的同步数据库会话"""
    with sync_db_session.begin() as session:
        yield session


# SQLA 数据库链接
SQLALCHEMY_DATABASE_URL = create_database_url()

# SQLA 同步引擎和会话
sync_engine, sync_db_session = create_sync_engine_and_session(SQLALCHEMY_DATABASE_URL)
# SALA 异步引擎和会话
async_engine, async_db_session = create_async_engine_and_session(
    SQLALCHEMY_DATABASE_URL
)


