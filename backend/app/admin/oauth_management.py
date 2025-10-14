"""OAuth Management API for Admin"""

from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.oauth_config import OAuthConfig
from app.models.user import AdminUser
from app.schemas.oauth import (
    OAuthConfigCreate,
    OAuthConfigPublicResponse,
    OAuthConfigResponse,
    OAuthConfigUpdate,
    OAuthTestResponse,
)
from app.utils.dependencies import get_current_superadmin
from app.utils.oauth_service import OAuthService

router = APIRouter()


@router.get("/oauth/configs", response_model=List[OAuthConfigResponse])
async def get_oauth_configs(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_superadmin),
):
    """Get all OAuth configurations (superadmin only)"""
    result = await db.execute(select(OAuthConfig))
    configs = result.scalars().all()

    # Mask client secrets in response
    response_configs = []
    for config in configs:
        config_dict = {
            "id": config.id,
            "provider": config.provider,
            "client_id": config.client_id,
            "client_secret": _mask_secret(config.client_secret),
            "redirect_uri": config.redirect_uri,
            "scopes": config.scopes,
            "authorization_url": config.authorization_url,
            "token_url": config.token_url,
            "userinfo_url": config.userinfo_url,
            "extra_config": config.extra_config,
            "enabled": config.enabled,
            "last_test_at": config.last_test_at,
            "last_test_status": config.last_test_status,
            "last_test_message": config.last_test_message,
            "created_at": config.created_at,
            "updated_at": config.updated_at,
        }
        response_configs.append(config_dict)

    return response_configs


@router.get("/oauth/configs/public", response_model=List[OAuthConfigPublicResponse])
async def get_public_oauth_configs(
    db: AsyncSession = Depends(get_db),
):
    """Get public OAuth configurations (no authentication required)"""
    result = await db.execute(
        select(OAuthConfig).filter(OAuthConfig.enabled == True)
    )
    configs = result.scalars().all()
    return configs


@router.get("/oauth/configs/{provider}", response_model=OAuthConfigResponse)
async def get_oauth_config(
    provider: str,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_superadmin),
):
    """Get OAuth configuration for specific provider"""
    result = await db.execute(
        select(OAuthConfig).filter(OAuthConfig.provider == provider.lower())
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OAuth configuration for '{provider}' not found"
        )

    config_dict = {
        "id": config.id,
        "provider": config.provider,
        "client_id": config.client_id,
        "client_secret": _mask_secret(config.client_secret),
        "redirect_uri": config.redirect_uri,
        "scopes": config.scopes,
        "authorization_url": config.authorization_url,
        "token_url": config.token_url,
        "userinfo_url": config.userinfo_url,
        "extra_config": config.extra_config,
        "enabled": config.enabled,
        "last_test_at": config.last_test_at,
        "last_test_status": config.last_test_status,
        "last_test_message": config.last_test_message,
        "created_at": config.created_at,
        "updated_at": config.updated_at,
    }
    return config_dict


@router.post("/oauth/configs", response_model=OAuthConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_oauth_config(
    config_data: OAuthConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_superadmin),
):
    """Create new OAuth configuration"""
    # Check if provider already exists
    result = await db.execute(
        select(OAuthConfig).filter(OAuthConfig.provider == config_data.provider.lower())
    )
    existing_config = result.scalar_one_or_none()

    if existing_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth configuration for '{config_data.provider}' already exists"
        )

    # Create new configuration
    new_config = OAuthConfig(
        provider=config_data.provider.lower(),
        client_id=config_data.client_id,
        client_secret=config_data.client_secret,
        redirect_uri=config_data.redirect_uri,
        scopes=config_data.scopes,
        authorization_url=config_data.authorization_url,
        token_url=config_data.token_url,
        userinfo_url=config_data.userinfo_url,
        extra_config=config_data.extra_config,
        enabled=config_data.enabled,
    )

    db.add(new_config)
    await db.commit()
    await db.refresh(new_config)

    return new_config


@router.put("/oauth/configs/{provider}", response_model=OAuthConfigResponse)
async def update_oauth_config(
    provider: str,
    config_data: OAuthConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_superadmin),
):
    """Update OAuth configuration"""
    result = await db.execute(
        select(OAuthConfig).filter(OAuthConfig.provider == provider.lower())
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OAuth configuration for '{provider}' not found"
        )

    # Update fields
    update_data = config_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)

    config.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(config)

    config_dict = {
        "id": config.id,
        "provider": config.provider,
        "client_id": config.client_id,
        "client_secret": _mask_secret(config.client_secret),
        "redirect_uri": config.redirect_uri,
        "scopes": config.scopes,
        "authorization_url": config.authorization_url,
        "token_url": config.token_url,
        "userinfo_url": config.userinfo_url,
        "extra_config": config.extra_config,
        "enabled": config.enabled,
        "last_test_at": config.last_test_at,
        "last_test_status": config.last_test_status,
        "last_test_message": config.last_test_message,
        "created_at": config.created_at,
        "updated_at": config.updated_at,
    }
    return config_dict


@router.delete("/oauth/configs/{provider}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_oauth_config(
    provider: str,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_superadmin),
):
    """Delete OAuth configuration"""
    result = await db.execute(
        select(OAuthConfig).filter(OAuthConfig.provider == provider.lower())
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OAuth configuration for '{provider}' not found"
        )

    await db.delete(config)
    await db.commit()

    return None


@router.post("/oauth/configs/{provider}/test", response_model=OAuthTestResponse)
async def test_oauth_config(
    provider: str,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_superadmin),
):
    """Test OAuth configuration"""
    result = await db.execute(
        select(OAuthConfig).filter(OAuthConfig.provider == provider.lower())
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OAuth configuration for '{provider}' not found"
        )

    # Validate configuration
    is_valid, message = await OAuthService.validate_config(config)

    # Update test status
    config.last_test_at = datetime.now(timezone.utc)
    config.last_test_status = "success" if is_valid else "failed"
    config.last_test_message = message

    await db.commit()

    # Generate test authorization URL
    authorization_url = None
    if is_valid:
        try:
            oauth_provider = OAuthService.get_provider(config)
            state = oauth_provider.generate_state()
            authorization_url = oauth_provider.get_authorization_url(state)
        except Exception as e:
            message = f"Failed to generate authorization URL: {str(e)}"
            is_valid = False

    return OAuthTestResponse(
        success=is_valid,
        message=message,
        authorization_url=authorization_url,
        details={
            "provider": config.provider,
            "client_id": config.client_id,
            "redirect_uri": config.redirect_uri,
            "scopes": config.scopes,
        }
    )


def _mask_secret(secret: str) -> str:
    """Mask client secret for security"""
    if not secret or len(secret) <= 8:
        return "********"
    return secret[:4] + "*" * (len(secret) - 8) + secret[-4:]
