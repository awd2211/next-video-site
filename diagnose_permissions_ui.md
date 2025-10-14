# 权限列表不显示 - 诊断指南

## 问题现象
在管理后台的"角色管理" → "权限列表"标签页，看不到任何权限。

## 数据验证 ✅
- ✅ 数据库有 36 个权限
- ✅ 数据库有 9 个角色
- ✅ 有 superadmin 账户
- ✅ 后端服务运行正常

## 最可能的原因

### 1. 权限要求问题（最常见）

**问题:** GET `/api/v1/admin/rbac/permissions` 需要 **superadmin** 权限

**检查方法:**
1. 打开浏览器开发者工具 (F12)
2. 切换到 **Network** 标签
3. 刷新角色管理页面
4. 找到 `/api/v1/admin/rbac/permissions` 请求
5. 查看状态码:
   - **403 Forbidden** → 你不是 superadmin
   - **200 OK** → API 正常，前端渲染有问题
   - **401 Unauthorized** → Token 过期

**解决方法:**
- 使用 superadmin 账户登录（admin 或 ai_admin）
- 确认账户密码正确

### 2. 前端渲染问题

**检查方法:**
1. 打开浏览器开发者工具 (F12)
2. 切换到 **Console** 标签
3. 查看是否有 JavaScript 错误

**可能的错误:**
```javascript
// 常见错误示例
TypeError: Cannot read property 'grouped' of undefined
TypeError: permissionsData.grouped is undefined
```

**解决方法:**
- 检查 `permissionsData` 是否正确加载
- 查看 React Query 的加载状态

### 3. API 响应格式问题

**检查方法:**
1. 打开浏览器开发者工具 (F12)
2. Network → 找到 `/api/v1/admin/rbac/permissions`
3. 点击查看 **Response** 标签
4. 确认响应格式:

**预期格式:**
```json
{
  "permissions": [...],
  "grouped": {
    "video": [
      {"id": 40, "name": "查看视频", "code": "video.read", "module": "video"},
      ...
    ],
    "user": [...],
    ...
  },
  "total": 36
}
```

## 立即测试步骤

### 步骤 1: 确认你的登录账户

在浏览器控制台执行：
```javascript
// 查看当前用户信息
console.log(JSON.parse(localStorage.getItem('user')))

// 应该看到:
// { ..., "is_superadmin": true, ... }
```

如果 `is_superadmin` 是 `false`，**重新用 superadmin 账户登录**。

### 步骤 2: 检查 API 请求

在浏览器控制台执行：
```javascript
// 直接测试 API
fetch('/api/v1/admin/rbac/permissions', {
  headers: {
    'Authorization': 'Bearer ' + JSON.parse(localStorage.getItem('token'))
  }
})
.then(res => res.json())
.then(data => console.log(data))
.catch(err => console.error(err))
```

**预期结果:**
- 应该看到包含 `permissions`, `grouped`, `total` 的对象
- `grouped` 应该是一个对象，包含各个模块的权限

**如果看到错误:**
- `403` → 不是 superadmin，重新登录
- `401` → Token 过期，重新登录
- 其他错误 → 查看错误消息

### 步骤 3: 检查前端组件状态

在浏览器控制台执行（在权限列表页面）：
```javascript
// 查看 React Query 状态
// 打开 React DevTools 或使用 TanStack Query DevTools
```

## 快速修复方案

### 方案 A: 重新登录
1. 退出当前账户
2. 使用 **admin** 账户登录
   - 用户名: `admin`
   - 邮箱: `admin@videosite.com`
3. 导航到"角色管理" → "权限列表"

### 方案 B: 检查后端权限依赖

可能需要修改后端，允许普通 admin 查看权限列表：

**文件:** `backend/app/admin/rbac.py:93-98`

**当前代码:**
```python
@router.get("/permissions", response_model=dict)
async def list_permissions(
    module: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_superadmin),  # 只允许 superadmin
):
```

**修改为:**
```python
@router.get("/permissions", response_model=dict)
async def list_permissions(
    module: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),  # 允许所有 admin
):
```

这样普通 admin 也能查看权限列表（但不能修改）。

## 测试数据

### 数据库中的权限（按模块）:
- video: 6 个权限
- user: 6 个权限
- system: 7 个权限
- comment: 4 个权限
- rbac: 3 个权限
- report: 2 个权限
- 其他模块: 各 1 个权限

### 可用的 superadmin 账户:
1. admin (ID: 5)
2. ai_admin (ID: 7)

## 常见错误及解决方案

| 错误 | 原因 | 解决方法 |
|------|------|----------|
| 权限列表空白 | 不是 superadmin | 用 superadmin 登录 |
| 403 Forbidden | API 权限不足 | 检查账户权限 |
| 401 Unauthorized | Token 过期 | 重新登录 |
| TypeError | 前端数据格式错误 | 检查 API 响应格式 |
| Loading 一直转 | API 请求失败 | 检查网络和后端状态 |

## 下一步

1. **首先**: 确认你用的是 superadmin 账户
2. **然后**: 打开浏览器开发者工具，查看网络请求
3. **最后**: 根据具体错误信息进行排查

## 需要更多帮助？

请提供：
1. 浏览器控制台的错误信息（Console 标签）
2. API 请求的响应内容（Network 标签）
3. 当前登录的账户信息
4. 截图（如果可能）
