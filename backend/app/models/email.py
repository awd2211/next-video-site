from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class EmailConfiguration(Base):
    __tablename__ = "email_configurations"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(20), nullable=False)  # 'smtp' or 'mailgun'
    is_active = Column(Boolean, default=False, nullable=False)

    # SMTP configuration
    smtp_host = Column(String(255), nullable=True)
    smtp_port = Column(Integer, nullable=True)
    smtp_username = Column(String(255), nullable=True)
    smtp_password = Column(String(255), nullable=True)
    smtp_use_tls = Column(Boolean, default=True, nullable=True)
    smtp_use_ssl = Column(Boolean, default=False, nullable=True)

    # Mailgun configuration
    mailgun_api_key = Column(String(255), nullable=True)
    mailgun_domain = Column(String(255), nullable=True)
    mailgun_base_url = Column(String(255), nullable=True)

    # Common fields
    from_email = Column(String(255), nullable=False)
    from_name = Column(String(255), nullable=False)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class EmailTemplate(Base):
    __tablename__ = "email_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    subject = Column(String(255), nullable=False)
    html_content = Column(Text, nullable=False)
    text_content = Column(Text, nullable=True)
    variables = Column(
        JSON, nullable=True
    )  # List of available variables like ["user_name", "video_title"]
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
