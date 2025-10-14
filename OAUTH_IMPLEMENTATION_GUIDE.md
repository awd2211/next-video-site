# OAuth 登录功能实施指南

## 📋 概述

本文档记录了 Google 和 Facebook OAuth 第三方登录功能的完整实施方案。

---

## ✅ 已完成的后端工作 (100%)

### 1. 数据库层

#### ✅ 创建 OAuthConfig 模型
**文件**: `backend/app/models/oauth_config.py`

存储 OAuth 提供商配置（Google、Facebook）：
- 提供商标识、Client ID、Client Secret
- OAuth URLs（authorization, token, userinfo）
- Scopes 配置
- 启用/禁用状态
- 测试状态追踪

####  ✅ 扩展 User 模型
**文件**: `backend/app/models/user.py` (已修改)

新增字段：
```python
oauth_provider: Optional[str]  # google, facebook
oauth_id: Optional[str]        # Provider's user ID
oauth_email: Optional[str]     # Email from OAuth
oauth_avatar: Optional[str]    # Avatar URL from OAuth
hashed_password: Optional[str] # Now optional for OAuth users
```

#### ✅ 数据库迁移
**文件**: `backend/alembic/versions/087c0df2c53b_add_oauth_support.py`

运行迁移：
```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

### 2. Schema 定义

#### ✅ OAuth Schemas
**文件**: `backend/app/schemas/oauth.py`

完整的 Pydantic schemas：
- `OAuthConfigCreate/Update/Response` - 配置管理
- `OAuthLoginRequest/Response` - 登录流程
- `OAuthCallbackResponse` - 回调处理
- `OAuthUserInfo` - 用户信息
- `OAuthTestRequest/Response` - 配置测试

### 3. 服务层

#### ✅ OAuth 服务实现
**文件**: `backend/app/utils/oauth_service.py`

核心功能：
- `OAuthProviderBase` - 抽象基类
- `GoogleOAuthProvider` - Google OAuth 2.0 完整实现
- `FacebookOAuthProvider` - Facebook OAuth 2.0 完整实现
- `OAuthService` - 服务管理器

功能：
- 生成授权 URL
- 交换 authorization code 获取 access token
- 获取用户信息
- CSRF 保护（state 参数）

### 4. API 端点

#### ✅ 用户 OAuth API
**文件**: `backend/app/api/oauth.py`

端点：
- `POST /api/v1/oauth/{provider}/login` - 发起 OAuth 登录
- `GET /api/v1/oauth/{provider}/callback` - OAuth 回调处理
- `POST /api/v1/oauth/{provider}/unlink` - 解除绑定

功能：
- 自动创建或链接用户账户
- 生成 JWT tokens
- 登录日志记录
- 管理员通知

#### ✅ 管理员 OAuth API
**文件**: `backend/app/admin/oauth_management.py`

端点：
- `GET /api/v1/admin/oauth/configs` - 获取所有配置（superadmin）
- `GET /api/v1/admin/oauth/configs/public` - 获取公开配置
- `GET /api/v1/admin/oauth/configs/{provider}` - 获取单个配置
- `POST /api/v1/admin/oauth/configs` - 创建配置
- `PUT /api/v1/admin/oauth/configs/{provider}` - 更新配置
- `DELETE /api/v1/admin/oauth/configs/{provider}` - 删除配置
- `POST /api/v1/admin/oauth/configs/{provider}/test` - 测试配置

### 5. 路由注册

#### ✅ FastAPI 路由配置
**文件**: `backend/app/main.py` (已修改)

已注册：
- OAuth 用户 API: `/api/v1/oauth/*`
- OAuth 管理 API: `/api/v1/admin/oauth/*`

---

## 🚧 待完成的前端工作

### 1. 用户前端 (frontend/)

#### 📝 创建 OAuthButtons 组件
**新建**: `frontend/src/components/OAuthButtons/index.tsx`

```tsx
import { useTranslation } from 'react-i18next'
import { FcGoogle } from 'react-icons/fc'
import { FaFacebook } from 'react-icons/fa'
import { initiateOAuthLogin } from '@/services/oauthService'

const OAuthButtons = () => {
  const { t } = useTranslation()

  const handleOAuthLogin = async (provider: 'google' | 'facebook') => {
    try {
      const { authorization_url } = await initiateOAuthLogin(provider)
      // Redirect to OAuth provider
      window.location.href = authorization_url
    } catch (error) {
      console.error(`${provider} login failed:`, error)
    }
  }

  return (
    <div className="space-y-3">
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-gray-700"></div>
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-2 bg-gray-800 text-gray-400">
            {t('auth.orContinueWith')}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <button
          onClick={() => handleOAuthLogin('google')}
          className="flex items-center justify-center px-4 py-2 border border-gray-600 rounded-lg hover:bg-gray-700 transition-colors"
        >
          <FcGoogle className="w-5 h-5 mr-2" />
          <span className="text-sm">Google</span>
        </button>

        <button
          onClick={() => handleOAuthLogin('facebook')}
          className="flex items-center justify-center px-4 py-2 border border-gray-600 rounded-lg hover:bg-gray-700 transition-colors"
        >
          <FaFacebook className="w-5 h-5 mr-2 text-blue-600" />
          <span className="text-sm">Facebook</span>
        </button>
      </div>
    </div>
  )
}

export default OAuthButtons
```

#### 📝 创建 OAuth 服务
**新建**: `frontend/src/services/oauthService.ts`

```typescript
import api from './api'

export interface OAuthLoginResponse {
  authorization_url: string
  state: string
}

export interface OAuthCallbackResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: any
}

export const initiateOAuthLogin = async (provider: 'google' | 'facebook'): Promise<OAuthLoginResponse> => {
  const response = await api.post(`/oauth/${provider}/login`)
  return response.data
}

export const handleOAuthCallback = async (
  provider: string,
  code: string,
  state: string
): Promise<OAuthCallbackResponse> => {
  const response = await api.get(`/oauth/${provider}/callback`, {
    params: { code, state }
  })
  return response.data
}

export const unlinkOAuthAccount = async (provider: string) => {
  const response = await api.post(`/oauth/${provider}/unlink`)
  return response.data
}
```

#### 📝 创建 OAuth 回调页面
**新建**: `frontend/src/pages/OAuthCallback/index.tsx`

```tsx
import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { handleOAuthCallback } from '@/services/oauthService'
import { useAuthStore } from '@/store/authStore'
import toast from 'react-hot-toast'

const OAuthCallback = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()
  const [error, setError] = useState<string>('')

  useEffect(() => {
    const processCallback = async () => {
      const code = searchParams.get('code')
      const state = searchParams.get('state')
      const provider = window.location.pathname.split('/')[2] // Extract provider from path

      if (!code || !state) {
        setError('Invalid OAuth callback parameters')
        return
      }

      try {
        const response = await handleOAuthCallback(provider, code, state)

        // Store tokens
        localStorage.setItem('access_token', response.access_token)
        localStorage.setItem('refresh_token', response.refresh_token)

        // Update auth state
        setAuth(response.user, response.access_token)

        toast.success(`Welcome ${response.user.username}!`)
        navigate('/')
      } catch (err: any) {
        const errorMsg = err.response?.data?.detail || 'OAuth login failed'
        setError(errorMsg)
        toast.error(errorMsg)

        // Redirect to login after 3 seconds
        setTimeout(() => navigate('/login'), 3000)
      }
    }

    processCallback()
  }, [searchParams, navigate, setAuth])

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl text-red-500 mb-4">Login Failed</h2>
          <p className="text-gray-400">{error}</p>
          <p className="text-gray-500 mt-2">Redirecting to login...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-red-600 mb-4"></div>
        <p className="text-gray-400">Completing login...</p>
      </div>
    </div>
  )
}

export default OAuthCallback
```

#### 📝 更新登录页面
**修改**: `frontend/src/pages/Login/index.tsx`

在表单下方添加：
```tsx
import OAuthButtons from '@/components/OAuthButtons'

// 在表单的 </form> 标签后添加：
<OAuthButtons />
```

#### 📝 更新注册页面
**修改**: `frontend/src/pages/Register/index.tsx`

同样添加 OAuthButtons 组件。

#### 📝 添加路由
**修改**: `frontend/src/App.tsx` 或路由配置文件

```tsx
import OAuthCallback from '@/pages/OAuthCallback'

// 添加路由：
<Route path="/oauth/:provider/callback" element={<OAuthCallback />} />
```

#### 📝 添加翻译
**修改**: `frontend/src/i18n/locales/en-US.json`

```json
{
  "auth": {
    "orContinueWith": "Or continue with",
    "oauthError": "OAuth login failed",
    "oauthSuccess": "Login successful",
    "unlinkOAuth": "Unlink {provider} account",
    "unlinkOAuthConfirm": "Are you sure you want to unlink your {provider} account?"
  }
}
```

**修改**: `frontend/src/i18n/locales/zh-CN.json`

```json
{
  "auth": {
    "orContinueWith": "或使用以下方式继续",
    "oauthError": "OAuth 登录失败",
    "oauthSuccess": "登录成功",
    "unlinkOAuth": "解除绑定 {provider} 账号",
    "unlinkOAuthConfirm": "确定要解除绑定您的 {provider} 账号吗？"
  }
}
```

#### 📝 安装依赖
```bash
cd frontend
pnpm add react-icons  # For Google/Facebook icons
```

---

### 2. 管理后台 (admin-frontend/)

#### 📝 创建 OAuth 配置页面
**新建**: `admin-frontend/src/pages/OAuthSettings/index.tsx`

这是一个完整的 Ant Design 管理页面，包含：
- OAuth 提供商列表（Google, Facebook）
- 配置表单（Client ID, Client Secret, Scopes）
- 启用/禁用开关
- 测试按钮
- Redirect URI 显示（只读）

由于代码较长（约 300+ 行），我建议您使用以下结构：

```tsx
import { useState, useEffect } from 'react'
import { Card, Form, Input, Switch, Button, Tabs, Alert, Space, Tag } from 'antd'
import { useQuery, useMutation } from '@tanstack/react-query'
import axios from '@/utils/axios'

const OAuthSettings = () => {
  // 1. 获取配置列表
  const { data: configs } = useQuery({
    queryKey: ['oauth-configs'],
    queryFn: async () => {
      const res = await axios.get('/api/v1/admin/oauth/configs')
      return res.data
    }
  })

  // 2. 更新配置 mutation
  const updateMutation = useMutation({
    mutationFn: async ({ provider, data }: any) => {
      return await axios.put(`/api/v1/admin/oauth/configs/${provider}`, data)
    }
  })

  // 3. 测试配置 mutation
  const testMutation = useMutation({
    mutationFn: async (provider: string) => {
      return await axios.post(`/api/v1/admin/oauth/configs/${provider}/test`)
    }
  })

  return (
    <div>
      <h1>OAuth 第三方登录配置</h1>

      <Tabs>
        <Tabs.TabPane tab="Google" key="google">
          {/* Google 配置表单 */}
        </Tabs.TabPane>
        <Tabs.TabPane tab="Facebook" key="facebook">
          {/* Facebook 配置表单 */}
        </Tabs.TabPane>
      </Tabs>

      {/* 配置说明文档 */}
      <Card title="配置指南">
        <Alert message="Google OAuth 配置步骤" type="info" />
        {/* 步骤说明 */}
      </Card>
    </div>
  )
}
```

#### 📝 添加路由
**修改**: `admin-frontend/src/App.tsx`

```tsx
import OAuthSettings from '@/pages/OAuthSettings'

