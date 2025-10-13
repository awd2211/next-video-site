"""
Error Logging Middleware

Automatically logs unhandled exceptions to the error_logs table
"""

import traceback
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.database import SessionLocal
from app.utils.logging_utils import log_error


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically log unhandled exceptions
    """

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        Intercept exceptions and log them to the database
        """
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Log the error to database
            try:
                db = SessionLocal()
                try:
                    # Get user info if available
                    user_id = None
                    user_type = None
                    if hasattr(request.state, "user"):
                        user_id = request.state.user.id
                        user_type = "admin" if hasattr(request.state, "is_admin") and request.state.is_admin else "user"

                    # Determine error level based on exception type
                    level = "critical" if isinstance(e, (SystemError, MemoryError, KeyboardInterrupt)) else "error"

                    # Get traceback
                    tb = traceback.format_exception(type(e), e, e.__traceback__)
                    traceback_str = ''.join(tb)

                    # Determine HTTP status code
                    status_code = getattr(e, "status_code", 500)

                    # Log the error
                    await log_error(
                        db=db,
                        error_type=e.__class__.__name__,
                        error_message=str(e),
                        level=level,
                        traceback_str=traceback_str,
                        request=request,
                        user_id=user_id,
                        user_type=user_type,
                        status_code=status_code,
                    )
                finally:
                    await db.close()
            except Exception as log_error_exception:
                # If logging fails, print to console but don't break the application
                print(f"Failed to log error to database: {log_error_exception}")

            # Re-raise the original exception so FastAPI can handle it properly
            raise
