# 修复 "Invalid status value" 错误

## 错误信息
```
Invalid status value. Must be one of: draft, published, archived
```

## 原因分析

这个错误说明你正在访问视频列表 API 时使用了**无效的 status 参数**。

### VideoStatus 的有效值
```python
# backend/app/models/video.py
class VideoStatus(str, enum.Enum):
    DRAFT = "draft"         # 草稿
    PUBLISHED = "published" # 已发布
    ARCHIVED = "archived"   # 已归档
```

❌ **不支持**: `pending`, `active`, `inactive` 等其他值

## 可能的触发场景

### 1. 直接访问带参数的 URL
```
http://localhost:3001/videos?status=pending  ❌ 错误
http://localhost:3001/videos?status=draft    ✅ 正确
```

### 2. 浏览器缓存的旧 URL
- 浏览器可能保存了之前的 URL 参数
- 需要清除缓存或手动修改 URL

### 3. 前端代码中的硬编码值（极少见）
- 某些页面可能硬编码了错误的 status 值

## 快速修复方案

### 方案 A: 清除 URL 参数（推荐）

1. **访问视频列表页面时，不要带 status 参数**
   ```
   http://localhost:3001/videos
   ```

2. **如果 URL 中有 status 参数，手动删除**
   ```
   从: http://localhost:3001/videos?status=pending
   改为: http://localhost:3001/videos
   ```

3. **刷新页面**
   - 按 F5 或 Ctrl+R

### 方案 B: 使用正确的 status 值

如果你需要筛选视频状态，使用这些值：

| 中文 | 英文 | URL 参数 |
|------|------|----------|
| 草稿 | Draft | `?status=draft` |
| 已发布 | Published | `?status=published` |
| 已归档 | Archived | `?status=archived` |

**示例:**
```
查看草稿: http://localhost:3001/videos?status=draft
查看已发布: http://localhost:3001/videos?status=published
查看已归档: http://localhost:3001/videos?status=archived
```

### 方案 C: 清除浏览器缓存

如果问题持续，清除浏览器缓存：

**在浏览器控制台执行:**
```javascript
// 清除 localStorage
localStorage.clear()

// 清除 sessionStorage
sessionStorage.clear()

// 刷新页面
location.reload()
```

## 前端状态选择器

视频列表页面的状态选择器应该只显示这三个选项：

```tsx
<Select
  placeholder="选择状态"
  onChange={(value) => setStatus(value)}
  allowClear
>
  <Option value="draft">草稿</Option>
  <Option value="published">已发布</Option>
  <Option value="archived">已归档</Option>
</Select>
```

## 与内容调度的区别

**重要:** 不要混淆两种不同的状态！

### VideoStatus (视频状态)
用于视频本身的状态管理：
- `draft` - 草稿
- `published` - 已发布
- `archived` - 已归档

### SchedulingStatus (调度状态)
用于内容调度系统的状态：
- `PENDING` - 待发布 ✅ 这里可以用
- `PUBLISHED` - 已发布
- `CANCELLED` - 已取消
- `FAILED` - 失败

**这就是为什么你在"内容调度"页面看到 pending，但在"视频列表"页面不能用！**

## 测试步骤

### 1. 访问视频列表（无参数）
```bash
# 在浏览器中访问
http://localhost:3001/videos
```
**预期:** 显示所有视频，无错误

### 2. 测试草稿状态筛选
```bash
# 在浏览器中访问
http://localhost:3001/videos?status=draft
```
**预期:** 只显示草稿视频，无错误

### 3. 测试已发布状态筛选
```bash
# 在浏览器中访问
http://localhost:3001/videos?status=published
```
**预期:** 只显示已发布视频，无错误

### 4. 测试无效状态（验证错误处理）
```bash
# 在浏览器中访问
http://localhost:3001/videos?status=pending
```
**预期:** 显示友好错误消息
```
Invalid status value. Must be one of: draft, published, archived
```

## API 测试

### 使用 curl 测试（需要 token）