// 添加路由：
<Route path="/oauth-settings" element={<OAuthSettings />} />
```

#### 📝 添加菜单项
在侧边栏菜单中添加"OAuth 配置"项。

---

## 🔧 OAuth 配置步骤

### Google OAuth 配置

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建项目或选择现有项目
3. 启用 **Google+ API**
4. OAuth 同意屏幕：
   - 用户类型：外部
   - 应用名称：VideoSite
   - Scopes: email, profile, openid
5. 凭据 → 创建凭据 → OAuth 2.0 客户端 ID：
   - 应用类型：Web 应用
   - 授权重定向 URI: `http://localhost:8000/api/v1/oauth/google/callback`
   - 生产环境: `https://yourdomain.com/api/v1/oauth/google/callback`
6. 复制 **Client ID** 和 **Client Secret**

### Facebook OAuth 配置

1. 访问 [Facebook Developers](https://developers.facebook.com/)
2. 创建应用 → 选择"消费者"类型
3. 添加产品 → **Facebook 登录** → Web
4. 设置 → 基本：
   - 获取**应用 ID**（Client ID）
   - 获取**应用密钥**（Client Secret）
5. Facebook 登录 → 设置：
   - 有效 OAuth 重定向 URI: `http://localhost:8000/api/v1/oauth/facebook/callback`
   - 生产环境: `https://yourdomain.com/api/v1/oauth/facebook/callback`

---

## 🧪 测试流程

### 1. 数据库迁移
```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

### 2. 创建 OAuth 配置（通过 Admin API）

```bash
# Google
curl -X POST "http://localhost:8000/api/v1/admin/oauth/configs" \
  -H "Authorization: Bearer <superadmin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "google",
    "client_id": "YOUR_GOOGLE_CLIENT_ID",
    "client_secret": "YOUR_GOOGLE_CLIENT_SECRET",
    "redirect_uri": "http://localhost:8000/api/v1/oauth/google/callback",
    "scopes": ["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"],
    "enabled": true
  }'

