"""
Description  :
Version      : 1.0.1
Author       : zzz
Date         : 2025-09-18 09:52:23
LastEditors  : zzz
LastEditTime : 2025-09-18 10:17:22
"""

import logging

from app.config import settings


# 创建自定义Formatter类
class CustomExtraFormatter(logging.Formatter):
    """自定义日志格式化器，支持添加额外的上下文信息"""

    def __init__(self, fmt=None, datefmt=None, style="%", validate=True):
        # 设置默认的额外字段值
        self.defaults = {
            "applicationCode": settings.APPLICATION_CODE,
            "applicationName": settings.APPLICATION_NAME,
        }
        super().__init__(fmt, datefmt, style, validate)

    def format(self, record):
        # 为每个日志记录添加默认的额外字段
        for key, value in self.defaults.items():
            setattr(record, key, value)

        if hasattr(record, "extra"):
            for key, value in record.extra.items():
                setattr(record, key, value)

        # 调用父类的format方法完成实际的格式化
        return super().format(record)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        "custom_formatter": {
            "()": CustomExtraFormatter,
            "format": "{'timestamp':'%(asctime)s', 'thread': '%(thread)s','level': '%(levelname)s', 'loggerName': '%(name)s', 'message': '%(message)s', 'linkid': '%(linkid)s', 'applicationName': '%(applicationName)s', 'applicationCode': '%(applicationCode)s'}",
        },
    },
    "handlers": {
        "default": {
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
        },
        "stream_handler": {
            "formatter": "custom_formatter",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
        },
    },
    "loggers": {
        "dj": {"handlers": ["stream_handler"], "level": "TRACE", "propagate": False},
        "dj.error": {
            "handlers": ["stream_handler"],
            "level": "TRACE",
            "propagate": False,
        },
    },
}
