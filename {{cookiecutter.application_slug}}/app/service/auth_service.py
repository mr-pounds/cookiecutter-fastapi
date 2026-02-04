"""
认证服务模块

提供用户登录认证相关的业务逻辑，包括验证码验证、用户认证和Token管理等功能。

主要功能：
- 验证码校验（从Redis获取并验证）
- 用户手机号校验和认证
- Token生成（UUID格式）
- Token存储到Redis（7天有效期）
- Token验证（从Redis校验）
"""

import random
import re
import time
import uuid
from datetime import datetime, timedelta, timezone

from redis.exceptions import RedisError
from sqlalchemy.orm import Session

from app.common.config import settings
from app.common.exception import errors
from app.common.log import log
from app.crud.user import user_dao
from app.database.redis import redis_client
from app.schema.auth import LoginResult, SendVerificationCodeResponse, TokenInfo
from app.service.sms_service import sms_service

# Redis中Token的key前缀
TOKEN_REDIS_PREFIX = "auth:token:"


def generate_token(user_id: str) -> str:
    """生成Token

    生成UUID格式的认证令牌。

    Args:
        user_id: 用户唯一标识

    Returns:
        Token字符串（UUID格式）
    """
    # 使用UUID生成唯一Token
    token = uuid.uuid4().hex

    log.info(f"Token已生成: user_id={user_id}, token={token[:8]}...")
    return token


def get_token_redis_key(token: str) -> str:
    """获取Token在Redis中的存储key

    Args:
        token: Token字符串

    Returns:
        Redis key字符串
    """
    return f"{TOKEN_REDIS_PREFIX}{token}"


async def save_token_to_redis(token: str, user_id: str, phone: str) -> None:
    """将Token保存到Redis

    Args:
        token: Token字符串
        user_id: 用户ID
        phone: 用户手机号
    """
    try:
        key = get_token_redis_key(token)
        # 存储用户信息，使用JSON格式
        value = f"{user_id}:{phone}"
        await redis_client.setex(key, settings.TOKEN_EXPIRE_DAYS * 24 * 60 * 60, value)
        log.info(f"Token已保存到Redis: key={key}, user_id={user_id}")
    except RedisError as e:
        log.error(f"保存Token到Redis失败: {e}")
        raise


def validate_phone_number(phone: str) -> bool:
    """验证手机号格式

    支持中国大陆手机号格式验证（以1开头的11位数字）

    Args:
        phone: 待验证的手机号字符串

    Returns:
        格式正确返回True，否则返回False
    """
    if not phone:
        return False

    # 中国大陆手机号正则：1[3-9]开头的11位数字
    pattern = r"^1[3-9]\d{9}$"
    return bool(re.match(pattern, phone))


def generate_verification_code(length: int = 6) -> str:
    """生成指定位数的数字验证码

    生成由指定位数随机数字组成的验证码字符串。

    Args:
        length: 验证码位数，默认6位

    Returns:
        数字验证码字符串

    Example:
        >>> generate_verification_code(4)
        '8523'
        >>> generate_verification_code(6)
        '584921'
    """
    if length < 1:
        length = 6

    code = "".join(str(random.randint(0, 9)) for _ in range(length))
    return code


def get_redis_key(phone: str, key_type: str = "code") -> str:
    """生成Redis存储的键名

    根据手机号和键类型生成对应的Redis键名。

    Args:
        phone: 手机号
        key_type: 键类型（code表示验证码，time表示发送时间）

    Returns:
        Redis键名字符串

    Example:
        >>> get_redis_key("13800138000", "code")
        'sms:code:13800138000'
        >>> get_redis_key("13800138000", "time")
        'sms:time:13800138000'
    """
    return f"sms:{key_type}:{phone}"


