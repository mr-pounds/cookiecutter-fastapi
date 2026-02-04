from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class AccessMiddleware(BaseHTTPMiddleware):
    """访问日志中间件"""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        请求日志中间件
        ==============
        在每个 HTTP 请求处理前后记录日志，便于问题排查和性能监控

        功能说明：
        - POST 请求：记录请求方法、URL 和请求体内容
        - GET 请求：只记录请求方法 和 URL
        - 记录响应状态（在 call_next 之后可扩展）

        Args:
            request (Request): 当前处理的请求对象
            call_next: 下一个中间件或路由处理函数的调用

        Returns:
            Response: 请求处理后的响应对象
        """
        if request.method == "POST":
            print(f"Request: {request.method} {request.url} {await request.json()}")
        else:
            print(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        return response
