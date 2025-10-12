"""
Password Reset Verification Code Manager
Uses Redis to store and validate verification codes
"""
import secrets
from datetime import timedelta
from typing import Optional

from app.utils.cache import get_redis


class ResetCodeManager:
    """Manage password reset verification codes"""

    CODE_LENGTH = 6
    CODE_EXPIRY_MINUTES = 15  # 验证码15分钟过期
    MAX_ATTEMPTS = 5  # 最多尝试5次

    @staticmethod
    def _get_code_key(email: str) -> str:
        """Get Redis key for verification code"""
        return f"reset_code:{email}"

    @staticmethod
    def _get_attempts_key(email: str) -> str:
        """Get Redis key for attempt counter"""
        return f"reset_attempts:{email}"

    @staticmethod
    def generate_code() -> str:
        """Generate a 6-digit verification code"""
        return "".join([str(secrets.randbelow(10)) for _ in range(ResetCodeManager.CODE_LENGTH)])

    @classmethod
    async def create_and_store_code(cls, email: str) -> str:
        """
        Create a verification code and store it in Redis

        Args:
            email: User's email address

        Returns:
            The generated verification code
        """
        redis = await get_redis()
        code = cls.generate_code()

        # Store code with expiry
        code_key = cls._get_code_key(email)
        await redis.setex(
            code_key,
            timedelta(minutes=cls.CODE_EXPIRY_MINUTES),
            code
        )

        # Reset attempt counter
        attempts_key = cls._get_attempts_key(email)
        await redis.setex(
            attempts_key,
            timedelta(minutes=cls.CODE_EXPIRY_MINUTES),
            "0"
        )

        return code

    @classmethod
    async def validate_code(cls, email: str, code: str) -> bool:
        """
        Validate a verification code

        Args:
            email: User's email address
            code: The code to validate

        Returns:
            True if code is valid, False otherwise
        """
        redis = await get_redis()

        # Check attempts
        attempts_key = cls._get_attempts_key(email)
        attempts_str = await redis.get(attempts_key)

        if attempts_str is None:
            # Code has expired or doesn't exist
            return False

        attempts = int(attempts_str)
        if attempts >= cls.MAX_ATTEMPTS:
            # Too many failed attempts
            return False

        # Get stored code
        code_key = cls._get_code_key(email)
        stored_code = await redis.get(code_key)

        if stored_code is None:
            # Code has expired
            return False

        # Validate code
        if stored_code == code:
            # Code is valid - delete it to prevent reuse
            await redis.delete(code_key)
            await redis.delete(attempts_key)
            return True
        else:
            # Code is invalid - increment attempts
            await redis.incr(attempts_key)
            return False

    @classmethod
    async def delete_code(cls, email: str) -> None:
        """
        Delete a verification code and its attempts counter

        Args:
            email: User's email address
        """
        redis = await get_redis()
        code_key = cls._get_code_key(email)
        attempts_key = cls._get_attempts_key(email)

        await redis.delete(code_key)
        await redis.delete(attempts_key)

    @classmethod
    async def get_remaining_attempts(cls, email: str) -> Optional[int]:
        """
        Get remaining validation attempts

        Args:
            email: User's email address

        Returns:
            Number of remaining attempts, or None if code doesn't exist
        """
        redis = await get_redis()
        attempts_key = cls._get_attempts_key(email)
        attempts_str = await redis.get(attempts_key)

        if attempts_str is None:
            return None

        attempts = int(attempts_str)
        return max(0, cls.MAX_ATTEMPTS - attempts)


# Global instance
reset_code_manager = ResetCodeManager()
