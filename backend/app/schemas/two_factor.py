"""
Pydantic schemas for Two-Factor Authentication (2FA)
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TwoFactorSetupRequest(BaseModel):
    """Request to initiate 2FA setup"""

    pass  # No input needed, will use current admin user


class TwoFactorSetupResponse(BaseModel):
    """Response containing QR code and secret for 2FA setup"""

    secret: str = Field(..., description="TOTP secret (for manual entry)")
    qr_code: str = Field(..., description="Base64-encoded QR code image")
    backup_codes: List[str] = Field(..., description="Backup codes for account recovery")


class TwoFactorVerifyRequest(BaseModel):
    """Request to verify and enable 2FA"""

    token: str = Field(..., min_length=6, max_length=6, description="6-digit TOTP token")


class TwoFactorVerifyResponse(BaseModel):
    """Response after successful 2FA verification"""

    enabled: bool = Field(..., description="Whether 2FA is now enabled")
    backup_codes: List[str] = Field(..., description="Backup codes (save these!)")
    verified_at: datetime = Field(..., description="Timestamp of verification")


class TwoFactorDisableRequest(BaseModel):
    """Request to disable 2FA"""

    password: str = Field(..., description="Current password for verification")
    token: Optional[str] = Field(None, min_length=6, max_length=6, description="6-digit TOTP token or backup code")


class TwoFactorDisableResponse(BaseModel):
    """Response after disabling 2FA"""

    disabled: bool = Field(..., description="Whether 2FA was disabled")


class TwoFactorStatusResponse(BaseModel):
    """Response containing current 2FA status"""

    enabled: bool = Field(..., description="Whether 2FA is enabled")
    verified_at: Optional[datetime] = Field(None, description="When 2FA was last verified")
    backup_codes_remaining: int = Field(0, description="Number of unused backup codes")


class TwoFactorLoginRequest(BaseModel):
    """Request to complete 2FA during login"""

    email: str = Field(..., description="Email address")
    password: str = Field(..., description="Password")
    token: str = Field(..., min_length=4, max_length=10, description="6-digit TOTP token or backup code (XXXX-XXXX)")
    captcha_id: str = Field(..., description="Captcha ID")
    captcha_code: str = Field(..., min_length=4, max_length=4, description="Captcha code")


class RegenerateBackupCodesRequest(BaseModel):
    """Request to regenerate backup codes"""

    password: str = Field(..., description="Current password for verification")


class RegenerateBackupCodesResponse(BaseModel):
    """Response with new backup codes"""

    backup_codes: List[str] = Field(..., description="New backup codes")
