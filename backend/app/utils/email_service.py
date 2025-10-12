from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

import aiosmtplib
import requests

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
        return await send_email_smtp(
            config, to_email, subject, html_content, text_content
        )
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


async def send_password_reset_email(
    config: EmailConfiguration,
    to_email: str,
    code: str,
    is_admin: bool = False,
):
    """Send password reset verification code email"""
    user_type = "管理员" if is_admin else "用户"

    subject = f"【密码重置】验证码 - {user_type}账户"

    html_content = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: #0073bb;
                    color: white;
                    padding: 30px;
                    border-radius: 8px 8px 0 0;
                    text-align: center;
                }}
                .content {{
                    background: #fff;
                    padding: 30px;
                    border: 1px solid #e0e0e0;
                    border-top: none;
                }}
                .code-box {{
                    background: #f7f9fa;
                    border: 2px dashed #ff9900;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 25px 0;
                    text-align: center;
                }}
                .code {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #ff9900;
                    letter-spacing: 8px;
                    font-family: 'Courier New', monospace;
                }}
                .warning {{
                    background: rgba(255, 153, 0, 0.1);
                    border-left: 4px solid #ff9900;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #666;
                    font-size: 12px;
                    border-top: 1px solid #e0e0e0;
                    margin-top: 20px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background-color: #ff9900;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 10px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔐 密码重置验证码</h1>
                <p>Video Site - {user_type}账户</p>
            </div>

            <div class="content">
                <h2>您好！</h2>
                <p>您正在尝试重置{user_type}账户的密码。请使用以下验证码完成密码重置：</p>

                <div class="code-box">
                    <div class="code">{code}</div>
                    <p style="margin: 10px 0 0 0; color: #666;">有效期：15分钟</p>
                </div>

                <div class="warning">
                    <strong>⚠️ 安全提示：</strong>
                    <ul style="margin: 10px 0 0 0;">
                        <li>此验证码仅可使用一次</li>
                        <li>请勿将验证码告诉任何人</li>
                        <li>如果这不是您的操作，请忽略此邮件</li>
                        <li>验证码将在15分钟后失效</li>
                    </ul>
                </div>

                <p>如果您在使用过程中遇到任何问题，请联系技术支持。</p>
            </div>

            <div class="footer">
                <p>此邮件由系统自动发送，请勿回复</p>
                <p>© 2025 Video Site. All rights reserved.</p>
            </div>
        </body>
    </html>
    """

    text_content = f"""
    密码重置验证码 - {user_type}账户
    ========================================

    您好！

    您正在尝试重置{user_type}账户的密码。请使用以下验证码完成密码重置：

    验证码：{code}
    有效期：15分钟

    安全提示：
    - 此验证码仅可使用一次
    - 请勿将验证码告诉任何人
    - 如果这不是您的操作，请忽略此邮件
    - 验证码将在15分钟后失效

    如果您在使用过程中遇到任何问题，请联系技术支持。

    ========================================
    此邮件由系统自动发送，请勿回复
    © 2025 Video Site. All rights reserved.
    """

    await send_email(config, to_email, subject, html_content, text_content)
