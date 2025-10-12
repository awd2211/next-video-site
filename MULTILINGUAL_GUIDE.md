# 多语言支持实施指南

**编写日期**: 2025-10-11  
**适用项目**: VideoSite

---

## 🎯 快速答案

### Q: 多语言需要后端支持吗？

**A: 90%的情况下不需要！**

- ✅ **纯前端国际化**（推荐）: 不需要后端改动
- ⚠️ **后端 API 国际化**（可选）: 需要后端支持
- 📦 **数据库内容多语言**（高级）: 需要后端和数据库改动

---

## 📊 三种方案对比

| 方案             | 后端改动  | 前端改动 | 适用场景     | 推荐度 |
| ---------------- | --------- | -------- | ------------ | ------ |
| 纯前端国际化     | ❌ 不需要 | ✅ 需要  | 界面翻译     | ⭐⭐⭐ |
| 后端 API 国际化  | ✅ 需要   | ✅ 需要  | API 消息翻译 | ⭐     |
| 数据库内容多语言 | ✅ 需要   | ✅ 需要  | 内容全球化   | ⭐     |

---

## 方案 1: 纯前端国际化（推荐）

### ✅ 优势

- 不需要后端改动
- 实施简单快速（2-3 天）
- 切换语言无需请求服务器
- 用户体验好（即时切换）

### 实施步骤

#### 1. 安装依赖

```bash
# 前端用户界面
cd frontend
pnpm add react-i18next i18next i18next-browser-languagedetector

# 管理后台
cd admin-frontend
pnpm add react-i18next i18next i18next-browser-languagedetector
```

#### 2. 创建翻译文件

**文件结构**:

```
frontend/src/
├── i18n/
│   ├── config.ts          # i18n配置
│   └── locales/
│       ├── zh-CN/
│       │   ├── common.ts  # 通用翻译
│       │   ├── video.ts   # 视频相关
│       │   ├── user.ts    # 用户相关
│       │   └── index.ts
│       └── en-US/
│           ├── common.ts
│           ├── video.ts
│           ├── user.ts
│           └── index.ts
```

**示例翻译文件**:

```typescript
// frontend/src/i18n/locales/zh-CN/common.ts
export default {
  // 通用按钮
  button: {
    search: '搜索',
    submit: '提交',
    cancel: '取消',
    confirm: '确认',
    save: '保存',
    delete: '删除',
    edit: '编辑',
    back: '返回',
  },

  // 通用标签
  label: {
    username: '用户名',
    email: '邮箱',
    password: '密码',
    confirmPassword: '确认密码',
  },

  // 通用消息
  message: {
    success: '操作成功',
    error: '操作失败',
    loading: '加载中...',
    noData: '暂无数据',
  },

  // 导航
  nav: {
    home: '首页',
    videos: '视频',
    categories: '分类',
    favorites: '收藏',
    history: '历史',
    profile: '个人中心',
  },
};

// frontend/src/i18n/locales/en-US/common.ts
export default {
  button: {
    search: 'Search',
    submit: 'Submit',
    cancel: 'Cancel',
    confirm: 'Confirm',
    save: 'Save',
    delete: 'Delete',
    edit: 'Edit',
    back: 'Back',
  },

  label: {
    username: 'Username',
    email: 'Email',
    password: 'Password',
    confirmPassword: 'Confirm Password',
  },

  message: {
    success: 'Success',
    error: 'Error',
    loading: 'Loading...',
    noData: 'No Data',
  },

  nav: {
    home: 'Home',
    videos: 'Videos',
    categories: 'Categories',
    favorites: 'Favorites',
    history: 'History',
    profile: 'Profile',
  },
};
```

#### 3. 配置 i18n

```typescript
// frontend/src/i18n/config.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import zhCN from './locales/zh-CN';
import enUS from './locales/en-US';

i18n
  .use(LanguageDetector) // 自动检测浏览器语言
  .use(initReactI18next)
  .init({
    resources: {
      'zh-CN': { translation: zhCN },
      'en-US': { translation: enUS },
    },
    fallbackLng: 'zh-CN', // 默认语言

    detection: {
      // 语言检测顺序
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
    },

    interpolation: {
      escapeValue: false, // React已经转义
    },
  });

export default i18n;
```

#### 4. 在 main.tsx 中引入

```typescript
// frontend/src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import './i18n/config'; // 导入i18n配置
import App from './App';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

#### 5. 在组件中使用

```typescript
// 示例：Header组件
import { useTranslation } from 'react-i18next';

export function Header() {
  const { t } = useTranslation();

  return (
    <nav>
      <Link to="/">{t('nav.home')}</Link>
      <Link to="/videos">{t('nav.videos')}</Link>
      <Link to="/favorites">{t('nav.favorites')}</Link>
    </nav>
  );
}

