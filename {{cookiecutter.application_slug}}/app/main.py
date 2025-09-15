"""
Name         :
Description  :
Version      : 1.0.1
Author       : zzz
Date         : 2025-04-30 16:30:22
LastEditors  : zzz
LastEditTime : 2025-09-15 09:01:07
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.config import settings
from app.constants import error_code
from app.demo.router import router as demo_router
from app.log import LOGGING_CONFIG
from app.response import ResponseModel

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("dj")


# if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
#     sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

SHOW_DOCS_ENVIRONMENT = ("local", "staging")
is_show_docs = settings.ENVIRONMENT in SHOW_DOCS_ENVIRONMENT

responses = {
    400: {"model": ResponseModel[None]},
    403: {"model": ResponseModel[None]},
    404: {"model": ResponseModel[None]},
    409: {"model": ResponseModel[None]},
    422: {"model": ResponseModel[None]},
}


app = FastAPI(
    title=settings.APPLICATION_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if is_show_docs else None,
    responses=responses,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> ResponseModel[None]:
    """将HTTPException的格式转化为统一的数据格式，方便前端处理。
    Args:
        _ (Request): _description_
        exc (HTTPException): _description_

    Returns:
        _type_: ResponseModel[None]
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "msg": exc.detail,
            "success": False,
            "data": None,
            "code": exc.status_code,
        },
    )


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(
    _: Request, exc: RequestValidationError
) -> ResponseModel[None]:
    """将 RequestValidationError 的格式转化为统一的数据格式，方便前端处理。
    Args:
        _ (Request): _description_
        exc (HTTPException): _description_

    Returns:
        _type_: ResponseModel[None]
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "msg": exc.errors(),
            "success": False,
            "data": None,
            "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
        },
    )


@app.middleware("http")
async def log_request(request: Request, call_next):
    link_id = request.headers.get("linkid")
    if request.method == "POST":
        logger.info(
            f"Request: {request.method} {request.url} {await request.json()}",
            link_id=link_id,
        )
    else:
        logger.info(
            f"Request: {request.method} {request.url}", extra={"linkid": link_id}
        )
    response = await call_next(request)
    return response


# 添加路由，一般不用处理
app.include_router(
    demo_router,
    prefix=settings.API_V1_STR,
)
