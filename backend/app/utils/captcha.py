"""
Captcha generation and validation utilities
"""

import uuid
from typing import Tuple

from captcha.image import ImageCaptcha

from app.utils.cache import get_redis


class CaptchaManager:
    """Manage captcha generation and validation"""

    def __init__(self):
        self.image_captcha = ImageCaptcha(width=160, height=60)
        self.captcha_expire_seconds = 300  # 5 minutes

    async def generate_captcha(self) -> Tuple[str, bytes]:
        """
        Generate a new captcha

        Returns:
            Tuple[str, bytes]: (captcha_id, image_bytes)
        """
        # Generate random captcha text (4 characters)
        import random
        import string
        import logging

        logger = logging.getLogger(__name__)

        captcha_text = "".join(
            random.choices(string.digits + string.ascii_uppercase, k=4)
        )

        # Generate captcha ID
        captcha_id = str(uuid.uuid4())

        # Store captcha text in Redis with expiration
        redis_client = await get_redis()
        cache_key = f"captcha:{captcha_id}"
        await redis_client.setex(cache_key, self.captcha_expire_seconds, captcha_text)

        logger.info(f"验证码生成成功 (captcha_id={captcha_id}, text={captcha_text}, expire_seconds={self.captcha_expire_seconds})")

        # Generate captcha image
        image = self.image_captcha.generate(captcha_text)
        image_bytes = image.read()

        return captcha_id, image_bytes

    async def validate_captcha(self, captcha_id: str, user_input: str) -> bool:
        """
        Validate a captcha

        Args:
            captcha_id: The captcha ID
            user_input: User's input

        Returns:
            bool: True if valid, False otherwise
        """
        import logging
        logger = logging.getLogger(__name__)

        if not captcha_id or not user_input:
            logger.warning(f"验证码验证失败: captcha_id或user_input为空 (captcha_id={captcha_id}, user_input={user_input})")
            return False

        redis_client = await get_redis()
        cache_key = f"captcha:{captcha_id}"

        # Get stored captcha text
        stored_text = await redis_client.get(cache_key)

        if not stored_text:
            logger.warning(f"验证码验证失败: Redis中未找到验证码 (captcha_id={captcha_id}, cache_key={cache_key})")
            return False

        # Delete captcha after validation (one-time use)
        await redis_client.delete(cache_key)

        # Compare (case-insensitive)
        # Handle both bytes and str (Redis 6.x returns str directly)
        if isinstance(stored_text, bytes):
            stored_text = stored_text.decode("utf-8")

        is_valid = stored_text.upper() == user_input.upper()
        if is_valid:
            logger.info(f"验证码验证成功 (captcha_id={captcha_id})")
        else:
            logger.warning(f"验证码验证失败: 验证码不匹配 (captcha_id={captcha_id}, expected={stored_text}, got={user_input})")

        return is_valid


# Singleton instance
captcha_manager = CaptchaManager()
