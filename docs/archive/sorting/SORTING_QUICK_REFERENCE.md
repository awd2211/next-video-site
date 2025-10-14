# 后端API排序功能快速参考

## 更新的API端点

| 文件 | 端点 | 默认排序 | 默认顺序 | 支持的排序字段 |
|------|------|----------|----------|----------------|
| **users.py** | `GET /api/v1/admin/users` | `created_at` | `desc` | id, username, email, full_name, created_at, updated_at, last_login_at, is_active, is_vip, is_verified |
| **banners.py** | `GET /api/v1/admin/banners` | `sort_order` | `desc` | id, title, sort_order, status, created_at, updated_at, start_date, end_date |
| **announcements.py** | `GET /api/v1/admin/announcements` | `created_at` | `desc` | id, title, type, is_active, is_pinned, created_at, updated_at, start_date, end_date |
| **series.py** | `GET /api/v1/admin/series` | `created_at` | `desc` | id, title, type, status, total_episodes, total_views, total_favorites, display_order, is_featured, created_at, updated_at |
| **actors.py** | `GET /api/v1/admin/actors` | `name` | `asc` | id, name, nationality, birth_date, created_at, updated_at |
| **directors.py** | `GET /api/v1/admin/directors` | `name` | `asc` | id, name, nationality, birth_date, created_at, updated_at |

## 查询参数

所有API都支持以下查询参数：

| 参数 | 类型 | 必填 | 默认值 | 描述 | 验证规则 |
|------|------|------|--------|------|----------|
| `sort_by` | string | 否 | 见上表 | 排序字段 | 必须在允许的字段列表中 |
| `sort_order` | string | 否 | 见上表 | 排序顺序 | 只能是 "asc" 或 "desc" |

## 前端字段映射

前端可以使用 camelCase，后端会自动转换为 snake_case：

| 前端字段 (camelCase) | 后端字段 (snake_case) |
|---------------------|---------------------|
| createdAt | created_at |
| updatedAt | updated_at |
| lastLogin / lastLoginAt | last_login_at |
| viewCount | view_count |
| averageRating | average_rating |
| sortOrder | sort_order |
| displayOrder | display_order |
| isActive | is_active |
| isVip | is_vip |
| isPinned | is_pinned |
| isFeatured | is_featured |
| birthDate | birth_date |
| startDate | start_date |
| endDate | end_date |
| totalEpisodes | total_episodes |
| totalViews | total_views |
| totalFavorites | total_favorites |

## API调用示例

### 1. 用户管理 (Users)

```bash
# 按创建时间降序（默认）
GET /api/v1/admin/users?page=1&page_size=20

# 按用户名升序
GET /api/v1/admin/users?page=1&page_size=20&sort_by=username&sort_order=asc

# 按最后登录时间降序
GET /api/v1/admin/users?page=1&page_size=20&sort_by=lastLoginAt&sort_order=desc

# 结合过滤器
GET /api/v1/admin/users?page=1&page_size=20&status=active&sort_by=created_at&sort_order=desc
```

### 2. 横幅管理 (Banners)

```bash
# 按排序值降序（默认）
GET /api/v1/admin/banners?page=1&page_size=20

# 按标题升序
GET /api/v1/admin/banners?page=1&page_size=20&sort_by=title&sort_order=asc

# 按创建时间降序，仅显示激活的横幅
GET /api/v1/admin/banners?page=1&page_size=20&status=active&sort_by=createdAt&sort_order=desc
```

### 3. 公告管理 (Announcements)

```bash
# 按创建时间降序（默认）
GET /api/v1/admin/announcements?page=1&page_size=20

# 按置顶状态降序（置顶的在前）
GET /api/v1/admin/announcements?page=1&page_size=20&sort_by=isPinned&sort_order=desc

# 按标题升序，仅显示激活的公告
GET /api/v1/admin/announcements?page=1&page_size=20&is_active=true&sort_by=title&sort_order=asc
```

### 4. 剧集管理 (Series)

```bash
# 按创建时间降序（默认）
GET /api/v1/admin/series?page=1&page_size=20

# 按总播放量降序
GET /api/v1/admin/series?page=1&page_size=20&sort_by=totalViews&sort_order=desc

# 按剧集数升序，仅显示已发布的
GET /api/v1/admin/series?page=1&page_size=20&status=published&sort_by=total_episodes&sort_order=asc

# 按推荐状态降序（推荐的在前）
GET /api/v1/admin/series?page=1&page_size=20&sort_by=is_featured&sort_order=desc
```

### 5. 演员管理 (Actors)

