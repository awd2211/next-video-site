from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.email import EmailConfiguration, EmailTemplate
from app.models.user import AdminUser
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


# Pydantic schemas
class EmailConfigSMTPCreate(BaseModel):
    provider: str = "smtp"
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False
    from_email: EmailStr
    from_name: str


class EmailConfigMailgunCreate(BaseModel):
    provider: str = "mailgun"
    mailgun_api_key: str
    mailgun_domain: str
    mailgun_base_url: str = "https://api.mailgun.net/v3"
    from_email: EmailStr
    from_name: str


class EmailConfigUpdate(BaseModel):
    provider: Optional[str] = None
    is_active: Optional[bool] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: Optional[bool] = None
    smtp_use_ssl: Optional[bool] = None
    mailgun_api_key: Optional[str] = None
    mailgun_domain: Optional[str] = None
    mailgun_base_url: Optional[str] = None
    from_email: Optional[EmailStr] = None
    from_name: Optional[str] = None


class EmailTemplateCreate(BaseModel):
    name: str
    slug: str
    subject: str
    html_content: str
    text_content: Optional[str] = None
    variables: Optional[list[str]] = None
    description: Optional[str] = None
    is_active: bool = True


class EmailTemplateUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    html_content: Optional[str] = None
    text_content: Optional[str] = None
    variables: Optional[list[str]] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


# Email Configuration Endpoints
@router.get("/config")
async def get_email_config(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Get current email configuration"""
    result = await db.execute(select(EmailConfiguration))
    configs = result.scalars().all()
    return configs


@router.post("/config")
async def create_email_config(
    config: EmailConfigSMTPCreate | EmailConfigMailgunCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Create new email configuration"""
    # Deactivate all existing configs
    existing = await db.execute(select(EmailConfiguration))
    for existing_config in existing.scalars().all():
        existing_config.is_active = False

    # Create new config
    config_data = config.model_dump()
    new_config = EmailConfiguration(**config_data, is_active=True)
    db.add(new_config)
    await db.commit()
    await db.refresh(new_config)

    return new_config


@router.put("/config/{config_id}")
async def update_email_config(
    config_id: int,
    config: EmailConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Update email configuration"""
    result = await db.execute(
        select(EmailConfiguration).filter(EmailConfiguration.id == config_id)
    )
    email_config = result.scalar_one_or_none()

    if not email_config:
        raise HTTPException(status_code=404, detail="Email configuration not found")

    # If setting this config to active, deactivate others
    if config.is_active:
        other_configs = await db.execute(
            select(EmailConfiguration).filter(EmailConfiguration.id != config_id)
        )
        for other_config in other_configs.scalars().all():
            other_config.is_active = False

    # Update fields
    for field, value in config.model_dump(exclude_unset=True).items():
        setattr(email_config, field, value)

    await db.commit()
    await db.refresh(email_config)

    return email_config


@router.delete("/config/{config_id}")
async def delete_email_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Delete email configuration"""
    result = await db.execute(
        select(EmailConfiguration).filter(EmailConfiguration.id == config_id)
    )
    email_config = result.scalar_one_or_none()

    if not email_config:
        raise HTTPException(status_code=404, detail="Email configuration not found")

    await db.delete(email_config)
    await db.commit()

    return {"message": "Email configuration deleted"}


@router.post("/config/{config_id}/test")
async def test_email_config(
    config_id: int,
    test_email: EmailStr,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Test email configuration by sending a test email"""
    result = await db.execute(
        select(EmailConfiguration).filter(EmailConfiguration.id == config_id)
    )
    email_config = result.scalar_one_or_none()

    if not email_config:
        raise HTTPException(status_code=404, detail="Email configuration not found")

    # Import email service (we'll create this next)
    from app.utils.email_service import send_test_email

    try:
        await send_test_email(email_config, test_email)
        return {"message": "Test email sent successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to send test email: {str(e)}"
        )


# Email Template Endpoints
@router.get("/templates")
async def list_email_templates(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """List all email templates"""
    result = await db.execute(
        select(EmailTemplate).order_by(EmailTemplate.created_at.desc())
    )
    templates = result.scalars().all()
    return templates


@router.get("/templates/{template_id}")
async def get_email_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Get email template by ID"""
    result = await db.execute(
        select(EmailTemplate).filter(EmailTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Email template not found")

    return template


@router.post("/templates")
async def create_email_template(
    template: EmailTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Create new email template"""
    # Check if slug already exists
    result = await db.execute(
        select(EmailTemplate).filter(EmailTemplate.slug == template.slug)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400, detail="Template with this slug already exists"
        )

    new_template = EmailTemplate(**template.model_dump())
    db.add(new_template)
    await db.commit()
    await db.refresh(new_template)

    return new_template


@router.put("/templates/{template_id}")
async def update_email_template(
    template_id: int,
    template: EmailTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Update email template"""
    result = await db.execute(
        select(EmailTemplate).filter(EmailTemplate.id == template_id)
    )
    email_template = result.scalar_one_or_none()

    if not email_template:
        raise HTTPException(status_code=404, detail="Email template not found")

    # Update fields
    for field, value in template.model_dump(exclude_unset=True).items():
        setattr(email_template, field, value)

    await db.commit()
    await db.refresh(email_template)

    return email_template


@router.delete("/templates/{template_id}")
async def delete_email_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Delete email template"""
    result = await db.execute(
        select(EmailTemplate).filter(EmailTemplate.id == template_id)
    )
    email_template = result.scalar_one_or_none()

    if not email_template:
        raise HTTPException(status_code=404, detail="Email template not found")

    await db.delete(email_template)
    await db.commit()

    return {"message": "Email template deleted"}


@router.post("/templates/{template_id}/preview")
async def preview_email_template(
    template_id: int,
    variables: dict,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Preview email template with variables"""
    result = await db.execute(
        select(EmailTemplate).filter(EmailTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Email template not found")

    # Simple template variable replacement
    html_preview = template.html_content
    subject_preview = template.subject

    for key, value in variables.items():
        html_preview = html_preview.replace(f"{{{{{key}}}}}", str(value))
        subject_preview = subject_preview.replace(f"{{{{{key}}}}}", str(value))

    return {
        "subject": subject_preview,
        "html_content": html_preview,
        "text_content": template.text_content,
    }