// 示例：搜索框
export function SearchBar() {
  const { t } = useTranslation();

  return <input type="text" placeholder={t('button.search')} />;
}
```

#### 6. 语言切换器组件

```typescript
// components/LanguageSwitcher/index.tsx
import { useTranslation } from 'react-i18next';
import { Globe } from 'lucide-react';

export function LanguageSwitcher() {
  const { i18n } = useTranslation();

  const languages = [
    { code: 'zh-CN', name: '简体中文', flag: '🇨🇳' },
    { code: 'en-US', name: 'English', flag: '🇺🇸' },
  ];

  const changeLanguage = (lang: string) => {
    i18n.changeLanguage(lang);
  };

  return (
    <div className="language-switcher">
      <Globe size={20} />
      <select
        value={i18n.language}
        onChange={(e) => changeLanguage(e.target.value)}
        className="ml-2"
      >
        {languages.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.flag} {lang.name}
          </option>
        ))}
      </select>
    </div>
  );
}
```

#### 7. 处理后端错误消息

**前端统一处理**（不需要后端改动）:

```typescript
// utils/errorMessages.ts
export const errorMessages = {
  'zh-CN': {
    'Video not found': '视频不存在',
    Unauthorized: '未授权，请先登录',
    'Email already registered': '该邮箱已被注册',
    'Incorrect email or password': '邮箱或密码错误',
  },
  'en-US': {
    'Video not found': 'Video not found',
    Unauthorized: 'Unauthorized, please login first',
    'Email already registered': 'Email already registered',
    'Incorrect email or password': 'Incorrect email or password',
  },
};

// 使用
import { useTranslation } from 'react-i18next';

function handleApiError(error: any) {
  const { i18n } = useTranslation();
  const backendMessage = error.response?.data?.detail || 'Unknown error';

  // 尝试翻译后端消息
  const translatedMessage = errorMessages[i18n.language]?.[backendMessage] || backendMessage;

  toast.error(translatedMessage);
}
```

---

## 方案 2: 后端 API 国际化（可选）

### 什么时候需要？

**需要后端支持的场景**:

- ✅ 想要 API 本身返回翻译后的消息
- ✅ 多个客户端（Web、iOS、Android）都需要多语言
- ✅ 邮件通知需要多语言

**不需要后端支持的场景**:

- ❌ 只是前端界面翻译
- ❌ 错误消息数量少（前端映射即可）

### 实施方案（如果需要）

#### 后端代码

```python
# app/utils/i18n.py
from typing import Dict, Optional
from fastapi import Request

class I18nManager:
    """国际化管理器"""

    # 翻译字典
    translations: Dict[str, Dict[str, str]] = {
        "zh-CN": {
            "video_not_found": "视频不存在",
            "user_not_found": "用户不存在",
            "unauthorized": "未授权，请先登录",
            "email_already_exists": "该邮箱已被注册",
            "username_already_exists": "该用户名已被使用",
            "incorrect_credentials": "邮箱或密码错误",
            "validation_failed": "数据验证失败",
            "server_error": "服务器错误，请稍后重试",
        },
        "en-US": {
            "video_not_found": "Video not found",
            "user_not_found": "User not found",
            "unauthorized": "Unauthorized, please login first",
            "email_already_exists": "Email already registered",
            "username_already_exists": "Username already taken",
            "incorrect_credentials": "Incorrect email or password",
            "validation_failed": "Validation failed",
            "server_error": "Server error, please try again later",
        }
    }

    @staticmethod
    def get_language(request: Request) -> str:
        """
        从请求头获取首选语言

        支持：
        - Accept-Language 头
        - X-Language 自定义头
        - 默认: zh-CN
        """
        # 优先使用自定义头
        custom_lang = request.headers.get("X-Language")
        if custom_lang and custom_lang in I18nManager.translations:
            return custom_lang

        # 解析 Accept-Language
        accept_lang = request.headers.get("Accept-Language", "")
        if accept_lang:
            # Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
            primary_lang = accept_lang.split(',')[0].split(';')[0].strip()

            # 完全匹配
            if primary_lang in I18nManager.translations:
                return primary_lang

            # 模糊匹配（zh -> zh-CN）
            lang_prefix = primary_lang.split('-')[0]
            for supported_lang in I18nManager.translations.keys():
                if supported_lang.startswith(lang_prefix):
                    return supported_lang

        # 默认语言
        return "zh-CN"

    @staticmethod
    def t(key: str, lang: str = "zh-CN", **kwargs) -> str:
        """
        翻译文本

        Args:
            key: 翻译键
            lang: 语言代码
            **kwargs: 格式化参数

        Returns:
            翻译后的文本
        """
        message = I18nManager.translations.get(lang, {}).get(key, key)

        # 支持参数格式化
        if kwargs:
            try:
                message = message.format(**kwargs)
            except (KeyError, ValueError):
                pass

        return message