```bash
# 获取 token
TOKEN=$(curl -s -X POST 'http://localhost:8000/api/v1/admin/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"superadmin","password":"superadmin123"}' | jq -r '.access_token')

# 测试正确的状态值
curl -H "Authorization: Bearer $TOKEN" \
  'http://localhost:8000/api/v1/admin/videos?status=draft' | jq '.total'
# 应该返回数字（草稿视频数量）

# 测试错误的状态值
curl -H "Authorization: Bearer $TOKEN" \
  'http://localhost:8000/api/v1/admin/videos?status=pending'
# 应该返回错误消息
```

## 前端代码检查

如果问题持续，检查前端代码：

### 文件位置
- `admin-frontend/src/pages/Videos/List.tsx`
- `admin-frontend/src/services/videoService.ts`

### 检查点
1. **状态选择器的选项值**
   ```tsx
   // 应该只有这三个选项
   <Option value="draft">草稿</Option>
   <Option value="published">已发布</Option>
   <Option value="archived">已归档</Option>
   ```

2. **API 请求参数**
   ```typescript
   // 检查是否有硬编码的 status 参数
   axios.get('/api/v1/admin/videos', {
     params: { status: 'pending' } // ❌ 这样是错误的
   })
   ```

3. **URL 参数读取**
   ```typescript
   // 如果从 URL 读取参数，确保验证
   const searchParams = new URLSearchParams(location.search)
   const status = searchParams.get('status')

   // 验证 status 值
   const validStatuses = ['draft', 'published', 'archived']
   if (status && !validStatuses.includes(status)) {
     // 处理无效值
   }
   ```

## 开发建议

### 1. 添加前端验证
在前端也添加状态值验证，避免发送无效请求：

```typescript
// utils/validators.ts
export const VIDEO_STATUSES = ['draft', 'published', 'archived'] as const
export type VideoStatus = typeof VIDEO_STATUSES[number]

export function isValidVideoStatus(status: any): status is VideoStatus {
  return VIDEO_STATUSES.includes(status)
}
```

### 2. 统一状态管理
创建一个状态常量文件：

```typescript
// constants/videoStatus.ts
export const VIDEO_STATUS = {
  DRAFT: 'draft',
  PUBLISHED: 'published',
  ARCHIVED: 'archived',
} as const

export const VIDEO_STATUS_LABELS = {
  draft: '草稿',
  published: '已发布',
  archived: '已归档',
} as const
```

### 3. 使用 TypeScript 类型
```typescript
type VideoStatus = 'draft' | 'published' | 'archived'

function fetchVideos(status?: VideoStatus) {
  // TypeScript 会在编译时检查类型
}
```

## 常见问题

### Q: 为什么内容调度可以用 "pending"，但视频列表不行？
**A:** 这是两个不同的状态系统：
- **VideoStatus** (视频状态) - 用于视频本身
- **SchedulingStatus** (调度状态) - 用于定时发布任务

### Q: 我需要添加 "pending" 状态到 VideoStatus 吗？
**A:** 通常不需要。如果你需要"待审核"功能：
1. 修改枚举添加 PENDING
2. 创建数据库迁移
3. 更新前端选择器

### Q: 这个错误会影响系统功能吗？
**A:** 不会。这是一个友好的错误提示，帮助你发现并修正无效的参数。

## 总结

✅ **修复已完成**: 后端已添加状态值验证
✅ **错误提示清晰**: 告诉你有效的状态值
✅ **解决方案简单**: 使用正确的状态值或不带参数访问

**立即行动:**
1. 访问 http://localhost:3001/videos （不带任何参数）
2. 使用状态筛选器选择状态（不要手动输入 URL）
3. 如果有问题，清除浏览器缓存

---

**相关文档:**
- [VALIDATION_ERROR_FIX.md](VALIDATION_ERROR_FIX.md) - 验证错误修复详情
- [ADMIN_ACCOUNTS.md](ADMIN_ACCOUNTS.md) - 管理员账户信息
- [PERMISSION_LIST_FIX.md](PERMISSION_LIST_FIX.md) - 权限列表修复详情