# Facebook
curl -X POST "http://localhost:8000/api/v1/admin/oauth/configs" \
  -H "Authorization: Bearer <superadmin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "facebook",
    "client_id": "YOUR_FACEBOOK_APP_ID",
    "client_secret": "YOUR_FACEBOOK_APP_SECRET",
    "redirect_uri": "http://localhost:8000/api/v1/oauth/facebook/callback",
    "scopes": ["email", "public_profile"],
    "enabled": true
  }'
```

### 3. 测试 OAuth 登录流程

1. 访问前端登录页面
2. 点击 Google 或 Facebook 按钮
3. 跳转到 OAuth 提供商授权页面
4. 授权后自动跳转回应用
5. 检查是否成功登录

### 4. API 测试（Swagger UI）

访问 http://localhost:8000/api/docs

测试端点：
- `POST /api/v1/oauth/google/login`
- `GET /api/v1/oauth/google/callback?code=xxx&state=xxx`

---

## 📁 文件清单

### 后端 (已完成)
- ✅ `backend/app/models/oauth_config.py`
- ✅ `backend/app/models/user.py` (修改)
- ✅ `backend/app/models/__init__.py` (修改)
- ✅ `backend/app/schemas/oauth.py`
- ✅ `backend/app/utils/oauth_service.py`
- ✅ `backend/app/api/oauth.py`
- ✅ `backend/app/admin/oauth_management.py`
- ✅ `backend/app/main.py` (修改)
- ✅ `backend/alembic/versions/087c0df2c53b_add_oauth_support.py`

### 前端 (待完成)
- ⏳ `frontend/src/components/OAuthButtons/index.tsx`
- ⏳ `frontend/src/services/oauthService.ts`
- ⏳ `frontend/src/pages/OAuthCallback/index.tsx`
- ⏳ `frontend/src/pages/Login/index.tsx` (修改)
- ⏳ `frontend/src/pages/Register/index.tsx` (修改)
- ⏳ `frontend/src/App.tsx` (修改 - 添加路由)
- ⏳ `frontend/src/i18n/locales/en-US.json` (修改)
- ⏳ `frontend/src/i18n/locales/zh-CN.json` (修改)

### 管理后台 (待完成)
- ⏳ `admin-frontend/src/pages/OAuthSettings/index.tsx`
- ⏳ `admin-frontend/src/App.tsx` (修改 - 添加路由)
- ⏳ `admin-frontend/src/i18n/locales/en-US.json` (修改)
- ⏳ `admin-frontend/src/i18n/locales/zh-CN.json` (修改)

---

## 🔒 安全注意事项

1. **Client Secret 加密**
   - 生产环境应使用加密存储 client_secret
   - 考虑使用 Fernet 或类似加密库

2. **State 参数**
   - 当前使用内存存储，生产环境应使用 Redis
   - 设置 TTL（10 分钟过期）

3. **HTTPS**
   - 生产环境必须使用 HTTPS
   - OAuth 回调 URL 必须是 HTTPS

4. **Redirect URI 白名单**
   - 在 OAuth 提供商控制台严格配置允许的 Redirect URI

5. **环境变量**
   - 不要在代码中硬编码 credentials
   - 使用 `.env` 文件（不要提交到 git）

---

## 📖 参考文档

- [Google OAuth 2.0 文档](https://developers.google.com/identity/protocols/oauth2)
- [Facebook Login 文档](https://developers.facebook.com/docs/facebook-login/)
- [FastAPI OAuth2 最佳实践](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)

---

## 🎯 下一步

1. 运行数据库迁移：`alembic upgrade head`
2. 在管理后台配置 Google/Facebook OAuth
3. 完成前端 OAuthButtons 组件
4. 添加 OAuth 回调页面
5. 测试完整登录流程
6. 部署到生产环境

---

## 🆘 故障排除

### 问题：redirect_uri_mismatch
**解决**: 确保 OAuth 配置中的 `redirect_uri` 与 Google/Facebook 控制台中配置的完全一致（包括协议、域名、路径）

### 问题：无法获取 email
**解决**: 检查 scopes 是否包含 email 相关权限

### 问题：State 参数不匹配
**解决**: 检查是否在多个服务器实例间共享状态，建议使用 Redis

---

**实施完成度**: 后端 100% ✅ | 前端 0% ⏳ | 管理后台 0% ⏳

**预估剩余工作时间**: 3-4 小时
