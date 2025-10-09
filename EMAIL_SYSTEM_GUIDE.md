# 邮件系统使用指南

## 功能概览

本系统提供了完整的邮件服务器配置和邮件模板管理功能，支持 **SMTP** 和 **Mailgun** 两种邮件发送方式。

## 访问路径

管理后台 → 系统设置 → 邮件服务器 / 邮件模板

- 管理后台地址: http://localhost:3001
- 邮件配置页面: http://localhost:3001/settings

## 1. 邮件服务器配置

### SMTP 配置

适用于使用自己的 SMTP 服务器或第三方 SMTP 服务（如 Gmail, Outlook, 阿里云邮件等）。

**配置参数：**
- SMTP 服务器地址: 例如 `smtp.gmail.com`
- SMTP 端口: 通常为 `587` (TLS) 或 `465` (SSL)
- 用户名: 邮箱地址
- 密码: 邮箱密码或授权码
- TLS/SSL: 根据服务器要求选择
- 发件人邮箱: 显示的发件人地址
- 发件人名称: 显示的发件人名字

**常见 SMTP 服务器配置示例：**

#### Gmail
```
服务器: smtp.gmail.com
端口: 587
TLS: 开启
需要应用专用密码（非账号密码）
```

#### QQ邮箱
```
服务器: smtp.qq.com
端口: 587
TLS: 开启
需要授权码
```

#### 阿里云邮件
```
服务器: smtpdm.aliyun.com
端口: 465
SSL: 开启
```

### Mailgun 配置

适用于使用 Mailgun 的专业邮件发送服务。

**配置参数：**
- Mailgun API Key: 从 Mailgun 控制台获取
- Mailgun Domain: 你的发送域名
- Base URL: 默认 `https://api.mailgun.net/v3` (欧洲区使用 `https://api.eu.mailgun.net/v3`)
- 发件人邮箱: 发送邮箱地址
- 发件人名称: 发送者名字

### 测试邮件配置

配置保存后，点击"测试"按钮，输入接收邮箱地址，系统会发送一封测试邮件验证配置是否正确。

## 2. 邮件模板管理

### 创建邮件模板

点击"创建模板"按钮，填写以下信息：

1. **模板名称**: 便于识别的名称，如"欢迎邮件"
2. **Slug**: 唯一标识符，只能包含小写字母、数字和连字符，如 `welcome-email`
3. **邮件主题**: 邮件的标题，支持变量
4. **HTML 内容**: 邮件的 HTML 版本内容
5. **纯文本内容**: （可选）不支持 HTML 的邮件客户端会显示此内容
6. **可用变量**: 模板中可以使用的变量列表，用逗号分隔
7. **描述**: 模板用途说明

### 使用变量

在邮件主题和内容中使用 `{{variable_name}}` 格式的变量，例如：

**主题:**
```
欢迎加入 {{site_name}}，{{user_name}}！
```

**HTML内容:**
```html
<html>
  <body>
    <h2>欢迎 {{user_name}}！</h2>
    <p>感谢您注册 {{site_name}}。</p>
    <p>您的账号已经激活，点击下方链接开始使用：</p>
    <a href="{{login_link}}">立即登录</a>
  </body>
</html>
```

### 预览模板

在模板列表中点击"预览"按钮，可以查看 HTML 内容的渲染效果。

### 内置模板建议

以下是一些常用的邮件模板建议：

#### 1. 欢迎邮件 (`welcome-email`)
变量: `user_name`, `site_name`, `login_link`

#### 2. 密码重置 (`password-reset`)
变量: `user_name`, `reset_link`, `expire_time`

#### 3. 视频上传成功通知 (`video-uploaded`)
变量: `user_name`, `video_title`, `video_link`

#### 4. 评论通知 (`comment-notification`)
变量: `user_name`, `video_title`, `comment_content`, `video_link`

#### 5. VIP 订阅确认 (`vip-subscription`)
变量: `user_name`, `plan_name`, `expire_date`, `price`

## 3. 在代码中使用邮件模板

### Python 后端示例

```python
from app.models.email import EmailConfiguration, EmailTemplate
from app.utils.email_service import send_template_email
from sqlalchemy import select

async def send_welcome_email(user_email: str, user_name: str):
    # 获取活跃的邮件配置
    config_result = await db.execute(
        select(EmailConfiguration).filter(EmailConfiguration.is_active == True)
    )
    config = config_result.scalar_one()

    # 获取欢迎邮件模板
    template_result = await db.execute(
        select(EmailTemplate).filter(EmailTemplate.slug == "welcome-email")
    )
    template = template_result.scalar_one()

    # 准备变量
    variables = {
        "user_name": user_name,
        "site_name": "视频平台",
        "login_link": "https://yoursite.com/login"
    }

    # 发送邮件
    await send_template_email(config, user_email, template, variables)
```

## 4. 数据库连接池优化

系统已经优化了数据库连接池配置，提供更好的并发性能：

- **连接池大小**: 20 个基础连接
- **最大溢出**: 额外 40 个连接
- **连接回收**: 1小时自动回收
- **健康检查**: 使用前自动检测连接有效性

### 查看连接池状态

可以通过 API 查看当前连接池状态：

```bash
GET /api/v1/admin/stats/database-pool
Authorization: Bearer {admin_token}
```

返回示例：
```json
{
  "pool_size": 20,
  "checked_in": 18,
  "checked_out": 2,
  "overflow": 0,
  "total_connections": 20
}
```

## 5. 安全建议

1. **SMTP 密码保护**: 不要在代码中硬编码 SMTP 密码
2. **使用 TLS/SSL**: 始终启用加密传输
3. **定期更新密钥**: 定期轮换 API 密钥和密码
4. **限制发送频率**: 防止被标记为垃圾邮件
5. **邮件内容审核**: 确保模板内容符合反垃圾邮件规定

## 6. 故障排查

### 测试邮件发送失败

**SMTP 相关问题：**
- 检查服务器地址和端口是否正确
- 确认用户名和密码/授权码正确
- 验证 TLS/SSL 设置与服务器要求一致
- 检查防火墙是否阻止了端口

**Mailgun 相关问题：**
- 确认 API Key 有效
- 检查 Domain 是否已验证
- 确认账户余额充足
- 检查发送域名的 DNS 配置

### 模板变量未替换

- 确保变量名称大小写正确
- 检查变量格式是否为 `{{variable_name}}`
- 确认在发送时传入了所有必需的变量

## API 文档

完整的 API 文档可以访问：http://localhost:8001/docs

相关接口：
- `GET /api/v1/admin/email/config` - 获取邮件配置列表
- `POST /api/v1/admin/email/config` - 创建邮件配置
- `PUT /api/v1/admin/email/config/{id}` - 更新邮件配置
- `POST /api/v1/admin/email/config/{id}/test` - 测试邮件配置
- `GET /api/v1/admin/email/templates` - 获取模板列表
- `POST /api/v1/admin/email/templates` - 创建模板
- `POST /api/v1/admin/email/templates/{id}/preview` - 预览模板

---

## 技术栈

**后端:**
- FastAPI
- SQLAlchemy (async)
- aiosmtplib (SMTP)
- requests (Mailgun)

**前端:**
- React + TypeScript
- Ant Design
- TanStack Query

**数据库:**
- PostgreSQL 16
- 优化的连接池配置
