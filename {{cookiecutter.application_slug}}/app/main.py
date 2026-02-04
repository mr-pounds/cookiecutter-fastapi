"""
FastAPI 应用主入口文件
=====================
Description : 产品集成平台的 Web 服务入口，集成 AG-UI ADK 框架实现 AI Agent 会话管理
Version     : 1.0.1
Author      : zzz
Date        : 2025-04-30 16:30:22
LastEditors : zzz
LastEditTime: 2025-09-18 10:17:28
"""

import logging

from app.agents.adk import register_adk_agent
from app.common.config import settings
from app.common.exception.exception_handler import register_exception
from app.common.log import setup_logging
from app.common.middleware import AccessMiddleware
from app.router import router as api_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 配置日志系统，使用预定义的 LOGGING_CONFIG 配置
logging.getLogger("adk_agent").setLevel(logging.WARNING)
logging.getLogger("event_translator").setLevel(logging.WARNING)
logging.getLogger("endpoint").setLevel(logging.WARNING)
logging.getLogger("session_manager").setLevel(logging.WARNING)
logging.getLogger("agent_registry").setLevel(logging.WARNING)


# 定义文档显示的环境配置，只有在 local 和 staging 环境才显示 OpenAPI 文档
SHOW_DOCS_ENVIRONMENT = ("local", "staging")
is_show_docs = settings.ENVIRONMENT in SHOW_DOCS_ENVIRONMENT

# 初始化 FastAPI 应用实例
# 根据环境配置决定是否开启 OpenAPI 文档访问
app = FastAPI(
    title=settings.APPLICATION_NAME,
    # openapi_url="/openapi.json" if is_show_docs else None,
    openapi_url="/openapi.json",
)

# 配置跨域资源共享（CORS）中间件
# 允许配置的域名列表中的来源进行跨域请求
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,  # ty:ignore[invalid-argument-type]
        allow_origins=settings.all_cors_origins,  # 允许的跨域来源列表
        allow_credentials=True,  # 允许携带认证信息（cookies、authorization header 等）
        allow_methods=["*"],  # 允许所有 HTTP 方法
        allow_headers=["*"],  # 允许所有 HTTP 头
    )

# 注册异常处理器
register_exception(app)
# 注册中间件
app.add_middleware(AccessMiddleware)  # ty:ignore[invalid-argument-type]
# 注册adk
register_adk_agent(app)
# 注册日志
setup_logging()

# 注册应用路由
# 将所有通过 app.router 定义的路由注册到主应用
# 前缀配置保留，可根据需要在 settings 中启用
app.include_router(
    api_router,
    # prefix=settings.API_VERSION_STR,
)
