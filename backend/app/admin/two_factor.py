"""
Admin Two-Factor Authentication (2FA) API endpoints
"""

import base64
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import AdminUser
from app.schemas.auth import TokenResponse
from app.schemas.two_factor import (
    RegenerateBackupCodesRequest,
    RegenerateBackupCodesResponse,
    TwoFactorDisableRequest,
    TwoFactorDisableResponse,
    TwoFactorLoginRequest,
    TwoFactorSetupRequest,
    TwoFactorSetupResponse,
    TwoFactorStatusResponse,
    TwoFactorVerifyRequest,
    TwoFactorVerifyResponse,
)
from app.utils.dependencies import get_current_admin_user
from app.utils.logging_utils import log_login_attempt
from app.utils.rate_limit import AutoBanDetector, RateLimitPresets, limiter
from app.utils.security import create_access_token, create_refresh_token, verify_password
from app.utils.totp import totp_manager

router = APIRouter()


@router.get("/status", response_model=TwoFactorStatusResponse)
async def get_2fa_status(
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current 2FA status for the admin user
    """
    backup_codes_count = 0
    if current_admin.totp_enabled and current_admin.backup_codes:
        backup_codes_count = totp_manager.get_remaining_backup_codes_count(current_admin.backup_codes)

    return TwoFactorStatusResponse(
        enabled=current_admin.totp_enabled,
        verified_at=current_admin.totp_verified_at,
        backup_codes_remaining=backup_codes_count,
    )


@router.post("/setup", response_model=TwoFactorSetupResponse)
async def setup_2fa(
    request: TwoFactorSetupRequest,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Initiate 2FA setup - generates secret and QR code
    Does not enable 2FA until verification is complete
    """
    if current_admin.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is already enabled. Disable it first to set up again.",
        )

    # Generate new secret
    secret = totp_manager.generate_secret()

    # Generate QR code
    qr_code_bytes = totp_manager.generate_qr_code(secret, current_admin.email)
    qr_code_base64 = base64.b64encode(qr_code_bytes).decode()

    # Generate backup codes
    backup_codes = totp_manager.generate_backup_codes()

    # Store encrypted secret and backup codes (but don't enable yet)
    encrypted_secret = totp_manager.encrypt_secret(secret)
    encrypted_backup_codes = totp_manager.encrypt_backup_codes(backup_codes)

    current_admin.totp_secret = encrypted_secret
    current_admin.backup_codes = encrypted_backup_codes
    current_admin.totp_enabled = False  # Not enabled until verification

    await db.commit()

    return TwoFactorSetupResponse(
        secret=secret,
        qr_code=f"data:image/png;base64,{qr_code_base64}",
        backup_codes=backup_codes,
    )


@router.post("/verify", response_model=TwoFactorVerifyResponse)
async def verify_and_enable_2fa(
    request: TwoFactorVerifyRequest,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Verify TOTP token and enable 2FA
    """
    if current_admin.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is already enabled",
        )

    if not current_admin.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA setup not initiated. Call /setup first.",
        )

    # Verify the token
    is_valid = totp_manager.verify_token(current_admin.totp_secret, request.token)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code. Please try again.",
        )

    # Enable 2FA
    current_admin.totp_enabled = True
    current_admin.totp_verified_at = datetime.utcnow()

    await db.commit()
    await db.refresh(current_admin)

    # Return backup codes (decrypted for display)
    backup_codes = totp_manager.decrypt_backup_codes(current_admin.backup_codes)

    return TwoFactorVerifyResponse(
        enabled=True,
        backup_codes=backup_codes,
        verified_at=current_admin.totp_verified_at,
    )


@router.post("/disable", response_model=TwoFactorDisableResponse)
async def disable_2fa(
    request: TwoFactorDisableRequest,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Disable 2FA - requires password and optionally TOTP token
    """
    if not current_admin.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled",
        )

    # Verify password
    if not verify_password(request.password, current_admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    # If token provided, verify it
    if request.token:
        # Check if it's a backup code (format: XXXX-XXXX)
        if "-" in request.token:
            is_valid, _ = totp_manager.verify_backup_code(current_admin.backup_codes, request.token)
        else:
            # Regular TOTP token
            is_valid = totp_manager.verify_token(current_admin.totp_secret, request.token)

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code",
            )

    # Disable 2FA
    current_admin.totp_enabled = False
    current_admin.totp_secret = None
    current_admin.backup_codes = None
    current_admin.totp_verified_at = None

    await db.commit()

    return TwoFactorDisableResponse(disabled=True)


