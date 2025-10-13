"""
Logging utilities for recording various types of logs
"""

import json
import traceback
from datetime import datetime
from typing import Optional

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from user_agents import parse

from app.models.admin import LoginLog, SystemLog, ErrorLog


async def log_login_attempt(
    db: AsyncSession,
    user_type: str,  # 'admin' or 'user'
    status: str,  # 'success', 'failed', 'blocked'
    request: Request,
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    email: Optional[str] = None,
    failure_reason: Optional[str] = None,
) -> LoginLog:
    """
    Record a login attempt

    Args:
        db: Database session
        user_type: 'admin' or 'user'
        status: 'success', 'failed', 'blocked'
        request: FastAPI request object
        user_id: User ID if login successful
        username: Username attempted
        email: Email attempted
        failure_reason: Reason for failure

    Returns:
        LoginLog object
    """
    # Parse user agent
    user_agent_string = request.headers.get("user-agent", "")
    user_agent = parse(user_agent_string)

    # Determine device type
    if user_agent.is_mobile:
        device_type = "mobile"
    elif user_agent.is_tablet:
        device_type = "tablet"
    elif user_agent.is_pc:
        device_type = "desktop"
    else:
        device_type = "unknown"

    # Get IP address
    ip_address = request.client.host if request.client else "unknown"

    # Create log entry
    log = LoginLog(
        user_type=user_type,
        user_id=user_id,
        username=username,
        email=email,
        status=status,
        failure_reason=failure_reason,
        ip_address=ip_address,
        user_agent=user_agent_string,
        device_type=device_type,
        browser=f"{user_agent.browser.family} {user_agent.browser.version_string}",
        os=f"{user_agent.os.family} {user_agent.os.version_string}",
        # location can be added later with GeoIP
    )

    db.add(log)
    await db.commit()
    await db.refresh(log)

    return log


async def log_system_event(
    db: AsyncSession,
    level: str,  # 'info', 'warning', 'error', 'critical'
    category: str,  # 'startup', 'shutdown', 'database', 'cache', 'storage', 'security', etc.
    event: str,
    message: str,
    details: Optional[dict] = None,
    source: Optional[str] = None,
    user_id: Optional[int] = None,
    user_type: Optional[str] = None,
) -> SystemLog:
    """
    Record a system event

    Args:
        db: Database session
        level: Log level
        category: Event category
        event: Event name
        message: Event message
        details: Additional details as dict (will be JSON serialized)
        source: Source module/file
        user_id: Related user ID if any
        user_type: 'admin' or 'user' if user-related

    Returns:
        SystemLog object
    """
    log = SystemLog(
        level=level,
        category=category,
        event=event,
        message=message,
        details=json.dumps(details, ensure_ascii=False) if details else None,
        source=source,
        user_id=user_id,
        user_type=user_type,
    )

    db.add(log)
    await db.commit()
    await db.refresh(log)

    return log


async def log_error(
    db: AsyncSession,
    error_type: str,
    error_message: str,
    level: str = "error",  # 'error' or 'critical'
    traceback_str: Optional[str] = None,
    request: Optional[Request] = None,
    user_id: Optional[int] = None,
    user_type: Optional[str] = None,
    status_code: Optional[int] = None,
) -> ErrorLog:
    """
    Record an error/exception

    Args:
        db: Database session
        error_type: Exception class name
        error_message: Error message
        level: 'error' or 'critical'
        traceback_str: Full stack trace
        request: FastAPI request object if available
        user_id: Related user ID if any
        user_type: 'admin' or 'user' if user-related
        status_code: HTTP status code

    Returns:
        ErrorLog object
    """
    log = ErrorLog(
        level=level,
        error_type=error_type,
        error_message=error_message,
        traceback=traceback_str,
        request_method=request.method if request else None,
        request_url=str(request.url) if request else None,
        request_data=None,  # Can be added if needed
        user_id=user_id,
        user_type=user_type,
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent") if request else None,
        status_code=status_code,
        resolved=False,
    )

    db.add(log)
    await db.commit()
    await db.refresh(log)

    return log


async def log_error_from_exception(
    db: AsyncSession,
    exception: Exception,
    level: str = "error",
    request: Optional[Request] = None,
    user_id: Optional[int] = None,
    user_type: Optional[str] = None,
    status_code: Optional[int] = None,
) -> ErrorLog:
    """
    Record an error from an exception object

    Args:
        db: Database session
        exception: Exception object
        level: 'error' or 'critical'
        request: FastAPI request object if available
        user_id: Related user ID if any
        user_type: 'admin' or 'user' if user-related
        status_code: HTTP status code

    Returns:
        ErrorLog object
    """
    error_type = exception.__class__.__name__
    error_message = str(exception)
    traceback_str = ''.join(traceback.format_tb(exception.__traceback__))

    return await log_error(
        db=db,
        error_type=error_type,
        error_message=error_message,
        level=level,
        traceback_str=traceback_str,
        request=request,
        user_id=user_id,
        user_type=user_type,
        status_code=status_code,
    )


# Synchronous versions for use in middleware/exception handlers
def create_login_log_sync(
    user_type: str,
    status: str,
    request: Request,
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    email: Optional[str] = None,
    failure_reason: Optional[str] = None,
) -> dict:
    """
    Create login log data dict for synchronous contexts

    Returns dict that can be used to create LoginLog later
    """
    user_agent_string = request.headers.get("user-agent", "")
    user_agent = parse(user_agent_string)

    if user_agent.is_mobile:
        device_type = "mobile"
    elif user_agent.is_tablet:
        device_type = "tablet"
    elif user_agent.is_pc:
        device_type = "desktop"
    else:
        device_type = "unknown"

    return {
        "user_type": user_type,
        "user_id": user_id,
        "username": username,
        "email": email,
        "status": status,
        "failure_reason": failure_reason,
        "ip_address": request.client.host if request.client else "unknown",
        "user_agent": user_agent_string,
        "device_type": device_type,
        "browser": f"{user_agent.browser.family} {user_agent.browser.version_string}",
        "os": f"{user_agent.os.family} {user_agent.os.version_string}",
    }
