from typing import Literal

from pydantic import BaseModel


class SessionBaseInfoResponse(BaseModel):
    session_id: str
    session_name: str
    material_url: str
    integrate_gear: int


class CreateSessionBody(BaseModel):
    material_url: str
    integrate_gear: Literal[1, 2, 3]
    factory_name: str | None = None
    factory_address: str | None = None
    product_line_num: int | None = None
    avg_product_width: float | None = None


class CreateSessionSchema(CreateSessionBody):
    user_id: str
    app_name: str