@router.post("/regenerate-backup-codes", response_model=RegenerateBackupCodesResponse)
async def regenerate_backup_codes(
    request: RegenerateBackupCodesRequest,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Regenerate backup codes - requires password verification
    """
    if not current_admin.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled",
        )

    # Verify password
    if not verify_password(request.password, current_admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    # Generate new backup codes
    new_backup_codes = totp_manager.generate_backup_codes()
    encrypted_backup_codes = totp_manager.encrypt_backup_codes(new_backup_codes)

    # Update database
    current_admin.backup_codes = encrypted_backup_codes
    await db.commit()

    return RegenerateBackupCodesResponse(backup_codes=new_backup_codes)


@router.post("/login-verify", response_model=TokenResponse)
@limiter.limit(RateLimitPresets.STRICT)  # 严格限流: 5/分钟
async def verify_2fa_login(
    request: Request,
    login_data: TwoFactorLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Complete 2FA login verification
    This is called after initial login when 2FA is enabled
    """
    from app.utils.captcha import captcha_manager

    # Validate captcha
    is_valid = await captcha_manager.validate_captcha(
        login_data.captcha_id, login_data.captcha_code
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired captcha code",
        )

    # Find admin user by email
    result = await db.execute(
        select(AdminUser).filter(AdminUser.email == login_data.email)
    )
    admin_user = result.scalar_one_or_none()

    if not admin_user or not verify_password(
        login_data.password, admin_user.hashed_password
    ):
        # Record failed attempt
        ip = request.client.host if request.client else "unknown"
        await AutoBanDetector.record_failed_attempt(ip, "admin_2fa_login")

        # Log failed login
        await log_login_attempt(
            db=db,
            user_type="admin",
            status="failed",
            request=request,
            email=login_data.email,
            failure_reason="Incorrect email or password",
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not admin_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive",
        )

    if not admin_user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled for this account",
        )

    # Verify 2FA token
    is_backup_code = "-" in login_data.token
    token_valid = False

    if is_backup_code:
        # Verify backup code
        token_valid, updated_codes = totp_manager.verify_backup_code(
            admin_user.backup_codes, login_data.token
        )
        if token_valid and updated_codes:
            # Update backup codes (remove used code)
            admin_user.backup_codes = updated_codes
            await db.commit()
    else:
        # Verify TOTP token
        token_valid = totp_manager.verify_token(admin_user.totp_secret, login_data.token)

    if not token_valid:
        # Record failed 2FA attempt
        ip = request.client.host if request.client else "unknown"
        await AutoBanDetector.record_failed_attempt(ip, "admin_2fa_verify")

        # Log failed 2FA verification
        await log_login_attempt(
            db=db,
            user_type="admin",
            status="failed",
            request=request,
            user_id=admin_user.id,
            username=admin_user.username,
            email=admin_user.email,
            failure_reason="Invalid 2FA code",
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid 2FA code",
        )

    # 2FA verification successful - clear failed attempts
    ip = request.client.host if request.client else "unknown"
    await AutoBanDetector.clear_failed_attempts(ip, "admin_2fa_login")
    await AutoBanDetector.clear_failed_attempts(ip, "admin_2fa_verify")

    # Update last login
    admin_user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    # Log successful login
    await log_login_attempt(
        db=db,
        user_type="admin",
        status="success",
        request=request,
        user_id=admin_user.id,
        username=admin_user.username,
        email=admin_user.email,
    )

    # Create tokens
    access_token = create_access_token({"sub": str(admin_user.id), "is_admin": True})
    refresh_token = create_refresh_token({"sub": str(admin_user.id), "is_admin": True})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