async def get_last_send_time(phone: str) -> float | None:
    """获取手机号上次发送验证码的时间

    Args:
        phone: 手机号

    Returns:
        上次发送的时间戳（秒），如果不存在返回None
    """
    try:
        key = get_redis_key(phone, "time")
        last_time_str = await redis_client.get(key)

        if last_time_str:
            return float(last_time_str)
        return None
    except RedisError as e:
        log.error(f"获取验证码发送时间失败: {e}")
        return None


async def save_verification_code(
    phone: str, code: str, expire_minutes: int = 6
) -> None:
    """保存验证码到Redis

    Args:
        phone: 手机号
        code: 验证码
        expire_minutes: 过期时间（分钟）
    """
    try:
        code_key = get_redis_key(phone, "code")
        time_key = get_redis_key(phone, "time")

        # 保存验证码，设置过期时间
        await redis_client.setex(code_key, expire_minutes * 60, code)

        # 记录发送时间
        await redis_client.setex(
            time_key, settings.VERIFICATION_CODE_INTERVAL_MINUTES * 60, str(time.time())
        )

        log.info(f"验证码已保存至Redis: phone={phone}, code={code}")
    except RedisError as e:
        log.error(f"保存验证码失败: {e}")
        raise


async def verify_code(phone: str, code: str) -> bool:
    """验证验证码是否正确

    Args:
        phone: 手机号
        code: 待验证的验证码

    Returns:
        验证码正确返回True，否则返回False
    """
    try:
        key = get_redis_key(phone, "code")
        saved_code = await redis_client.get(key)

        if saved_code and saved_code == code:
            # 验证成功后删除验证码，防止重复使用
            await redis_client.delete(key)
            return True

        return False
    except RedisError as e:
        log.error(f"验证码验证失败: {e}")
        return False


