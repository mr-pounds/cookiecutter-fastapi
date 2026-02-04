import inspect
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from app.common.config import settings
from app.constant.paths import LOG_DIR
from loguru import logger

LOG_STD_LEVEL: str = "INFO"
LOG_FORMAT: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> ' \
            '| <magenta>{process}</magenta>:<yellow>{thread}</yellow> ' \
            '| <cyan>{name}</cyan>:<cyan>{function}</cyan>:<yellow>{line}</yellow> - <level>{message}</level>"



class InterceptHandler(logging.Handler):
    """
    日志拦截处理器，用于将标准库的日志重定向到 loguru

    参考：https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord) -> None:
        # 获取对应的 Loguru 级别（如果存在）
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 查找记录日志消息的调用者
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def default_formatter(record: logging.LogRecord) -> str:
    """默认日志格式化程序"""

    # 重写 sqlalchemy echo 输出
    # https://github.com/sqlalchemy/sqlalchemy/discussions/12791
    record_name = record["name"] or ""  # ty:ignore[not-subscriptable]
    if record_name.startswith("sqlalchemy"):
        record["message"] = re.sub(r"\s+", " ", record["message"]).strip()  # ty:ignore[invalid-assignment]

    return LOG_FORMAT


def setup_logging() -> None:
    """
    设置日志处理器

    参考：
    - https://github.com/benoitc/gunicorn/issues/1572#issuecomment-638391953
    - https://github.com/pawamoy/pawamoy.github.io/issues/17
    """
    # 设置根日志处理器和级别
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(LOG_STD_LEVEL)

    for name in logging.root.manager.loggerDict.keys():
        # 清空所有默认日志处理器
        logging.getLogger(name).handlers = []

        # 配置日志传播规则
        if "uvicorn.access" in name or "watchfiles.main" in name:
            logging.getLogger(name).propagate = False
        else:
            logging.getLogger(name).propagate = True

        # Debug log handlers
        # logging.debug(f'{logging.getLogger(name)}, {logging.getLogger(name).propagate}')

    # 移除 loguru 默认处理器
    logger.remove()
    # 配置 loguru 处理器
    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "level": LOG_STD_LEVEL,
                "format": default_formatter,
            },
        ],  # ty:ignore[invalid-argument-type]
    )


def set_custom_logfile() -> None:
    """设置自定义日志文件"""
    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)

    # 日志文件
    log_access_file = LOG_DIR / settings.LOG_ACCESS_FILENAME
    log_error_file = LOG_DIR / settings.LOG_ERROR_FILENAME

    # 日志压缩回调
    def compression(filepath: str) -> Path:
        filename = filepath.split(os.sep)[-1]
        original_filename = filename.split(".")[0]
        if "-" in original_filename:
            return LOG_DIR / f"{original_filename}.log"
        return (
            LOG_DIR / f"{original_filename}_{datetime.now().strftime('%Y-%m-%d')}.log"
        )

    # 日志文件通用配置
    # https://loguru.readthedocs.io/en/stable/api/logger.html#loguru._logger.Logger.add
    log_config = {
        "format": default_formatter,
        "enqueue": True,
        "rotation": "00:00",
        "retention": "7 days",
        "compression": lambda filepath: os.rename(filepath, compression(filepath)),
    }

    # 标准输出文件
    logger.add(
        str(log_access_file),
        level="INFO",
        filter=lambda record: record["level"].no <= 25,
        backtrace=False,
        diagnose=False,
        **log_config,
    )

    # 标准错误文件
    logger.add(
        str(log_error_file),
        level="ERROR",
        filter=lambda record: record["level"].no >= 30,
        backtrace=True,
        diagnose=True,
        **log_config,
    )


# 创建 logger 实例
log = logger
