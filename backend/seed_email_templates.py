"""
Seed default email templates
"""
import asyncio
from sqlalchemy import text
from app.database import async_engine

default_templates = [
    {
        "name": "用户注册欢迎邮件",
        "slug": "user_welcome",
        "subject": "欢迎加入 {{site_name}}！",
        "html_content": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
        .button { display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
        .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 欢迎来到 {{site_name}}</h1>
        </div>
        <div class="content">
            <h2>你好，{{user_name}}！</h2>
            <p>感谢你注册 {{site_name}}！我们很高兴你加入我们的社区。</p>
            <p>现在你可以：</p>
            <ul>
                <li>📺 观看海量精彩视频</li>
                <li>💾 收藏喜欢的内容</li>
                <li>💬 发表评论与互动</li>
                <li>🔔 订阅你喜欢的内容创作者</li>
            </ul>
            <a href="{{login_url}}" class="button">立即开始探索</a>
            <p>如有任何问题，请随时联系我们的客服团队。</p>
        </div>
        <div class="footer">
            <p>© 2025 {{site_name}}. All rights reserved.</p>
            <p>这是一封自动发送的邮件，请勿直接回复。</p>
        </div>
    </div>
</body>
</html>
        """,
        "text_content": "欢迎加入 {{site_name}}！\n\n你好，{{user_name}}！\n\n感谢你注册我们的平台。现在你可以观看视频、收藏内容、发表评论等。\n\n访问 {{login_url}} 开始探索。",
        "variables": ["site_name", "user_name", "login_url"],
        "description": "用户注册后发送的欢迎邮件"
    },
    {
        "name": "密码重置邮件",
        "slug": "password_reset",
        "subject": "重置你的 {{site_name}} 密码",
        "html_content": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #ff6b6b; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
        .button { display: inline-block; padding: 12px 30px; background: #ff6b6b; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
        .warning { background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }
        .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 密码重置请求</h1>
        </div>
        <div class="content">
            <h2>你好，{{user_name}}！</h2>
            <p>我们收到了重置你账户密码的请求。如果这是你本人的操作，请点击下面的按钮重置密码：</p>
            <a href="{{reset_url}}" class="button">重置密码</a>
            <p>此链接将在 <strong>{{expiry_time}}</strong> 后失效。</p>
            <div class="warning">
                <strong>⚠️ 安全提示：</strong>如果你没有请求重置密码，请忽略此邮件。你的密码不会被更改。
            </div>
            <p>为了保护你的账户安全，请不要将此链接分享给任何人。</p>
        </div>
        <div class="footer">
            <p>© 2025 {{site_name}}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """,
        "text_content": "重置你的密码\n\n你好，{{user_name}}！\n\n我们收到了重置密码的请求。请访问以下链接重置密码：\n{{reset_url}}\n\n此链接将在 {{expiry_time}} 后失效。\n\n如果这不是你的操作，请忽略此邮件。",
        "variables": ["site_name", "user_name", "reset_url", "expiry_time"],
        "description": "用户请求重置密码时发送"
    },
    {
        "name": "邮箱验证",
        "slug": "email_verification",
        "subject": "验证你的 {{site_name}} 邮箱地址",
        "html_content": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #4CAF50; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
        .button { display: inline-block; padding: 12px 30px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
        .code { font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #4CAF50; text-align: center; padding: 20px; background: white; border: 2px dashed #4CAF50; border-radius: 5px; margin: 20px 0; }
        .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✉️ 验证你的邮箱</h1>
        </div>
        <div class="content">
            <h2>你好，{{user_name}}！</h2>
            <p>感谢注册 {{site_name}}！请验证你的邮箱地址以激活账户。</p>
            <p>点击下面的按钮完成验证：</p>
            <a href="{{verification_url}}" class="button">验证邮箱</a>
            <p>或者输入以下验证码：</p>
            <div class="code">{{verification_code}}</div>
            <p>验证码有效期为 <strong>30分钟</strong>。</p>
        </div>
        <div class="footer">
            <p>© 2025 {{site_name}}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """,
        "text_content": "验证你的邮箱地址\n\n你好，{{user_name}}！\n\n请访问以下链接验证邮箱：\n{{verification_url}}\n\n或输入验证码：{{verification_code}}\n\n验证码有效期为30分钟。",
        "variables": ["site_name", "user_name", "verification_url", "verification_code"],
        "description": "新用户邮箱验证"
    },
    {
        "name": "订阅确认",
        "slug": "subscription_confirmation",
        "subject": "感谢订阅 {{plan_name}} 计划！",
        "html_content": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
        .info-box { background: white; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #f5576c; }
        .button { display: inline-block; padding: 12px 30px; background: #f5576c; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
        .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎊 订阅成功！</h1>
        </div>
        <div class="content">
            <h2>你好，{{user_name}}！</h2>
            <p>感谢你订阅 <strong>{{plan_name}}</strong> 计划！你的订阅已激活。</p>
            <div class="info-box">
                <h3>📋 订阅详情</h3>
                <p><strong>计划名称：</strong>{{plan_name}}</p>
                <p><strong>订阅金额：</strong>¥{{amount}}</p>
                <p><strong>开始日期：</strong>{{start_date}}</p>
                <p><strong>下次续费：</strong>{{next_billing_date}}</p>
            </div>
            <p>现在你可以享受所有高级功能：</p>
            <ul>
                <li>🎬 无广告观看体验</li>
                <li>📥 离线下载功能</li>
                <li>🎯 4K超清画质</li>
                <li>👥 多设备同时观看</li>
            </ul>
            <a href="{{dashboard_url}}" class="button">查看我的订阅</a>
        </div>
        <div class="footer">
            <p>© 2025 {{site_name}}. All rights reserved.</p>
            <p>如需取消订阅，请访问账户设置。</p>
        </div>
    </div>
</body>
</html>
        """,
        "text_content": "订阅成功！\n\n你好，{{user_name}}！\n\n感谢订阅 {{plan_name}} 计划。\n\n订阅详情：\n- 计划：{{plan_name}}\n- 金额：¥{{amount}}\n- 开始：{{start_date}}\n- 续费：{{next_billing_date}}\n\n访问 {{dashboard_url}} 管理订阅。",
        "variables": ["site_name", "user_name", "plan_name", "amount", "start_date", "next_billing_date", "dashboard_url"],
        "description": "用户订阅成功后的确认邮件"
    },
    {
        "name": "订阅即将到期提醒",
        "slug": "subscription_expiring",
        "subject": "你的 {{plan_name}} 订阅即将到期",
        "html_content": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #ff9800; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
        .alert { background: #fff3e0; border-left: 4px solid #ff9800; padding: 15px; margin: 20px 0; }
        .button { display: inline-block; padding: 12px 30px; background: #ff9800; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
        .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⏰ 订阅即将到期</h1>
        </div>
        <div class="content">
            <h2>你好，{{user_name}}！</h2>
            <div class="alert">
                <strong>📢 重要提醒：</strong>你的 <strong>{{plan_name}}</strong> 订阅将在 <strong>{{days_left}}</strong> 天后到期（{{expiry_date}}）。
            </div>
            <p>为了继续享受高级会员权益，请及时续费：</p>
            <ul>
                <li>无广告观看</li>
                <li>4K超清画质</li>
                <li>离线下载</li>
                <li>更多专属内容</li>
            </ul>
            <a href="{{renewal_url}}" class="button">立即续费</a>
            <p>如有疑问，请联系客服。</p>
        </div>
        <div class="footer">
            <p>© 2025 {{site_name}}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """,
        "text_content": "订阅即将到期\n\n你好，{{user_name}}！\n\n你的 {{plan_name}} 订阅将在 {{days_left}} 天后到期（{{expiry_date}}）。\n\n访问 {{renewal_url}} 续费以继续享受高级权益。",
        "variables": ["site_name", "user_name", "plan_name", "days_left", "expiry_date", "renewal_url"],
        "description": "订阅到期前提醒用户续费"
    },
    {
        "name": "视频上传成功通知",
        "slug": "video_upload_success",
        "subject": "你的视频《{{video_title}}》已成功上传！",
        "html_content": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
        .video-box { background: white; padding: 20px; border-radius: 5px; margin: 20px 0; }
        .video-box img { width: 100%; border-radius: 5px; }
        .button { display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
        .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 视频上传成功！</h1>
        </div>
        <div class="content">
            <h2>你好，{{user_name}}！</h2>
            <p>你的视频已成功上传并发布！</p>
            <div class="video-box">
                <h3>《{{video_title}}》</h3>
                <p><strong>时长：</strong>{{video_duration}}</p>
                <p><strong>上传时间：</strong>{{upload_time}}</p>
                <p><strong>状态：</strong><span style="color: green;">✓ 已发布</span></p>
            </div>
            <p>你的视频现在对所有用户可见。快去分享给你的朋友吧！</p>
            <a href="{{video_url}}" class="button">查看视频</a>
        </div>
        <div class="footer">
            <p>© 2025 {{site_name}}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """,
        "text_content": "视频上传成功！\n\n你好，{{user_name}}！\n\n你的视频《{{video_title}}》已成功上传。\n\n视频详情：\n- 标题：{{video_title}}\n- 时长：{{video_duration}}\n- 上传时间：{{upload_time}}\n\n访问 {{video_url}} 查看视频。",
        "variables": ["site_name", "user_name", "video_title", "video_duration", "upload_time", "video_url"],
        "description": "创作者上传视频成功后的通知"
    },
    {
        "name": "评论回复通知",
        "slug": "comment_reply",
        "subject": "{{replier_name}} 回复了你的评论",
        "html_content": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #2196F3; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
        .comment-box { background: white; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 3px solid #2196F3; }
        .reply-box { background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 10px 0 10px 20px; border-left: 3px solid #64b5f6; }
        .button { display: inline-block; padding: 12px 30px; background: #2196F3; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
        .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💬 新回复通知</h1>
        </div>
        <div class="content">
            <h2>你好，{{user_name}}！</h2>
            <p><strong>{{replier_name}}</strong> 回复了你在视频《{{video_title}}》下的评论：</p>
            <div class="comment-box">
                <p><strong>你的评论：</strong></p>
                <p>{{original_comment}}</p>
            </div>
            <div class="reply-box">
                <p><strong>{{replier_name}} 的回复：</strong></p>
                <p>{{reply_content}}</p>
            </div>
            <a href="{{comment_url}}" class="button">查看对话</a>
        </div>
        <div class="footer">
            <p>© 2025 {{site_name}}. All rights reserved.</p>
            <p>如不想接收此类通知，可在账户设置中关闭。</p>
        </div>
    </div>
</body>
</html>
        """,
        "text_content": "新回复通知\n\n你好，{{user_name}}！\n\n{{replier_name}} 回复了你的评论：\n\n你的评论：\n{{original_comment}}\n\n回复：\n{{reply_content}}\n\n访问 {{comment_url}} 查看对话。",
        "variables": ["site_name", "user_name", "replier_name", "video_title", "original_comment", "reply_content", "comment_url"],
        "description": "用户评论被回复时的通知"
    },
    {
        "name": "系统维护通知",
        "slug": "system_maintenance",
        "subject": "系统维护通知 - {{maintenance_date}}",
        "html_content": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #9C27B0; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
        .notice { background: #f3e5f5; border: 2px solid #9C27B0; padding: 20px; border-radius: 5px; margin: 20px 0; }
        .timeline { background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #9C27B0; }
        .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 系统维护通知</h1>
        </div>
        <div class="content">
            <h2>尊敬的用户：</h2>
            <div class="notice">
                <p><strong>📅 维护时间：</strong>{{maintenance_date}}</p>
                <p><strong>⏱️ 维护时长：</strong>{{maintenance_duration}}</p>
            </div>
            <p>为了给你提供更好的服务，我们将进行系统维护升级。维护期间，平台可能无法访问。</p>
            <div class="timeline">
                <h3>维护内容：</h3>
                <ul>
                    <li>{{maintenance_item_1}}</li>
                    <li>{{maintenance_item_2}}</li>
                    <li>{{maintenance_item_3}}</li>
                </ul>
            </div>
            <p>我们会尽快完成维护工作。给你带来的不便，敬请谅解。</p>
            <p>感谢你的支持与理解！</p>
        </div>
        <div class="footer">
            <p>© 2025 {{site_name}}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """,
        "text_content": "系统维护通知\n\n尊敬的用户：\n\n我们将于 {{maintenance_date}} 进行系统维护，预计耗时 {{maintenance_duration}}。\n\n维护内容：\n- {{maintenance_item_1}}\n- {{maintenance_item_2}}\n- {{maintenance_item_3}}\n\n维护期间平台可能无法访问，敬请谅解。",
        "variables": ["site_name", "maintenance_date", "maintenance_duration", "maintenance_item_1", "maintenance_item_2", "maintenance_item_3"],
        "description": "系统维护前发送给用户的通知"
    },
    {
        "name": "账户安全警告",
        "slug": "security_alert",
        "subject": "⚠️ 账户安全提醒 - 检测到异常登录",
        "html_content": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #f44336; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
        .alert-box { background: #ffebee; border: 2px solid #f44336; padding: 20px; border-radius: 5px; margin: 20px 0; }
        .info-table { width: 100%; background: white; border-collapse: collapse; margin: 15px 0; }
        .info-table td { padding: 10px; border-bottom: 1px solid #eee; }
        .info-table td:first-child { font-weight: bold; width: 120px; }
        .button { display: inline-block; padding: 12px 30px; background: #f44336; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
        .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 账户安全警告</h1>
        </div>
        <div class="content">
            <h2>你好，{{user_name}}！</h2>
            <div class="alert-box">
                <strong>⚠️ 安全提醒：</strong>我们检测到你的账户有一次新的登录活动。
            </div>
            <h3>登录详情：</h3>
            <table class="info-table">
                <tr>
                    <td>登录时间</td>
                    <td>{{login_time}}</td>
                </tr>
                <tr>
                    <td>登录地点</td>
                    <td>{{login_location}}</td>
                </tr>
                <tr>
                    <td>IP地址</td>
                    <td>{{ip_address}}</td>
                </tr>
                <tr>
                    <td>设备</td>
                    <td>{{device_info}}</td>
                </tr>
            </table>
            <p><strong>如果这是你本人的操作</strong>，请忽略此邮件。</p>
            <p><strong>如果这不是你的操作</strong>，你的账户可能已被盗用。请立即：</p>
            <ul>
                <li>修改密码</li>
                <li>检查账户设置</li>
                <li>联系客服团队</li>
            </ul>
            <a href="{{security_url}}" class="button">保护我的账户</a>
        </div>
        <div class="footer">
            <p>© 2025 {{site_name}}. All rights reserved.</p>
            <p>这是一封自动发送的安全邮件。</p>
        </div>
    </div>
</body>
</html>
        """,
        "text_content": "账户安全警告\n\n你好，{{user_name}}！\n\n检测到新的登录活动：\n- 时间：{{login_time}}\n- 地点：{{login_location}}\n- IP：{{ip_address}}\n- 设备：{{device_info}}\n\n如不是你本人操作，请立即访问 {{security_url}} 保护账户。",
        "variables": ["site_name", "user_name", "login_time", "login_location", "ip_address", "device_info", "security_url"],
        "description": "检测到异常登录时的安全警告"
    },
    {
        "name": "月度报告",
        "slug": "monthly_report",
        "subject": "你的 {{month}} 月观看报告 📊",
        "html_content": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
        .stat-box { background: white; padding: 20px; border-radius: 5px; margin: 15px 0; text-align: center; }
        .stat-number { font-size: 48px; font-weight: bold; color: #667eea; }
        .stat-label { color: #666; margin-top: 10px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0; }
        .button { display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
        .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 你的 {{month}} 月观看报告</h1>
        </div>
        <div class="content">
            <h2>你好，{{user_name}}！</h2>
            <p>来看看你这个月的精彩时光吧！</p>
            <div class="stat-box">
                <div class="stat-number">{{total_hours}}</div>
                <div class="stat-label">观看时长（小时）</div>
            </div>
            <div class="grid">
                <div class="stat-box">
                    <div class="stat-number" style="font-size: 32px;">{{videos_watched}}</div>
                    <div class="stat-label">观看视频数</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number" style="font-size: 32px;">{{favorites_added}}</div>
                    <div class="stat-label">新增收藏</div>
                </div>
            </div>
            <h3>🏆 你最喜欢的分类</h3>
            <div class="stat-box">
                <p style="font-size: 24px; color: #667eea;">{{favorite_category}}</p>
                <p style="color: #666;">观看了 {{category_count}} 个视频</p>
            </div>
            <p>继续探索更多精彩内容！</p>
            <a href="{{explore_url}}" class="button">发现更多</a>
        </div>
        <div class="footer">
            <p>© 2025 {{site_name}}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """,
        "text_content": "你的 {{month}} 月观看报告\n\n你好，{{user_name}}！\n\n本月数据：\n- 观看时长：{{total_hours}} 小时\n- 观看视频：{{videos_watched}} 个\n- 新增收藏：{{favorites_added}} 个\n- 最爱分类：{{favorite_category}}（{{category_count}} 个视频）\n\n访问 {{explore_url}} 发现更多内容。",
        "variables": ["site_name", "user_name", "month", "total_hours", "videos_watched", "favorites_added", "favorite_category", "category_count", "explore_url"],
        "description": "每月发送给用户的观看数据报告"
    }
]

async def seed_templates():
    """Insert default email templates"""
    async with async_engine.begin() as conn:
        # Check if templates already exist
        result = await conn.execute(
            text("SELECT COUNT(*) FROM email_templates")
        )
        count = result.scalar()

        if count > 0:
            print(f"⚠️  Database already has {count} email templates.")
            response = input("Do you want to clear and re-seed? (yes/no): ")
            if response.lower() != 'yes':
                print("Aborted.")
                return

            # Clear existing templates
            await conn.execute(text("DELETE FROM email_templates"))
            print("✓ Cleared existing templates")

        # Insert templates
        import json

        for template in default_templates:
            insert_query = text("""
                INSERT INTO email_templates
                (name, slug, subject, html_content, text_content, variables, description, is_active)
                VALUES
                (:name, :slug, :subject, :html_content, :text_content, CAST(:variables AS json), :description, :is_active)
            """)

            await conn.execute(
                insert_query,
                {
                    "name": template["name"],
                    "slug": template["slug"],
                    "subject": template["subject"],
                    "html_content": template["html_content"],
                    "text_content": template["text_content"],
                    "variables": json.dumps(template["variables"]),
                    "description": template["description"],
                    "is_active": True
                }
            )
            print(f"✓ Created template: {template['name']}")

        print(f"\n🎉 Successfully seeded {len(default_templates)} email templates!")

if __name__ == "__main__":
    asyncio.run(seed_templates())
