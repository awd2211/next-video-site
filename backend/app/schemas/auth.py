from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegister(BaseModel):
    """User registration schema"""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = None

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """验证密码强度"""
        from app.utils.password_validator import validate_password_field

        return validate_password_field(v)


class UserLogin(BaseModel):
    """User login schema"""

    email: EmailStr
    password: str


class AdminLogin(BaseModel):
    """Admin login schema"""

    username: str
    password: str
    captcha_id: str = Field(..., description="Captcha ID")
    captcha_code: str = Field(
        ..., min_length=4, max_length=4, description="Captcha code"
    )


class TokenResponse(BaseModel):
    """Token response schema"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""

    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Password reset request schema - send verification code"""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirm schema - reset password with code"""

    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """验证密码强度"""
        from app.utils.password_validator import validate_password_field

        return validate_password_field(v)
