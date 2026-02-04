"""
短信验证码服务模块

该模块提供短信验证码的生成、发送和验证功能。
支持手机号格式校验、发送频率限制、验证码生成和Redis存储等功能。

主要功能：
- 生成指定位数的数字验证码
- 手机号格式校验
- 发送频率限制（5分钟内不能重复发送）
- 调用第三方短信服务API发送验证码
- Redis存储验证码及发送时间信息

Usage:
    from app.service.sms_service import send_verification_code

    result = await send_verification_code(phone="13800138000")
"""

import json
from typing import Any

import httpx

from app.common.config import settings
from app.common.exception import errors
from app.common.log import log


class SMSService:
    @staticmethod
    async def send_sms(phone: str, template_code: str, code: str) -> dict[str, Any]:
        """调用第三方短信服务API发送验证码

        Args:
            phone: 接收手机号
            template_code: 短信模板code
            code: 验证码

        Returns:
            API响应结果

        Raises:
            SMSServiceError: 短信服务调用失败
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    settings.SMS_API_URL,
                    data={
                        "phone": phone,
                        "code": template_code,
                        "data": json.dumps({"code": code}),
                    },  # ty:ignore[invalid-argument-type]
                )

                response.raise_for_status()

                result = response.json()
                # print("response", result)

                # 根据实际短信服务API响应格式调整
                # 这里假设返回格式包含success字段
                if result.get("success"):
                    log.info(f"短信发送成功: phone={phone}")
                    return result
                else:
                    error_msg = result.get("msg", "未知错误")
                    log.error(f"短信发送失败: phone={phone}, error={error_msg}")
                    raise errors.CustomError(
                        error=errors.CustomErrorCode.SMS_SERVICE_ERROR
                    )

        except Exception as e:
            log.error(f"短信服务异常: {e}")
            raise errors.CustomError(error=errors.CustomErrorCode.SMS_SERVICE_ERROR)


sms_service = SMSService()