class AuthService:
    @staticmethod
    async def validate_token(token: str) -> TokenInfo | None:
        """验证Token是否有效

        从Redis中检查Token是否存在且有效。

        Args:
            token: 待验证的Token字符串

        Returns:
            如果Token有效，返回TokenInfo模型；否则返回None
        """
        try:
            key = get_token_redis_key(token)
            value = await redis_client.get(key)

            if value:
                # 解析存储的值
                parts = value.split(":")
                if len(parts) == 2:
                    user_id = parts[0]
                    phone = parts[1]
                    # 获取过期时间
                    ttl = await redis_client.ttl(key)
                    if ttl > 0:
                        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)
                        return TokenInfo(
                            user_id=user_id,
                            phone=phone,
                            token=token,
                            created_at=datetime.now(timezone.utc),
                            expires_at=expires_at,
                        )
            return None
        except RedisError as e:
            log.error(f"验证Token失败: {e}")
            return None

    @staticmethod
    async def delete_token(token: str) -> bool:
        """删除Token（登出时使用）

        Args:
            token: 要删除的Token字符串

        Returns:
            删除成功返回True，否则返回False
        """
        try:
            key = get_token_redis_key(token)
            result = await redis_client.delete(key)
            log.info(f"Token已删除: key={key}, success={result > 0}")
            return result > 0
        except RedisError as e:
            log.error(f"删除Token失败: {e}")
            return False

    @staticmethod
    async def login(
        db_session: Session, phone: str, verification_code: str
    ) -> LoginResult:
        """用户登录主逻辑

        完整的登录流程：
        1. 校验手机号格式
        2. 验证验证码是否正确
        3. 根据手机号查询用户
        4. 生成Token
        5. 将Token保存到Redis
        6. 返回LoginResult结果

        Args:
            db_session: 数据库会话
            phone: 用户手机号
            verification_code: 6位验证码

        Returns:
            LoginResult: 登录结果数据模型

        Raises:
            InvalidVerificationCodeError: 验证码错误
            UserNotFoundError: 用户不存在
        """
        log.info(f"开始登录流程: phone={phone}")

        # 1. 验证验证码
        is_valid = await verify_code(phone, verification_code)

        if not is_valid:
            log.warning(f"验证码验证失败: phone={phone}")
            raise errors.CustomError(error=errors.CustomErrorCode.CAPTCHA_ERROR)

        # 2. 根据手机号查询用户
        user = user_dao.get_user_by_phone(db_session, phone)
        if user is None:
            log.info(f"用户不存在，自动创建新用户: phone={phone}")
            # 用户不存在，创建新用户
            user_name = f"用户{phone[-4:]}"  # 使用手机号后4位作为默认用户名
            user = user_dao.create(db_session, user_name, phone)
            # db_session.commit()
            # log.info(f"新用户创建成功: user_id={user.user_id}, phone={phone}")

        # 3. 生成Token
        token = generate_token(user.user_id)

        # 4. 将Token保存到Redis
        await save_token_to_redis(token, user.user_id, user.phone or phone)

        log.info(f"登录成功: user_id={user.user_id}, phone={phone}")

        # 5. 计算过期时间
        created_at = datetime.now(timezone.utc)
        expires_at = created_at + timedelta(days=settings.TOKEN_EXPIRE_DAYS)

        # 6. 构建并返回LoginResult
        token_info = TokenInfo(
            user_id=user.user_id,
            phone=user.phone or phone,
            token=token,
            created_at=created_at,
            expires_at=expires_at,
        )

        return LoginResult(
            success=True,
            message="登录成功",
            user_id=user.user_id,
            user_name=user.user_name,
            token_info=token_info,
            phone=user.phone,
        )

    @staticmethod
    async def send_verification_code(phone: str) -> SendVerificationCodeResponse:
        """发送验证码主逻辑

        完整的验证码发送流程：
        1. 校验手机号格式
        2. 检查发送间隔（5分钟内不能重复发送）
        3. 生成6位随机验证码
        4. 保存验证码到Redis（6分钟过期）
        5. 调用短信服务API发送验证码
        6. 返回发送结果

        Args:
            phone: 接收验证码的手机号

        Returns:
            发送结果字典，包含success和message字段

        Raises:
            InvalidPhoneNumberError: 手机号格式不正确
            VerificationCodeIntervalError: 发送间隔限制
            SMSServiceError: 短信服务调用失败
        """
        # 1. 校验手机号格式
        if not validate_phone_number(phone):
            log.warning(f"手机号格式不正确: {phone}")
            raise errors.CustomError(
                error=errors.CustomErrorCode.INVALID_PHONE_NUMBER_ERROR
            )

        # 2. 检查发送间隔
        last_send_time = await get_last_send_time(phone)
        if last_send_time:
            elapsed_seconds = time.time() - last_send_time
            interval_seconds = settings.VERIFICATION_CODE_INTERVAL_MINUTES * 60

            if elapsed_seconds < interval_seconds:
                remaining_seconds = int(interval_seconds - elapsed_seconds)
                log.warning(
                    f"验证码发送过于频繁: phone={phone}, elapsed={elapsed_seconds}s"
                )
                raise errors.VerificationCodeIntervalError(
                    remaining_seconds=remaining_seconds
                )

        # 3. 生成6位验证码
        code_length = settings.VERIFICATION_CODE_LENGTH
        code = generate_verification_code(code_length)
        # code = "888888"
        # log.info(f"验证码已生成: phone={phone}, code={code}")
        print(f"验证码已生成: phone={phone}, code={code}")

        # 4. 保存验证码到Redis
        expire_minutes = settings.VERIFICATION_CODE_EXPIRE_MINUTES
        await save_verification_code(phone, code, expire_minutes)

        # 5. 调用短信服务API发送验证码
        await sms_service.send_sms(phone, settings.SMS_TEMPLATE_CODE, code)

        # 6. 返回成功结果
        return SendVerificationCodeResponse(
            success=True,
            msg="验证码发送成功",
            phone=phone,
            expire_minutes=expire_minutes,
        )


auth_service = AuthService()
