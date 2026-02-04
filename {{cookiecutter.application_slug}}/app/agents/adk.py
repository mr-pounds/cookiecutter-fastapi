from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
from app.crud.session import session_dao
from app.database.db import sync_db_session
from app.database.session_service import database_session_service
from app.schema.adk import (AgentsSchema, HealthResponse, ListAgentsResponse,
                            RootResponse)
from fastapi import FastAPI
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.agent_tool import AgentTool

MODEL_QWEN_MAX = LiteLlm(
    "openai/qwen3-max-2026-01-23",
)

root_agent = Agent(
    model=MODEL_QWEN_MAX,
    name="root_agent",
    description="结合材质整合报告，问答用户相关问题。",
    tools=[],
    instruction="""瓦楞纸板材质整合智能体""",
)


def extract_user_id(input_data) -> str:
    """Extract user ID from context."""
    # print("extract_user_id")
    session_id = input_data.thread_id
    with sync_db_session() as db_session:
        session_obj = session_dao.get_session(db_session, session_id)
        if session_obj is None:
            return ""
        return session_obj.user_id


# def extract_app_name(input_data):
#     """Extract app name from context."""
#     for ctx in input_data.context:
#         if ctx.description == "app":
#             return ctx.value
#     return "default_app"


# 创建 ADKAgent 实例
# - root_agent: AI Agent 的核心逻辑
# - app_name: 应用名称，用于会话管理
# - user_id: 用户标识，用于隔离不同用户的会话
# - session_service: 会话服务，负责管理会话状态
# - use_in_memory_services: 使用内存服务提高性能
# - max_concurrent_executions: 最大并发执行数
# - cleanup_interval_seconds: 清理过期会话的间隔时间
ag_agent = ADKAgent(
    root_agent,
    app_name="product_integration",
    user_id_extractor=extract_user_id,
    session_service=database_session_service,
    use_in_memory_services=True,
    max_concurrent_executions=10,
    cleanup_interval_seconds=60 * 5,
)


def register_adk_agent(app: FastAPI):
    add_adk_fastapi_endpoint(app, ag_agent, path="/chat")

    @app.get("/")
    async def root() -> RootResponse:
        available_agents = ["product_integration"]
        endpoints = {"chat": "/chat", "docs": "/docs", "health": "/health"}
        return RootResponse(
            service="product_integration",
            version="0.1.0",
            agents=AgentsSchema(
                default="product_integration", available=available_agents
            ),
            endpoints=endpoints,
        )

    @app.get("/health")
    async def health() -> HealthResponse:
        return HealthResponse(
            status="healthy", agents_available=1, default_agent="product_integration"
        )

    @app.get("/agents")
    async def list_agents() -> ListAgentsResponse:
        """List available agents."""
        available_agents = ["product_integration"]
        return ListAgentsResponse(
            agents=available_agents, default="product_integration"
        )
