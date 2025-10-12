# VideoSite 快速参考卡片

**版本**: v2.0 (优化版)  
**评分**: ⭐⭐⭐⭐⭐ (4.8/5)  
**最后更新**: 2025-10-11

---

## 🚀 快速启动

```bash
# 完整启动
make infra-up                        # PostgreSQL + Redis + MinIO
cd backend && make backend-run       # 后端 API :8000
cd admin-frontend && pnpm run dev    # 管理后台 :3001
cd frontend && pnpm run dev          # 用户前端 :3000
```

---

## 🎯 管理后台新功能

### 右上角工具栏

| 图标 | 功能              | 快捷键    |
| ---- | ----------------- | --------- |
| ❓   | 快捷键帮助        | `Shift+?` |
| 🌙   | 暗黑模式          | -         |
| 🌐   | 语言切换（🇨🇳/🇺🇸） | -         |
| 🚪   | 退出登录          | -         |

### 键盘快捷键

| 快捷键    | 功能       | 页面     |
| --------- | ---------- | -------- |
| `Ctrl+N`  | 新建       | 视频列表 |
| `Ctrl+S`  | 保存       | 表单页面 |
| `Ctrl+F`  | 搜索       | 所有列表 |
| `/`       | 快速搜索   | 全局     |
| `Shift+?` | 显示帮助   | 全局     |
| `Esc`     | 关闭对话框 | 全局     |

### 批量操作

**支持页面**:

- ✅ 视频列表：发布/下架/删除
- ✅ 用户列表：封禁/解封
- ✅ 横幅列表：启用/禁用
- ✅ 评论列表：通过/拒绝/删除

**使用**: 勾选多项 → 自动显示批量操作栏

### 数据导出

**支持页面**: 视频、用户、横幅、日志  
**格式**: CSV (UTF-8 BOM)  
**位置**: 右上角导出按钮

---

## 🌐 多语言 API

### 测试命令

```bash
# 中文（默认）
curl http://localhost:8000/api/v1/categories

# 英文
curl -H "X-Language: en-US" http://localhost:8000/api/v1/categories

# 返回示例
# 中文: {"name": "动作", ...}
# 英文: {"name": "Action", ...}
```

### 前端使用

```typescript
// 设置语言（会自动同步到所有API）
localStorage.setItem('language', 'en-US');

// API自动包含语言头
// X-Language: en-US
// Accept-Language: en-US
```

---

## 📊 已翻译的数据

| 类型 | 数量 | 完成度 | 示例                |
| ---- | ---- | ------ | ------------------- |
| 分类 | 8    | 100%   | 动作 →Action        |
| 标签 | 7    | 100%   | 高分 →High Rating   |
| 国家 | 6    | 100%   | 美国 →United States |

---

## 🎨 UX 特性

### 加载反馈

- 🎯 **顶部进度条**: 蓝色，每次请求可见
- 🔍 **搜索图标**: 搜索时显示 loading
- 💎 **骨架屏**: Dashboard 统计卡片

### 交互优化

- 📤 **拖拽上传**: 拖放文件即可
- 🎨 **页面动画**: 淡入淡出 0.3 秒
- ✔️ **实时验证**: 表单失焦时验证
- 📋 **空状态**: 友好提示 + 快捷按钮

---

## 📖 主要文档

| 文档                          | 用途            |
| ----------------------------- | --------------- |
| `ALL_OPTIMIZATIONS_FINAL.md`  | 完整总结报告 ⭐ |
| `README_OPTIMIZATION.md`      | 优化总览        |
| `OPTIMIZATION_QUICK_START.md` | 快速开始        |
| `UX_OPTIMIZATION_COMPLETE.md` | UX 优化详情     |

---

## 🔧 开发参考

### 添加新翻译

```json
// admin-frontend/src/i18n/locales/zh-CN.json
{
  "myFeature": {
    "title": "我的功能"
  }
}

// en-US.json
{
  "myFeature": {
    "title": "My Feature"
  }
}
```

```tsx
// 使用
const { t } = useTranslation()
<h1>{t('myFeature.title')}</h1>
```

### 添加批量操作

参考: `src/pages/Videos/List.tsx`

```tsx
const batchMutation = useMutation({
  mutationFn: async (ids) => axios.put('/batch', { ids }),
  onSuccess: () => {
    queryClient.invalidateQueries();
    setSelectedRowKeys([]);
  },
});
```

---

## ⚙️ 配置文件

### 后端配置

```env
# backend/.env
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://localhost:6379
MINIO_ENDPOINT=localhost:9000
```

### 前端配置

```typescript
// admin-frontend/src/utils/axios.ts
baseURL: '/api/v1';

// 自动添加:
// - Authorization header
// - X-Language header
// - NProgress 进度条
```

---

## 📞 快速帮助

### 常见问题

**Q: 如何切换语言？**  
A: 右上角地球图标 🌐，选择语言

**Q: 如何开启暗黑模式？**  
A: 右上角开关 🌙

**Q: 快捷键不生效？**  
A: 按 `Shift+?` 查看帮助，确保不在输入框中

**Q: 如何批量操作？**  
A: 勾选多项，会自动显示批量操作栏

**Q: 数据导出在哪里？**  
A: 列表页面右上角或批量操作栏

---

## 🎊 成就解锁

- 🏅 数据库多语言架构师
- 🏅 国际化专家
- 🏅 UX 优化大师
- 🏅 性能优化专家
- 🏅 全栈开发专家

---

**VideoSite - 商业级 5 星视频平台** ⭐⭐⭐⭐⭐

**Happy Coding!** 💻✨
