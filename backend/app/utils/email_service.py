import aiosmtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from app.models.email import EmailConfiguration


async def send_email_smtp(
    config: EmailConfiguration,
    to_email: str | List[str],
    subject: str,
    html_content: str,
    text_content: Optional[str] = None,
):
    """Send email using SMTP"""
    # Create message
    message = MIMEMultipart("alternative")
    message["From"] = f"{config.from_name} <{config.from_email}>"
    message["To"] = to_email if isinstance(to_email, str) else ", ".join(to_email)
    message["Subject"] = subject

    # Add text and HTML parts
    if text_content:
        part1 = MIMEText(text_content, "plain")
        message.attach(part1)

    part2 = MIMEText(html_content, "html")
    message.attach(part2)

    # Send email
    async with aiosmtplib.SMTP(
        hostname=config.smtp_host,
        port=config.smtp_port,
        use_tls=config.smtp_use_tls,
    ) as smtp:
        if config.smtp_username and config.smtp_password:
            await smtp.login(config.smtp_username, config.smtp_password)

        await smtp.send_message(message)


def send_email_mailgun(
    config: EmailConfiguration,
    to_email: str | List[str],
    subject: str,
    html_content: str,
    text_content: Optional[str] = None,
):
    """Send email using Mailgun API"""
    url = f"{config.mailgun_base_url}/{config.mailgun_domain}/messages"

    data = {
        "from": f"{config.from_name} <{config.from_email}>",
        "to": to_email if isinstance(to_email, list) else [to_email],
        "subject": subject,
        "html": html_content,
    }

    if text_content:
        data["text"] = text_content

    response = requests.post(
        url,
        auth=("api", config.mailgun_api_key),
        data=data,
    )

    response.raise_for_status()
    return response.json()


async def send_email(
    config: EmailConfiguration,
    to_email: str | List[str],
    subject: str,
    html_content: str,
    text_content: Optional[str] = None,
):
    """Send email using configured provider"""
    if config.provider == "smtp":
        return await send_email_smtp(config, to_email, subject, html_content, text_content)
    elif config.provider == "mailgun":
        return send_email_mailgun(config, to_email, subject, html_content, text_content)
    else:
        raise ValueError(f"Unsupported email provider: {config.provider}")


async def send_test_email(config: EmailConfiguration, to_email: str):
    """Send a test email to verify configuration"""
    subject = "测试邮件 - Email Configuration Test"
    html_content = """
    <html>
        <body>
            <h2>邮件配置测试成功！</h2>
            <p>如果您收到这封邮件，说明您的邮件服务器配置正确。</p>
            <p>If you receive this email, your email server configuration is correct.</p>
            <hr>
            <p style="color: #666; font-size: 12px;">
                This is an automated test email from your Video Streaming Platform.
            </p>
        </body>
    </html>
    """
    text_content = """
    邮件配置测试成功！

    如果您收到这封邮件，说明您的邮件服务器配置正确。
    If you receive this email, your email server configuration is correct.

    ---
    This is an automated test email from your Video Streaming Platform.
    """

    await send_email(config, to_email, subject, html_content, text_content)


async def send_template_email(
    config: EmailConfiguration,
    to_email: str | List[str],
    template,
    variables: dict,
):
    """Send email using template with variable replacement"""
    # Replace variables in subject and content
    subject = template.subject
    html_content = template.html_content
    text_content = template.text_content

    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        subject = subject.replace(placeholder, str(value))
        html_content = html_content.replace(placeholder, str(value))
        if text_content:
            text_content = text_content.replace(placeholder, str(value))

    await send_email(config, to_email, subject, html_content, text_content)
