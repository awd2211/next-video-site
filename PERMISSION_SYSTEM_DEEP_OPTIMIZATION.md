# 权限系统深度优化方案

## 📊 当前权限系统分析

### 现状
- **36个权限** 覆盖12个模块
- **基础RBAC**: 角色-权限-管理员三层结构
- **权限检查**: `/api/v1/admin/rbac/check-permission` 端点

### 发现的问题和优化空间

---

## 🎯 核心优化方向

### 1️⃣ **权限验证装饰器/依赖项** (高优先级) ⭐⭐⭐

#### 问题
当前只有基础的权限检查,**没有便捷的权限验证装饰器**:
- 每个需要权限的路由都要手动检查
- 代码重复,不易维护
- 没有统一的权限验证机制

#### 解决方案
创建 `require_permission` 依赖项装饰器:

```python
# backend/app/utils/permissions.py
from typing import List
from fastapi import Depends, HTTPException
from app.utils.dependencies import get_current_admin_user

def require_permission(*permission_codes: str):
    """权限验证依赖项装饰器"""
    async def permission_checker(
        current_admin: AdminUser = Depends(get_current_admin_user),
        db: AsyncSession = Depends(get_db)
    ) -> AdminUser:
        # 超级管理员跳过检查
        if current_admin.is_superadmin:
            return current_admin

        # 加载管理员角色和权限
        result = await db.execute(
            select(AdminUser)
            .where(AdminUser.id == current_admin.id)
            .options(selectinload(AdminUser.role).selectinload(Role.permissions))
        )
        admin = result.scalar_one()

        if not admin.role:
            raise HTTPException(
                status_code=403,
                detail="您没有任何角色，无法执行此操作"
            )

        # 检查权限
        user_permissions = {p.code for p in admin.role.permissions}
        required_permissions = set(permission_codes)

        if not required_permissions.issubset(user_permissions):
            missing = required_permissions - user_permissions
            raise HTTPException(
                status_code=403,
                detail=f"权限不足，需要: {', '.join(missing)}"
            )

        return current_admin

    return permission_checker

# 使用示例
@router.post("/videos", dependencies=[Depends(require_permission("video.create"))])
async def create_video(...):
    # 无需手动检查权限
    pass

@router.delete("/videos/{id}", dependencies=[Depends(require_permission("video.delete"))])
async def delete_video(...):
    pass
```

**优势**:
- ✅ 声明式权限检查
- ✅ 代码更简洁
- ✅ 易于审计和维护
- ✅ 统一错误处理

---

### 2️⃣ **细粒度权限控制** (高优先级) ⭐⭐⭐

#### 问题
当前权限粒度太粗:
- `video.update` 可以修改所有视频字段
- 没有区分敏感操作(如发布/下架)
- 无法限制某些管理员只能管理自己创建的内容

#### 解决方案A: 添加更细粒度的权限

```python
# 新增权限
video.update.basic     # 修改基本信息(标题、描述)
video.update.status    # 修改状态(发布/下架)
video.update.sensitive # 修改敏感信息(分类、标签)
video.delete.own       # 只能删除自己创建的视频
video.delete.all       # 删除所有视频

user.ban.temporary     # 临时封禁
user.ban.permanent     # 永久封禁
```

#### 解决方案B: 资源所有权检查

```python
# backend/app/utils/permissions.py
async def check_resource_ownership(
    resource_type: str,
    resource_id: int,
    current_admin: AdminUser,
    db: AsyncSession
) -> bool:
    """检查管理员是否拥有资源"""
    if current_admin.is_superadmin:
        return True

    # 根据资源类型查询
    if resource_type == "video":
        result = await db.execute(
            select(Video).where(
                Video.id == resource_id,
                Video.created_by == current_admin.id
            )
        )
        return result.scalar_one_or_none() is not None

    return False

# 使用
@router.delete("/videos/{video_id}")
async def delete_video(
    video_id: int,
    current_admin: AdminUser = Depends(require_permission("video.delete")),
    db: AsyncSession = Depends(get_db)
):
    # 检查是否只能删除自己的
    if "video.delete.own" in admin_permissions:
        if not await check_resource_ownership("video", video_id, current_admin, db):
            raise HTTPException(403, "您只能删除自己创建的视频")
```

---

### 3️⃣ **权限缓存优化** (中优先级) ⭐⭐

#### 问题
每次请求都查询数据库加载权限:
- 性能开销大
- 数据库压力高
- 权限很少变化,适合缓存

