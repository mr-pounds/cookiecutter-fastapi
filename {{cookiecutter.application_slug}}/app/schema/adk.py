from pydantic import BaseModel


class AgentsSchema(BaseModel):
    default: str
    available: list[str]


class RootResponse(BaseModel):
    service: str
    version: str
    agents: AgentsSchema
    endpoints: dict[str, str]


class HealthResponse(BaseModel):
    status: str
    agents_available: int
    default_agent: str


class ListAgentsResponse(BaseModel):
    default: str
    agents: list[str]
