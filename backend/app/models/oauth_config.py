"""OAuth Configuration Model for Google, Facebook, etc."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class OAuthConfig(Base):
    """OAuth provider configuration model"""

    __tablename__ = "oauth_configs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Provider identifier (google, facebook, github, etc.)
    provider: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    # OAuth application credentials
    client_id: Mapped[str] = mapped_column(String(500), nullable=False)
    client_secret: Mapped[str] = mapped_column(Text, nullable=False)  # Should be encrypted in production

    # OAuth configuration
    redirect_uri: Mapped[Optional[str]] = mapped_column(String(500))
    scopes: Mapped[Optional[list]] = mapped_column(JSON, default=list)  # List of scopes

    # Authorization and token URLs (can be overridden)
    authorization_url: Mapped[Optional[str]] = mapped_column(String(500))
    token_url: Mapped[Optional[str]] = mapped_column(String(500))
    userinfo_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Additional provider-specific configuration
    extra_config: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)

    # Enable/disable this provider
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    # Test status
    last_test_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_test_status: Mapped[Optional[str]] = mapped_column(String(20))  # success, failed
    last_test_message: Mapped[Optional[str]] = mapped_column(Text)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<OAuthConfig(provider={self.provider}, enabled={self.enabled})>"
