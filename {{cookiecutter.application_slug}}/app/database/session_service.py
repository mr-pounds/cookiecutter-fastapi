"""
ADK 会话服务模块

提供 Google ADK (Agent Development Kit) 的数据库会话服务集成。
该模块使用 SQLAlchemy 和 PostgreSQL 数据库存储和管理 AI Agent 的会话状态。

主要组件：
- DATABASE_URL: PostgreSQL 数据库连接 URL
- database_session_service: DatabaseSessionService 实例，用于管理会话持久化

依赖：
- google.adk.sessions.database_session_service: ADK 的数据库会话服务
- sqlalchemy: SQLAlchemy 数据库工具库
- settings: 应用配置模块
"""

from google.adk.sessions.database_session_service import DatabaseSessionService

from app.common.config import settings

# 构建 PostgreSQL 数据库连接 URL
# 格式：postgresql+psycopg://用户名:密码@主机:端口/数据库名
# 示例：postgresql+psycopg://postgres:***@192.168.2.49:32768/postgres
DATABASE_URL = f"postgresql+psycopg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
# 创建 ADK 数据库会话服务实例
# 该服务负责将 AI Agent 的会话状态持久化到 PostgreSQL 数据库中
# 支持会话的创建、读取、更新和删除操作
database_session_service = DatabaseSessionService(db_url=DATABASE_URL)
