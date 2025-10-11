"""
Captcha schemas
"""

from pydantic import BaseModel, Field


class CaptchaResponse(BaseModel):
    """Captcha response schema"""

    captcha_id: str = Field(..., description="Captcha ID")
    image_url: str = Field(..., description="Captcha image URL")


class CaptchaValidateRequest(BaseModel):
    """Captcha validation request schema"""

    captcha_id: str = Field(..., description="Captcha ID")
    captcha_code: str = Field(
        ..., min_length=4, max_length=4, description="Captcha code"
    )