#### 解决方案: Redis缓存权限

```python
# backend/app/utils/permission_cache.py
import json
from typing import Set, Optional
from app.utils.cache import get_redis

async def get_admin_permissions(admin_id: int) -> Set[str]:
    """获取管理员权限(带缓存)"""
    redis = await get_redis()
    cache_key = f"admin_permissions:{admin_id}"

    # 尝试从缓存获取
    cached = await redis.get(cache_key)
    if cached:
        return set(json.loads(cached))

    # 从数据库加载
    # ... 查询逻辑 ...

    # 缓存30分钟
    await redis.setex(cache_key, 1800, json.dumps(list(permissions)))
    return permissions

async def invalidate_admin_permissions(admin_id: int):
    """清除管理员权限缓存"""
    redis = await get_redis()
    await redis.delete(f"admin_permissions:{admin_id}")

async def invalidate_role_permissions(role_id: int):
    """清除角色相关的所有管理员权限缓存"""
    redis = await get_redis()
    # 查找所有使用该角色的管理员
    # ... 清除缓存 ...
```

---

### 4️⃣ **权限组和模板** (中优先级) ⭐⭐

#### 问题
- 创建角色时手动选择权限繁琐
- 常见角色配置需要重复操作

#### 解决方案: 权限模板系统

```python
# backend/app/utils/role_templates.py
ROLE_TEMPLATES = {
    "content_editor": {
        "name": "内容编辑",
        "description": "负责视频内容的创建和编辑",
        "permissions": [
            "video.create",
            "video.read",
            "video.update.basic",
            "actor.manage",
            "director.manage",
            "tag.manage",
        ]
    },
    "moderator": {
        "name": "审核员",
        "description": "负责内容审核和用户管理",
        "permissions": [
            "video.read",
            "video.review",
            "comment.read",
            "comment.moderate",
            "comment.delete",
            "user.read",
            "user.ban.temporary",
        ]
    },
    "administrator": {
        "name": "管理员",
        "description": "拥有大部分管理权限",
        "permissions": [
            "video.*",  # 所有视频权限
            "user.*",   # 所有用户权限
            "comment.*",
            "system.read",
            "stats.view",
        ]
    }
}

# API端点
@router.get("/role-templates")
async def get_role_templates():
    """获取角色模板列表"""
    return {"templates": ROLE_TEMPLATES}

@router.post("/roles/from-template/{template_name}")
async def create_role_from_template(
    template_name: str,
    role_name: Optional[str] = None
):
    """从模板创建角色"""
    template = ROLE_TEMPLATES.get(template_name)
    if not template:
        raise HTTPException(404, "模板不存在")

    # 解析通配符权限
    # 创建角色
    # ...
```

---

### 5️⃣ **权限审计和日志** (高优先级) ⭐⭐⭐

#### 问题
- 看不到谁修改了权限
- 无法追踪敏感操作
- 缺少权限变更历史

#### 解决方案: 权限变更日志

```python
# backend/app/models/admin.py
class PermissionLog(Base):
    """权限变更日志"""
    __tablename__ = "permission_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    admin_user_id: Mapped[int] = mapped_column(ForeignKey("admin_users.id"))
    action: Mapped[str] = mapped_column(String(50))  # grant, revoke, role_change
    target_type: Mapped[str] = mapped_column(String(50))  # role, admin_user
    target_id: Mapped[int] = mapped_column(Integer)
    permission_codes: Mapped[Optional[str]] = mapped_column(Text)  # JSON
    old_value: Mapped[Optional[str]] = mapped_column(Text)  # JSON
    new_value: Mapped[Optional[str]] = mapped_column(Text)  # JSON
    ip_address: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

# 使用
@router.post("/roles/{role_id}/permissions")
async def update_role_permissions(
    role_id: int,
    permission_ids: List[int],
    current_admin: AdminUser = Depends(get_current_superadmin),
    request: Request = None
):
    # 记录变更前的状态
    old_permissions = get_role_permissions(role_id)

    # 更新权限
    # ...

    # 记录变更日志
    await log_permission_change(
        admin_id=current_admin.id,
        action="role_permissions_updated",
        target_type="role",
        target_id=role_id,
        old_value=old_permissions,
        new_value=new_permissions,
        ip=request.client.host
    )
```

---

### 6️⃣ **前端权限控制** (高优先级) ⭐⭐⭐

