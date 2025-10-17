"""OAuth Authentication API Endpoints"""

from datetime import datetime, timezone
from typing import Any, TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.oauth_config import OAuthConfig
from app.models.user import User
from app.schemas.oauth import (
    OAuthCallbackResponse,
    OAuthLoginResponse,
)
from app.utils.oauth_service import OAuthService
from app.utils.security import create_access_token, create_refresh_token
from app.utils.logging_utils import log_login_attempt
from app.utils.admin_notification_service import AdminNotificationService

if TYPE_CHECKING:
    from app.utils.dependencies import get_current_user
else:
    # Import at module level to avoid runtime circular import issues
    from app.utils.dependencies import get_current_user

router = APIRouter()


# In-memory state storage (in production, use Redis with TTL)
# Format: {state: {provider: str, timestamp: datetime, redirect_url: str}}
_oauth_states: dict[str, dict[str, Any]] = {}


@router.post("/oauth/{provider}/login", response_model=OAuthLoginResponse)
async def oauth_login(
    provider: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> OAuthLoginResponse:
    """
    Initiate OAuth login flow
    Returns authorization URL to redirect user to OAuth provider
    """
    # Get OAuth configuration
    result = await db.execute(
        select(OAuthConfig).filter(
            OAuthConfig.provider == provider.lower(),
            OAuthConfig.enabled == True
        )
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OAuth provider '{provider}' is not configured or enabled"
        )

    # Get OAuth provider instance
    oauth_provider = OAuthService.get_provider(config)

    # Generate state for CSRF protection
    state = oauth_provider.generate_state()

    # Store state (in production, use Redis with 10-minute TTL)
    _oauth_states[state] = {
        "provider": provider.lower(),
        "timestamp": datetime.now(timezone.utc),
        "redirect_url": request.headers.get("referer", "/")
    }

    # Clean up old states (older than 10 minutes)
    datetime.now(timezone.utc)
    _oauth_states.clear()  # Simple cleanup - in production use Redis EXPIRE

    # Generate authorization URL
    authorization_url = oauth_provider.get_authorization_url(state)

    return OAuthLoginResponse(
        authorization_url=authorization_url,
        state=state
    )


@router.get("/oauth/{provider}/callback", response_model=OAuthCallbackResponse)
async def oauth_callback(
    provider: str,
    code: str,
    state: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> OAuthCallbackResponse:
    """
    OAuth callback endpoint
    Handles the redirect from OAuth provider after user authorization
    """
    # Validate state (CSRF protection)
    stored_state = _oauth_states.get(state)
    if not stored_state or stored_state["provider"] != provider.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter. Possible CSRF attack."
        )

    # Remove used state
    _oauth_states.pop(state, None)

    # Get OAuth configuration
    result = await db.execute(
        select(OAuthConfig).filter(
            OAuthConfig.provider == provider.lower(),
            OAuthConfig.enabled == True
        )
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OAuth provider '{provider}' is not configured"
        )

    # Get OAuth provider instance
    oauth_provider = OAuthService.get_provider(config)

    try:
        # Exchange code for access token
        token_data = await oauth_provider.exchange_code_for_token(code)
        access_token_oauth = token_data.get("access_token")

        if not access_token_oauth:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to obtain access token from OAuth provider"
            )

        # Get user info from OAuth provider
        user_info = await oauth_provider.get_user_info(access_token_oauth)

        if not user_info.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by OAuth provider"
            )

        # Find or create user
        result = await db.execute(
            select(User).filter(
                User.oauth_provider == provider.lower(),
                User.oauth_id == user_info.provider_user_id
            )
        )
        user = result.scalar_one_or_none()

        if not user:
            # Check if user exists with same email
            result = await db.execute(
                select(User).filter(User.email == user_info.email)
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                # Link OAuth account to existing user
                existing_user.oauth_provider = provider.lower()
                existing_user.oauth_id = user_info.provider_user_id
                existing_user.oauth_email = user_info.email
                existing_user.oauth_avatar = user_info.avatar_url
                if user_info.verified_email:
                    existing_user.is_verified = True
                user = existing_user
            else:
                # Create new user
                username = user_info.email.split("@")[0]
                # Ensure unique username
                base_username = username
                counter = 1
                while True:
                    result = await db.execute(
                        select(User).filter(User.username == username)
                    )
                    if not result.scalar_one_or_none():
                        break
                    username = f"{base_username}{counter}"
                    counter += 1

                user = User(
                    email=user_info.email,
                    username=username,
                    full_name=user_info.full_name,
                    avatar=user_info.avatar_url,
                    oauth_provider=provider.lower(),
                    oauth_id=user_info.provider_user_id,
                    oauth_email=user_info.email,
                    oauth_avatar=user_info.avatar_url,
                    is_verified=user_info.verified_email,
                    is_active=True,
                    hashed_password=None  # OAuth users don't have password
                )
                db.add(user)

                # Send notification to admins about new OAuth user
                try:
                    await AdminNotificationService.notify_new_user_registration(
                        db=db,
                        user_id=user.id,
                        username=user.username,
                        email=user.email,
                    )
                except Exception as e:
                    print(f"Failed to send new user notification: {e}")

        # Update last login
        user.last_login_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(user)

        # Log successful login
        await log_login_attempt(
            db=db,
            user_type="user",
            status="success",
            request=request,
            user_id=user.id,
            username=user.username,
            email=user.email,
        )

        # Create JWT tokens
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        return OAuthCallbackResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user={
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "avatar": user.avatar,
                "is_verified": user.is_verified,
                "oauth_provider": user.oauth_provider,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        # Log failed login
        await log_login_attempt(
            db=db,
            user_type="user",
            status="failed",
            request=request,
            failure_reason=f"OAuth error: {str(e)}",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth authentication failed: {str(e)}"
        )


@router.post("/oauth/{provider}/unlink")
async def oauth_unlink(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Unlink OAuth account from user
    Requires user to have a password set before unlinking
    """
    if current_user.oauth_provider != provider.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User is not linked to {provider}"
        )

    # Check if user has a password (can't unlink if no password)
    if not current_user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please set a password before unlinking OAuth account"
        )

    # Unlink OAuth account
    current_user.oauth_provider = None
    current_user.oauth_id = None
    current_user.oauth_email = None
    current_user.oauth_avatar = None

    await db.commit()

    return {"success": True, "message": f"{provider.title()} account unlinked successfully"}