# 依赖函数
async def get_language(request: Request) -> str:
    """获取请求语言（用作依赖）"""
    return I18nManager.get_language(request)
```

**在 API 中使用**:

```python
# app/api/videos.py
from app.utils.i18n import I18nManager, get_language

@router.get("/{video_id}")
async def get_video(
    video_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """获取视频详情"""
    video = await db.execute(...)

    if not video:
        lang = I18nManager.get_language(request)
        raise HTTPException(
            status_code=404,
            detail=I18nManager.t("video_not_found", lang)
        )

    return video

# 响应示例
# zh-CN: {"detail": "视频不存在"}
# en-US: {"detail": "Video not found"}
```

**更新异常处理器**:

```python
# app/main.py

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    lang = I18nManager.get_language(request)
    error_msg = str(exc.orig).lower()

    if "email" in error_msg:
        message = I18nManager.t("email_already_exists", lang)
    elif "username" in error_msg:
        message = I18nManager.t("username_already_exists", lang)
    else:
        message = I18nManager.t("validation_failed", lang)

    return JSONResponse(
        status_code=409,
        content={
            "detail": message,
            "error_code": "DUPLICATE_RESOURCE",
            "request_id": request.state.request_id,
        }
    )
```

---

## 方案 3: 混合方案（实用）⭐⭐

**后端**: 只返回错误码  
**前端**: 负责所有翻译

### 后端实现

```python
# 后端只返回标准化的错误码
raise HTTPException(
    status_code=404,
    detail="VIDEO_NOT_FOUND"  # 错误码，不是消息
)

# 响应
{
  "detail": "VIDEO_NOT_FOUND",
  "error_code": "VIDEO_NOT_FOUND",
  "request_id": "uuid..."
}
```

### 前端实现

```typescript
// frontend/src/utils/errorMessages.ts
export const ERROR_MESSAGES = {
  'zh-CN': {
    VIDEO_NOT_FOUND: '视频不存在',
    USER_NOT_FOUND: '用户不存在',
    UNAUTHORIZED: '未授权，请先登录',
    VALIDATION_ERROR: '数据验证失败',
  },
  'en-US': {
    VIDEO_NOT_FOUND: 'Video not found',
    USER_NOT_FOUND: 'User not found',
    UNAUTHORIZED: 'Unauthorized, please login first',
    VALIDATION_ERROR: 'Validation failed',
  },
};

// 使用
import { useTranslation } from 'react-i18next';

function useApiError() {
  const { i18n } = useTranslation();

  return (error: any) => {
    const errorCode = error.response?.data?.error_code || error.response?.data?.detail;

    const message = ERROR_MESSAGES[i18n.language]?.[errorCode] || errorCode || 'Unknown error';

    toast.error(message);
  };
}
```

**优势**:

- ✅ 后端改动最小（只需统一错误码）
- ✅ 前端完全控制翻译
- ✅ 易于维护和扩展

---

## 💡 推荐方案

### 对于你的项目 VideoSite

**推荐: 纯前端国际化** ⭐⭐⭐

**理由**:

1. ✅ 不需要后端改动（已完成的优化不受影响）
2. ✅ 实施简单快速
3. ✅ 性能好（无需请求服务器）
4. ✅ 你的后端错误已经很规范（有 error_code）

**实施计划**:

**第 1 步**: 前端界面国际化（2 天）

- 安装 react-i18next
- 创建翻译文件
- 添加语言切换器
- 提取硬编码文字

**第 2 步**: 前端错误消息映射（半天）

- 创建错误消息翻译表
- 处理后端错误码

**不需要第 3 步**（后端改动）✅

---

## 🔧 当前你的后端优势

你的后端**已经为国际化做好准备**：

1. ✅ **错误码已标准化**

   ```json
   {
     "detail": "Video not found",
     "error_code": "RESOURCE_NOT_FOUND", // ← 标准错误码
     "request_id": "uuid..."
   }
   ```

2. ✅ **验证错误已结构化**

   ```json
   {
     "detail": "Request validation failed",
     "error_code": "VALIDATION_ERROR",
     "errors": [{ "field": "email", "message": "...", "type": "value_error" }]
   }
   ```

3. ✅ **支持 subtitle 多语言**
   - 视频已有 `subtitle_languages` 字段
   - 字幕模型已有 `language` 字段

---

## 📋 总结

### Q: 多语言需要后端支持吗？

**A: 不需要！**（对于界面翻译）

你可以：

- ✅ 完全在前端实现（React i18next）
- ✅ 后端保持不变
- ✅ 利用现有的 error_code 做错误消息映射

### 建议

**现阶段**: 先不做多语言

- 你的用户主要是中文用户
- 功能更重要

**未来如需要**: 纯前端方案

- 2-3 天完成
- 不影响后端
- 用户体验好

---

**需要我帮你设计前端国际化方案吗？还是当前的中文版本已经足够了？**