#### 问题
前端没有权限验证:
- 所有按钮都显示
- 用户可能点击无权限的功能
- 体验不友好

#### 解决方案A: 权限上下文

```typescript
// admin-frontend/src/contexts/PermissionContext.tsx
import { createContext, useContext, useState, useEffect } from 'react'
import axios from '@/utils/axios'

interface PermissionContextType {
  permissions: string[]
  hasPermission: (code: string) => boolean
  hasAnyPermission: (...codes: string[]) => boolean
  hasAllPermissions: (...codes: string[]) => boolean
  isLoading: boolean
}

const PermissionContext = createContext<PermissionContextType | null>(null)

export const PermissionProvider = ({ children }: { children: React.ReactNode }) => {
  const [permissions, setPermissions] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // 获取当前管理员权限
    axios.get('/api/v1/admin/rbac/my-permissions')
      .then(res => {
        setPermissions(res.data.permissions)
        setIsLoading(false)
      })
      .catch(() => setIsLoading(false))
  }, [])

  const hasPermission = (code: string) => {
    return permissions.includes(code) || permissions.includes('*')
  }

  const hasAnyPermission = (...codes: string[]) => {
    return codes.some(code => hasPermission(code))
  }

  const hasAllPermissions = (...codes: string[]) => {
    return codes.every(code => hasPermission(code))
  }

  return (
    <PermissionContext.Provider value={{
      permissions,
      hasPermission,
      hasAnyPermission,
      hasAllPermissions,
      isLoading
    }}>
      {children}
    </PermissionContext.Provider>
  )
}

export const usePermissions = () => {
  const context = useContext(PermissionContext)
  if (!context) throw new Error('usePermissions must be within PermissionProvider')
  return context
}
```

#### 解决方案B: 权限保护组件

```typescript
// admin-frontend/src/components/PermissionGuard.tsx
import { usePermissions } from '@/contexts/PermissionContext'
import { Tooltip } from 'antd'

interface PermissionGuardProps {
  permission: string | string[]
  children: React.ReactNode
  fallback?: React.ReactNode
  hideIfNoPermission?: boolean
  showTooltip?: boolean
}

export const PermissionGuard = ({
  permission,
  children,
  fallback = null,
  hideIfNoPermission = false,
  showTooltip = true
}: PermissionGuardProps) => {
  const { hasPermission, hasAnyPermission } = usePermissions()

  const hasAccess = Array.isArray(permission)
    ? hasAnyPermission(...permission)
    : hasPermission(permission)

  if (!hasAccess) {
    if (hideIfNoPermission) return null

    if (showTooltip) {
      return (
        <Tooltip title="您没有此操作的权限">
          <span style={{ cursor: 'not-allowed', opacity: 0.5 }}>
            {children}
          </span>
        </Tooltip>
      )
    }

    return <>{fallback}</>
  }

  return <>{children}</>
}

// 使用
<PermissionGuard permission="video.delete">
  <Button danger icon={<DeleteOutlined />} onClick={handleDelete}>
    删除
  </Button>
</PermissionGuard>

<PermissionGuard permission={["video.update", "video.delete"]} hideIfNoPermission>
  <Space>
    <Button onClick={handleEdit}>编辑</Button>
    <Button danger onClick={handleDelete}>删除</Button>
  </Space>
</PermissionGuard>
```

---

### 7️⃣ **权限冲突检测** (低优先级) ⭐

#### 问题
某些权限可能冲突:
- 同时拥有"只读"和"编辑"权限
- 权限过多可能导致安全风险

#### 解决方案: 权限规则引擎

