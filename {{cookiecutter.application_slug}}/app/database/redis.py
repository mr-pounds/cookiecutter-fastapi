"""
Redis 客户端模块

提供 Redis 异步客户端的封装实现，继承自 redis-py 的 Redis 类。
该模块实现了自定义的 Redis 客户端，包含连接管理、键前缀操作等功能。

主要组件：
- RedisCli: 自定义 Redis 客户端类，提供便捷的 Redis 操作方法
- redis_client: Redis 客户端单例实例（已注释）

依赖：
- redis: Redis Python 客户端库
- settings: 应用配置模块
"""

import sys

from redis.asyncio import Redis
from redis.exceptions import AuthenticationError, TimeoutError

from app.common.config import settings
from app.common.log import log


class RedisCli(Redis):
    """Redis 异步客户端封装类

    继承自 redis.asyncio.Redis，提供基于异步的 Redis 操作能力。
    在初始化时自动从配置中读取连接参数，并设置合适的连接选项。

    主要特性：
    - 支持密码认证
    - 自动连接保活
    - 健康检查机制
    - 响应自动解码为 UTF-8 字符串
    """

    def __init__(self) -> None:
        """初始化 Redis 客户端

        从应用配置中读取 Redis 连接参数，创建异步 Redis 连接实例。
        配置包括主机地址、端口、密码、数据库编号、超时时间等。
        """
        super().__init__(
            host=settings.PYTHON_REDIS_HOST,  # Redis 服务器主机地址
            port=settings.PYTHON_REDIS_PORT,  # Redis 服务器端口
            password=settings.PYTHON_REDIS_PASSWORD,  # Redis 认证密码
            db=settings.PYTHON_REDIS_DATABASE,  # 使用的数据库编号（0-15）
            socket_timeout=settings.PYTHON_REDIS_TIMEOUT,  # 套接字操作超时时间（秒）
            socket_connect_timeout=settings.PYTHON_REDIS_TIMEOUT,  # 套接字连接超时时间（秒）
            socket_keepalive=True,  # 启用 TCP keepalive 保持连接
            health_check_interval=30,  # 健康检查间隔（秒）
            decode_responses=True,  # 自动将响应解码为字符串（UTF-8）
        )

    async def open(self) -> None:
        """建立 Redis 连接

        尝试与 Redis 服务器建立连接，通过 ping 命令验证连接状态。
        如果连接失败，根据不同的错误类型记录日志并退出程序。

        异常处理：
        - TimeoutError: 连接超时，记录错误日志并退出
        - AuthenticationError: 认证失败，记录错误日志并退出
        - Exception: 其他异常，记录错误日志并退出
        """
        try:
            await self.ping()  # ty:ignore[invalid-await]
        except TimeoutError:
            log.error("❌ 数据库 redis 连接超时")
            sys.exit()
        except AuthenticationError:
            log.error("❌ 数据库 redis 连接认证失败")
            sys.exit()
        except Exception as e:
            log.error("❌ 数据库 redis 连接异常 {}", e)
            sys.exit()

    async def delete_prefix(
        self,
        prefix: str,
        exclude: str | list[str] | None = None,
        batch_size: int = 1000,
    ) -> None:
        """
        删除指定前缀的所有键

        使用 SCAN 命令迭代查找匹配前缀的键，并批量删除。
        支持排除特定键，支持批量删除以避免阻塞 Redis 服务器。

        参数:
            prefix: 要删除的键的前缀（必填）
            exclude: 要排除的键或键列表，可选
            batch_size: 批量删除的批次大小，默认 1000

        注意事项:
            - 使用 SCAN 命令而非 KEYS 命令，避免阻塞 Redis
            - 批量删除可以避免一次性删除大量键导致的性能问题
        """
        exclude_set = (
            set(exclude)
            if isinstance(exclude, list)
            else {exclude}
            if isinstance(exclude, str)
            else set()
        )
        batch_keys = []

        # 使用 SCAN 迭代器安全地查找匹配前缀的键
        async for key in self.scan_iter(match=f"{prefix}*"):
            if key not in exclude_set:
                batch_keys.append(key)

                # 当达到批次大小时执行批量删除
                if len(batch_keys) >= batch_size:
                    await self.delete(*batch_keys)
                    batch_keys.clear()

        # 删除剩余的键
        if batch_keys:
            await self.delete(*batch_keys)

    async def get_prefix(self, prefix: str, count: int = 100) -> list[str]:
        """
        获取指定前缀的所有键

        使用 SCAN 命令迭代查找匹配前缀的所有键。

        参数:
            prefix: 要搜索的键前缀（必填）
            count: 每次 SCAN 迭代返回的数量，默认 100

        返回:
            匹配前缀的所有键的列表

        注意事项:
            - 使用 SCAN 命令避免阻塞 Redis 服务器
            - 较大的 count 值可以提高扫描速度，但会增加内存占用
        """
        return [key async for key in self.scan_iter(match=f"{prefix}*", count=count)]


# 创建 redis 客户端单例
redis_client: RedisCli = RedisCli()