```bash
# 按姓名升序（默认）
GET /api/v1/admin/actors?page=1&page_size=20

# 按出生日期降序（最年轻的在前）
GET /api/v1/admin/actors?page=1&page_size=20&sort_by=birthDate&sort_order=desc

# 按创建时间降序，搜索包含"Tom"的演员
GET /api/v1/admin/actors?page=1&page_size=20&search=Tom&sort_by=created_at&sort_order=desc
```

### 6. 导演管理 (Directors)

```bash
# 按姓名升序（默认）
GET /api/v1/admin/directors?page=1&page_size=20

# 按国籍升序
GET /api/v1/admin/directors?page=1&page_size=20&sort_by=nationality&sort_order=asc

# 按创建时间降序，搜索包含"Steven"的导演
GET /api/v1/admin/directors?page=1&page_size=20&search=Steven&sort_by=createdAt&sort_order=desc
```

## 错误处理

### 无效的排序字段

**请求：**
```bash
GET /api/v1/admin/users?sort_by=invalid_field
```

**响应：** `400 Bad Request`
```json
{
  "detail": "Sorting by 'invalid_field' is not allowed. Allowed fields: id, username, email, full_name, created_at, updated_at, last_login_at, is_active, is_vip, is_verified"
}
```

### 无效的排序顺序

**请求：**
```bash
GET /api/v1/admin/users?sort_order=invalid
```

**响应：** `422 Unprocessable Entity`
```json
{
  "detail": [
    {
      "loc": ["query", "sort_order"],
      "msg": "string does not match regex \"^(asc|desc)$\"",
      "type": "value_error.str.regex"
    }
  ]
}
```

## 测试建议

### 1. 基本排序测试
```bash
# 测试默认排序
curl -X GET "http://localhost:8000/api/v1/admin/users?page=1&page_size=5"

# 测试升序排序
curl -X GET "http://localhost:8000/api/v1/admin/users?page=1&page_size=5&sort_by=username&sort_order=asc"

# 测试降序排序
curl -X GET "http://localhost:8000/api/v1/admin/users?page=1&page_size=5&sort_by=created_at&sort_order=desc"
```

### 2. 字段名转换测试
```bash
# 测试 camelCase 转换
curl -X GET "http://localhost:8000/api/v1/admin/users?sort_by=createdAt&sort_order=desc"
curl -X GET "http://localhost:8000/api/v1/admin/users?sort_by=lastLoginAt&sort_order=desc"
```

### 3. 错误处理测试
```bash
# 测试无效字段
curl -X GET "http://localhost:8000/api/v1/admin/users?sort_by=invalid_field"

# 测试无效顺序
curl -X GET "http://localhost:8000/api/v1/admin/users?sort_order=invalid"
```

### 4. 结合过滤器测试
```bash
# 用户API - 搜索 + 排序
curl -X GET "http://localhost:8000/api/v1/admin/users?search=john&sort_by=created_at&sort_order=desc"

# 横幅API - 状态过滤 + 排序
curl -X GET "http://localhost:8000/api/v1/admin/banners?status=active&sort_by=sort_order&sort_order=desc"

# 剧集API - 类型过滤 + 排序
curl -X GET "http://localhost:8000/api/v1/admin/series?type=movie&sort_by=total_views&sort_order=desc"
```

## 前端集成示例 (React)

```typescript
// 定义排序参数类型
interface SortParams {
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// API调用函数
async function fetchUsers(page: number, pageSize: number, sort?: SortParams) {
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString(),
  });
  
  if (sort?.sortBy) {
    params.append('sort_by', sort.sortBy);
  }
  if (sort?.sortOrder) {
    params.append('sort_order', sort.sortOrder);
  }
  
  const response = await fetch(`/api/v1/admin/users?${params}`);
  return response.json();
}

// 使用示例
const users = await fetchUsers(1, 20, { 
  sortBy: 'createdAt',  // 自动转换为 created_at
  sortOrder: 'desc' 
});
```

## 注意事项

1. **字段名格式**: 后端同时支持 snake_case 和 camelCase，但建议前端统一使用 camelCase
2. **字段白名单**: 每个API都有严格的字段白名单，只有列出的字段可以用于排序
3. **默认行为**: 如果不指定排序参数，使用合理的默认值（见上面的表格）
4. **参数验证**: sort_order 参数使用正则表达式验证，必须是 "asc" 或 "desc"
5. **错误响应**: 无效参数会返回清晰的错误信息，便于调试

## Swagger UI

所有排序参数都会自动出现在 Swagger UI 文档中：

访问 `http://localhost:8000/api/docs` 查看完整的API文档。