```python
# backend/app/utils/permission_rules.py
PERMISSION_RULES = {
    "conflicts": [
        # 互斥权限
        ("video.read_only", "video.update"),
        ("user.view_only", "user.delete"),
    ],
    "dependencies": [
        # 权限依赖(拥有A必须拥有B)
        ("video.update", "video.read"),
        ("video.delete", "video.read"),
        ("user.delete", "user.read"),
    ],
    "recommendations": {
        # 权限推荐
        "video.create": ["video.read", "video.update.basic"],
        "comment.moderate": ["comment.read", "comment.delete"],
    }
}

def validate_permissions(permission_codes: List[str]) -> dict:
    """验证权限组合"""
    conflicts = []
    missing_dependencies = []
    recommendations = []

    perm_set = set(permission_codes)

    # 检查冲突
    for p1, p2 in PERMISSION_RULES["conflicts"]:
        if p1 in perm_set and p2 in perm_set:
            conflicts.append(f"{p1} 与 {p2} 冲突")

    # 检查依赖
    for dependent, required in PERMISSION_RULES["dependencies"]:
        if dependent in perm_set and required not in perm_set:
            missing_dependencies.append(f"{dependent} 需要 {required}")

    # 生成推荐
    for perm in perm_set:
        if perm in PERMISSION_RULES["recommendations"]:
            recommended = PERMISSION_RULES["recommendations"][perm]
            missing_recommended = set(recommended) - perm_set
            if missing_recommended:
                recommendations.append({
                    "for": perm,
                    "recommended": list(missing_recommended)
                })

    return {
        "valid": len(conflicts) == 0 and len(missing_dependencies) == 0,
        "conflicts": conflicts,
        "missing_dependencies": missing_dependencies,
        "recommendations": recommendations
    }
```

---

### 8️⃣ **批量权限操作** (中优先级) ⭐⭐

#### 问题
- 无法批量分配权限给多个角色
- 无法批量移除某个权限
- 权限迁移困难

#### 解决方案: 批量操作API

```python
@router.post("/permissions/bulk-assign")
async def bulk_assign_permissions(
    role_ids: List[int],
    permission_ids: List[int],
    action: str = "add",  # add, remove, replace
    current_admin: AdminUser = Depends(get_current_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """批量分配/移除权限"""
    for role_id in role_ids:
        if action == "add":
            # 添加权限到角色
            pass
        elif action == "remove":
            # 从角色移除权限
            pass
        elif action == "replace":
            # 替换角色的所有权限
            pass

    return {"success": True, "affected_roles": len(role_ids)}
```

---

### 9️⃣ **权限分析和报告** (低优先级) ⭐

#### 功能
- 权限使用统计
- 最常用/最少用权限
- 权限覆盖率分析
- 角色权限对比

```python
@router.get("/permissions/analytics")
async def get_permission_analytics(db: AsyncSession = Depends(get_db)):
    """权限分析报告"""
    # 统计每个权限被多少个角色使用
    # 统计每个角色有多少管理员
    # 找出未被使用的权限
    # 找出权限过多的角色
    pass
```

---

### 🔟 **动态权限和API权限映射** (高优先级) ⭐⭐⭐

#### 问题
权限和API端点是分离的:
- 需要手动维护权限-API映射
- 容易遗漏权限检查
- 难以审计

#### 解决方案: 自动权限映射

```python
# backend/app/utils/api_permissions.py
API_PERMISSION_MAP = {
    "/api/v1/admin/videos POST": "video.create",
    "/api/v1/admin/videos/{id} PUT": "video.update",
    "/api/v1/admin/videos/{id} DELETE": "video.delete",
    "/api/v1/admin/videos GET": "video.read",
    # ... 自动生成
}

# 中间件自动检查
class APIPermissionMiddleware:
    async def __call__(self, request: Request, call_next):
        if request.url.path.startswith("/api/v1/admin"):
            # 根据路径和方法查找所需权限
            required_perm = get_required_permission(request.method, request.url.path)
            if required_perm:
                # 自动验证
                await check_admin_permission(request, required_perm)

        return await call_next(request)
```

---

## 📋 优化优先级总结

### 🔥 立即实施 (高优先级)
1. **权限验证装饰器** - 简化权限检查代码
2. **前端权限控制** - 改善用户体验
3. **权限审计日志** - 安全合规必需
4. **动态权限映射** - 自动化权限管理

### 🚀 尽快实施 (中优先级)
5. **权限缓存** - 性能优化
6. **权限模板** - 提升效率
7. **细粒度权限** - 更精确的控制
8. **批量操作** - 管理便利

### 💡 可选实施 (低优先级)
9. **权限冲突检测** - 智能辅助
10. **权限分析报告** - 数据洞察

---

## 🎯 推荐实施顺序

### 第一阶段 (2-3小时)
1. 创建权限验证装饰器
2. 添加前端权限上下文
3. 实现PermissionGuard组件

### 第二阶段 (2-3小时)
4. 添加权限缓存
5. 实现权限审计日志
6. 创建角色模板

### 第三阶段 (按需)
7. 细粒度权限扩展
8. 批量操作API
9. 其他增强功能

---

想要我立即实施哪些优化？我推荐从**第一阶段**开始！
