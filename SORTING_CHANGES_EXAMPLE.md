# 排序功能改动示例

## 以 `users.py` 为例

### 改动前（Before）

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, desc, or_
# ... 其他导入 ...

@router.get("")
async def admin_list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by username or email"),
    status: Optional[str] = Query(None, description="Filter by status: active, banned, all"),
    is_vip: Optional[bool] = Query(None, description="Filter by VIP status"),
    sort_by: Optional[str] = Query("created_at", description="Sort field: created_at, last_login_at, username"),
    sort_order: Optional[str] = Query("desc", description="Sort order: asc, desc"),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Get all users with search and filters"""
    query = select(User)
    
    # ... 过滤逻辑 ...
    
    # Count total with filters
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    # Apply sorting - 硬编码逻辑
    if sort_by == "username":
        sort_column = User.username
    elif sort_by == "last_login_at":
        sort_column = User.last_login_at
    else:  # default to created_at
        sort_column = User.created_at
    
    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return {"total": total, "page": page, "page_size": page_size, "items": users}
```

### 改动后（After）

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, desc, or_
# ... 其他导入 ...
from app.utils.sorting import apply_sorting, normalize_sort_field  # 新增导入

@router.get("")
async def admin_list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by username or email"),
    status: Optional[str] = Query(None, description="Filter by status: active, banned, all"),
    is_vip: Optional[bool] = Query(None, description="Filter by VIP status"),
    sort_by: Optional[str] = Query(
        "created_at",
        description="排序字段: id, username, email, created_at, last_login_at, is_active, is_vip"  # 更详细的说明
    ),
    sort_order: Optional[str] = Query(
        "desc",
        regex="^(asc|desc)$",  # 新增正则验证
        description="排序顺序: asc (升序) 或 desc (降序)"
    ),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Get all users with search and filters"""
    query = select(User)
    
    # ... 过滤逻辑（不变）...
    
    # Count total with filters
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    # Apply sorting - 使用统一工具
    sort_field = normalize_sort_field(sort_by)  # 支持 camelCase 转换
    allowed_sort_fields = [  # 白名单验证
        "id",
        "username",
        "email",
        "full_name",
        "created_at",
        "updated_at",
        "last_login_at",
        "is_active",
        "is_vip",
        "is_verified",
    ]
    query = apply_sorting(
        query, User, sort_field, sort_order, 
        default_sort="created_at", 
        allowed_fields=allowed_sort_fields
    )
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return {"total": total, "page": page, "page_size": page_size, "items": users}
```

## 关键改进点

### 1. 代码重用
**Before**: 每个API都需要写 10+ 行重复的排序逻辑
```python
if sort_by == "username":
    sort_column = User.username
elif sort_by == "last_login_at":
    sort_column = User.last_login_at
else:
    sort_column = User.created_at

if sort_order == "asc":
    query = query.order_by(sort_column.asc())
else:
    query = query.order_by(sort_column.desc())
```

**After**: 统一调用 3 行代码
```python
sort_field = normalize_sort_field(sort_by)
allowed_sort_fields = [...]
query = apply_sorting(query, User, sort_field, sort_order, ...)
```

### 2. 字段扩展性
**Before**: 只支持 3 个字段（username, last_login_at, created_at）
**After**: 支持 10 个字段，轻松添加更多

### 3. 前端兼容性
**Before**: 只能使用 snake_case（created_at）
**After**: 支持 camelCase（createdAt）自动转换

### 4. 安全性
**Before**: 没有字段白名单，潜在的SQL注入风险
**After**: 严格的字段白名单验证

### 5. 参数验证
**Before**: sort_order 可以是任意字符串
**After**: 使用正则表达式验证，只能是 "asc" 或 "desc"

### 6. 错误处理
**Before**: 无效字段时默认使用 created_at，用户不知道出错
**After**: 返回清晰的 400 错误信息，指出哪个字段不可用

## 使用示例

### 1. 默认排序（按创建时间降序）
```bash
GET /api/v1/admin/users?page=1&page_size=20
```

### 2. 按用户名升序排序
```bash
GET /api/v1/admin/users?page=1&page_size=20&sort_by=username&sort_order=asc
```

### 3. 按最后登录时间降序排序
```bash
GET /api/v1/admin/users?page=1&page_size=20&sort_by=last_login_at&sort_order=desc
```

### 4. 前端 camelCase 格式（自动转换）
```bash
GET /api/v1/admin/users?page=1&page_size=20&sort_by=lastLoginAt&sort_order=desc
```

### 5. 结合搜索和过滤
```bash
GET /api/v1/admin/users?page=1&page_size=20&search=john&status=active&is_vip=true&sort_by=created_at&sort_order=desc
```

### 6. 错误示例（返回 400 错误）
```bash
# 无效字段
GET /api/v1/admin/users?page=1&page_size=20&sort_by=invalid_field

# 无效顺序
GET /api/v1/admin/users?page=1&page_size=20&sort_order=invalid_order
```

## 总结

通过引入统一的排序工具函数，实现了：
- ✅ 代码重用和一致性
- ✅ 更好的扩展性
- ✅ 前端友好（camelCase 支持）
- ✅ 安全性（字段白名单）
- ✅ 更好的错误处理
- ✅ 易于维护和测试

所有6个API都遵循同样的模式，确保了代码库的一致性。
