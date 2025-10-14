"""OAuth Schemas for authentication and configuration"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ==================== OAuth Configuration Schemas ====================

class OAuthConfigBase(BaseModel):
    """Base OAuth configuration schema"""
    provider: str = Field(..., description="Provider name (google, facebook, etc.)")
    client_id: str = Field(..., description="OAuth client ID")
    client_secret: str = Field(..., description="OAuth client secret")
    redirect_uri: Optional[str] = Field(None, description="OAuth redirect URI")
    scopes: Optional[list[str]] = Field(default=[], description="OAuth scopes")
    authorization_url: Optional[str] = None
    token_url: Optional[str] = None
    userinfo_url: Optional[str] = None
    extra_config: Optional[dict] = Field(default={}, description="Additional provider-specific config")
    enabled: bool = Field(default=False, description="Whether this provider is enabled")


class OAuthConfigCreate(OAuthConfigBase):
    """Schema for creating OAuth configuration"""
    pass


class OAuthConfigUpdate(BaseModel):
    """Schema for updating OAuth configuration"""
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    redirect_uri: Optional[str] = None
    scopes: Optional[list[str]] = None
    authorization_url: Optional[str] = None
    token_url: Optional[str] = None
    userinfo_url: Optional[str] = None
    extra_config: Optional[dict] = None
    enabled: Optional[bool] = None


class OAuthConfigResponse(OAuthConfigBase):
    """Schema for OAuth configuration response"""
    id: int
    client_secret: str = Field(..., description="Client secret (masked in response)")
    last_test_at: Optional[datetime] = None
    last_test_status: Optional[str] = None
    last_test_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @classmethod
    def mask_secret(cls, secret: str) -> str:
        """Mask the client secret for security"""
        if not secret or len(secret) <= 8:
            return "********"
        return secret[:4] + "*" * (len(secret) - 8) + secret[-4:]


class OAuthConfigPublicResponse(BaseModel):
    """Public OAuth configuration (without secrets)"""
    id: int
    provider: str
    enabled: bool
    scopes: Optional[list[str]] = []
    redirect_uri: Optional[str] = None

    class Config:
        from_attributes = True


# ==================== OAuth Authentication Schemas ====================

class OAuthLoginRequest(BaseModel):
    """Schema for initiating OAuth login"""
    provider: str = Field(..., description="Provider name (google, facebook)")
    redirect_url: Optional[str] = Field(None, description="Frontend redirect URL after successful login")


class OAuthLoginResponse(BaseModel):
    """Schema for OAuth login response"""
    authorization_url: str = Field(..., description="URL to redirect user for OAuth authorization")
    state: str = Field(..., description="CSRF protection state parameter")


class OAuthCallbackRequest(BaseModel):
    """Schema for OAuth callback"""
    code: str = Field(..., description="Authorization code from OAuth provider")
    state: str = Field(..., description="State parameter for CSRF protection")


class OAuthCallbackResponse(BaseModel):
    """Schema for OAuth callback response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict  # UserResponse but keeping as dict to avoid circular imports


class OAuthUserInfo(BaseModel):
    """Schema for user info from OAuth provider"""
    provider: str
    provider_user_id: str
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    verified_email: bool = False
    raw_data: Optional[dict] = None  # Store raw response for debugging


# ==================== OAuth Test Schemas ====================

class OAuthTestRequest(BaseModel):
    """Schema for testing OAuth configuration"""
    test_authorization: bool = Field(default=True, description="Test authorization URL generation")


class OAuthTestResponse(BaseModel):
    """Schema for OAuth test response"""
    success: bool
    message: str
    details: Optional[dict] = None
    authorization_url: Optional[str] = None


# ==================== OAuth Unlink Schema ====================

class OAuthUnlinkRequest(BaseModel):
    """Schema for unlinking OAuth account"""
    provider: str = Field(..., description="Provider to unlink")


class OAuthUnlinkResponse(BaseModel):
    """Schema for OAuth unlink response"""
    success: bool
    message: str
