"""OAuth Service for Google, Facebook, and other providers"""

import secrets
from abc import ABC, abstractmethod
from typing import Optional
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, status

from app.models.oauth_config import OAuthConfig
from app.schemas.oauth import OAuthUserInfo


class OAuthProviderBase(ABC):
    """Base class for OAuth providers"""

    def __init__(self, config: OAuthConfig):
        self.config = config
        self.client_id = config.client_id
        self.client_secret = config.client_secret
        self.redirect_uri = config.redirect_uri
        self.scopes = config.scopes or []

    @abstractmethod
    def get_authorization_url(self, state: str) -> str:
        """Generate authorization URL for OAuth flow"""
        pass

    @abstractmethod
    async def exchange_code_for_token(self, code: str) -> dict:
        """Exchange authorization code for access token"""
        pass

    @abstractmethod
    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """Get user information from OAuth provider"""
        pass

    def generate_state(self) -> str:
        """Generate secure random state for CSRF protection"""
        return secrets.token_urlsafe(32)


class GoogleOAuthProvider(OAuthProviderBase):
    """Google OAuth 2.0 Provider"""

    def __init__(self, config: OAuthConfig):
        super().__init__(config)
        self.authorization_url = config.authorization_url or "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = config.token_url or "https://oauth2.googleapis.com/token"
        self.userinfo_url = config.userinfo_url or "https://www.googleapis.com/oauth2/v2/userinfo"

        # Default scopes if not configured
        if not self.scopes:
            self.scopes = [
                "openid",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile"
            ]

    def get_authorization_url(self, state: str) -> str:
        """Generate Google OAuth authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "state": state,
            "access_type": "offline",  # Request refresh token
            "prompt": "consent"  # Force consent screen to get refresh token
        }
        return f"{self.authorization_url}?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str) -> dict:
        """Exchange authorization code for Google access token"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.token_url,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "code": code,
                        "grant_type": "authorization_code",
                        "redirect_uri": self.redirect_uri,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to exchange code for token: {e.response.text}"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"OAuth token exchange failed: {str(e)}"
                )

    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """Get user information from Google"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.userinfo_url,
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                response.raise_for_status()
                data = response.json()

                return OAuthUserInfo(
                    provider="google",
                    provider_user_id=data.get("id"),
                    email=data.get("email"),
                    full_name=data.get("name"),
                    avatar_url=data.get("picture"),
                    verified_email=data.get("verified_email", False),
                    raw_data=data
                )
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to get user info: {e.response.text}"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to retrieve user info: {str(e)}"
                )


class FacebookOAuthProvider(OAuthProviderBase):
    """Facebook OAuth 2.0 Provider"""

    def __init__(self, config: OAuthConfig):
        super().__init__(config)
        self.authorization_url = config.authorization_url or "https://www.facebook.com/v18.0/dialog/oauth"
        self.token_url = config.token_url or "https://graph.facebook.com/v18.0/oauth/access_token"
        self.userinfo_url = config.userinfo_url or "https://graph.facebook.com/me"

        # Default scopes if not configured
        if not self.scopes:
            self.scopes = ["email", "public_profile"]

    def get_authorization_url(self, state: str) -> str:
        """Generate Facebook OAuth authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": ",".join(self.scopes),
            "state": state,
        }
        return f"{self.authorization_url}?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str) -> dict:
        """Exchange authorization code for Facebook access token"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.token_url,
                    params={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "code": code,
                        "redirect_uri": self.redirect_uri,
                    }
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to exchange code for token: {e.response.text}"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"OAuth token exchange failed: {str(e)}"
                )

    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """Get user information from Facebook"""
        async with httpx.AsyncClient() as client:
            try:
                # Request specific fields
                fields = "id,email,name,picture.type(large)"
                response = await client.get(
                    self.userinfo_url,
                    params={
                        "fields": fields,
                        "access_token": access_token
                    }
                )
                response.raise_for_status()
                data = response.json()

                # Extract picture URL
                avatar_url = None
                if "picture" in data and "data" in data["picture"]:
                    avatar_url = data["picture"]["data"].get("url")

                return OAuthUserInfo(
                    provider="facebook",
                    provider_user_id=data.get("id"),
                    email=data.get("email"),
                    full_name=data.get("name"),
                    avatar_url=avatar_url,
                    verified_email=True,  # Facebook emails are verified
                    raw_data=data
                )
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to get user info: {e.response.text}"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to retrieve user info: {str(e)}"
                )


class OAuthService:
    """OAuth Service Manager"""

    @staticmethod
    def get_provider(config: OAuthConfig) -> OAuthProviderBase:
        """Get OAuth provider instance based on configuration"""
        provider_map = {
            "google": GoogleOAuthProvider,
            "facebook": FacebookOAuthProvider,
        }

        provider_class = provider_map.get(config.provider.lower())
        if not provider_class:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported OAuth provider: {config.provider}"
            )

        return provider_class(config)

    @staticmethod
    async def validate_config(config: OAuthConfig) -> tuple[bool, Optional[str]]:
        """Validate OAuth configuration by testing authorization URL generation"""
        try:
            provider = OAuthService.get_provider(config)
            state = provider.generate_state()
            auth_url = provider.get_authorization_url(state)

            # Basic validation
            if not auth_url or not auth_url.startswith("http"):
                return False, "Invalid authorization URL generated"

            return True, "Configuration is valid"
        except Exception as e:
            return False, f"Configuration validation failed: {str(e)}"
