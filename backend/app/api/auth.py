from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.database import get_db
from app.models.user import User, AdminUser
from app.schemas.auth import UserRegister, UserLogin, AdminLogin, TokenResponse, RefreshTokenRequest
from app.schemas.user import UserResponse, AdminUserResponse
from app.utils.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.utils.dependencies import get_current_user, get_current_admin_user

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")  # 限制注册频率
async def register(
    request: Request,
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user"""
    # Check if email already exists
    result = await db.execute(select(User).filter(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check if username already exists
    result = await db.execute(select(User).filter(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    # Create new user
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")  # 限制登录频率，防止暴力破解
async def login(
    request: Request,
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """User login"""
    result = await db.execute(select(User).filter(User.email == credentials.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Update last login
    user.last_login_at = datetime.utcnow()
    await db.commit()

    # Create tokens (sub must be string per JWT spec)
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/admin/login", response_model=TokenResponse)
@limiter.limit("5/minute")  # 更严格的管理员登录限制
async def admin_login(
    request: Request,
    credentials: AdminLogin,
    db: AsyncSession = Depends(get_db),
):
    """Admin login with captcha verification"""
    # Validate captcha first
    from app.utils.captcha import captcha_manager

    is_valid = await captcha_manager.validate_captcha(
        credentials.captcha_id,
        credentials.captcha_code
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired captcha code",
        )

    result = await db.execute(select(AdminUser).filter(AdminUser.username == credentials.username))
    admin_user = result.scalar_one_or_none()

    if not admin_user or not verify_password(credentials.password, admin_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not admin_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive",
        )

    # Update last login
    admin_user.last_login_at = datetime.utcnow()
    await db.commit()

    # Create tokens with admin flag (sub must be string per JWT spec)
    access_token = create_access_token({"sub": str(admin_user.id), "is_admin": True})
    refresh_token = create_refresh_token({"sub": str(admin_user.id), "is_admin": True})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token"""
    payload = decode_token(token_data.refresh_token)

    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = payload.get("sub")
    is_admin = payload.get("is_admin", False)

    # Verify user still exists and is active
    if is_admin:
        result = await db.execute(select(AdminUser).filter(AdminUser.id == user_id))
        user = result.scalar_one_or_none()
    else:
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Create new tokens (sub must be string per JWT spec)
    token_payload = {"sub": str(user_id)}
    if is_admin:
        token_payload["is_admin"] = True

    access_token = create_access_token(token_payload)
    refresh_token_new = create_refresh_token(token_payload)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_new,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current user info"""
    return current_user


@router.get("/admin/me", response_model=AdminUserResponse)
async def get_current_admin_info(
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Get current admin user info"""
    return current_admin
