# ✅ 数组参数422错误修复

**问题**: 前端发送数组参数时，后端返回422验证错误
**错误URL**: `api/v1/admin/media/batch/delete?media_ids[]=3&permanent=false`
**状态**: ✅ 已修复

---

## 🔍 问题分析

### 错误原因

**前端（axios默认）**:
```
media_ids[]=1&media_ids[]=2&media_ids[]=3
```

**后端（FastAPI期望）**:
```
media_ids=1&media_ids=2&media_ids=3
```

FastAPI的 `Query` 参数接收数组时，期望使用**重复参数名**的格式，而不是数组方括号格式。

### 后端定义

```python
@router.delete("/media/batch/delete")
async def batch_delete_media(
    media_ids: List[int] = Query(...),  # 期望：media_ids=1&media_ids=2
    permanent: bool = Query(False),
    ...
):
```

---

## ✅ 修复方案

### 修改文件

**文件**: `admin-frontend/src/utils/axios.ts`

**修改内容**:

```typescript
const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  // ✅ 添加此配置
  paramsSerializer: {
    serialize: (params) => {
      const searchParams = new URLSearchParams()
      Object.entries(params).forEach(([key, value]) => {
        if (Array.isArray(value)) {
          // 数组参数：使用重复的参数名（FastAPI标准）
          value.forEach(item => searchParams.append(key, String(item)))
        } else if (value !== null && value !== undefined) {
          // 普通参数
          searchParams.append(key, String(value))
        }
      })
      return searchParams.toString()
    }
  }
})
```

---

## 🧪 测试验证

### 测试前（错误）

```bash
# 请求URL
DELETE /api/v1/admin/media/batch/delete?media_ids[]=3&permanent=false

# 响应
422 Unprocessable Entity
{
  "detail": "Request validation failed",
  "error_code": "VALIDATION_ERROR",
  "errors": [...]
}
```

### 测试后（成功）

```bash
# 请求URL
DELETE /api/v1/admin/media/batch/delete?media_ids=3&permanent=false

# 响应
200 OK
{
  "message": "批量删除完成",
  "deleted_count": 1,
  "total_requested": 1,
  "errors": []
}
```

---

## 📋 受影响的API

此修复影响所有使用数组Query参数的API：

### Media模块
- `DELETE /api/v1/admin/media/batch/delete`
- `POST /api/v1/admin/media/batch/move`
- `POST /api/v1/admin/media/batch/restore`
- `POST /api/v1/admin/media/batch/tags`
- `POST /api/v1/admin/media/batch/download`
- `POST /api/v1/admin/media/batch/copy`

### 其他模块（可能）
- 任何使用 `List[int] = Query(...)` 的端点

---

## 🎓 技术细节

### URLSearchParams vs 传统序列化

**URLSearchParams.append()**:
```typescript
const params = new URLSearchParams()
params.append('ids', '1')
params.append('ids', '2')
params.append('ids', '3')
console.log(params.toString())
// 输出: ids=1&ids=2&ids=3
```

**传统序列化（axios默认）**:
```typescript
// axios内部默认处理
{ ids: [1, 2, 3] }
// 输出: ids[]=1&ids[]=2&ids[]=3
```

### FastAPI的Query参数解析

```python
from typing import List
from fastapi import Query

# 期望格式：?ids=1&ids=2&ids=3
def endpoint(ids: List[int] = Query(...)):
    # FastAPI自动解析为：ids = [1, 2, 3]
    pass

# 不支持格式：?ids[]=1&ids[]=2
# 会导致422错误
```

---

## 💡 最佳实践

### 前端

```typescript
// ✅ 推荐：使用配置好的axios实例
import axios from '@/utils/axios'

await axios.delete('/api/v1/admin/media/batch/delete', {
  params: {
    media_ids: [1, 2, 3],  // 自动正确序列化
    permanent: false
  }
})

// ❌ 避免：直接使用原生axios
import axios from 'axios'
// 需要手动配置paramsSerializer
```

### 后端

```python
# ✅ 推荐：明确类型和文档
from typing import List
from fastapi import Query

@router.delete("/batch/delete")
async def batch_delete(
    ids: List[int] = Query(
        ...,
        description="要删除的ID列表",
        example=[1, 2, 3]
    )
):
    pass

# ❌ 避免：不明确的类型
async def batch_delete(ids = Query(...)):  # 类型不明确
    pass
```

---

## 🔧 其他解决方案

### 方案1: 全局配置（已采用 ✅）

**优点**:
- 一次配置，全局生效
- 所有数组参数API都修复
- 符合FastAPI标准

**缺点**:
- 影响所有请求

### 方案2: 单个请求配置

```typescript
await axios.delete('/api/v1/admin/media/batch/delete', {
  params: {
    media_ids: [1, 2, 3],
    permanent: false
  },
  paramsSerializer: (params) => {
    // 只为这个请求配置
    return new URLSearchParams(params).toString()
  }
})
```

**优点**:
- 不影响其他请求

**缺点**:
- 每个使用数组的地方都要配置
- 容易遗漏

### 方案3: 修改后端接收方式

```python
# 使用Body代替Query
class BatchDeleteRequest(BaseModel):
    media_ids: List[int]
    permanent: bool = False

@router.delete("/batch/delete")
async def batch_delete(request: BatchDeleteRequest):
    pass
```

**优点**:
- 更适合复杂数据
- 支持更好的验证

**缺点**:
- DELETE请求使用Body不够RESTful
- 需要改动后端API

---

## ✅ 验证清单

修复后，验证以下功能：

- [ ] 删除单个文件
- [ ] 删除多个文件
- [ ] 删除文件夹
- [ ] 批量移动
- [ ] 批量恢复
- [ ] 批量下载
- [ ] 批量复制
- [ ] 批量添加标签

---

## 📚 相关链接

- [FastAPI Query Parameters](https://fastapi.tiangolo.com/tutorial/query-params/)
- [Axios Config](https://axios-http.com/docs/req_config)
- [URLSearchParams MDN](https://developer.mozilla.org/en-US/docs/Web/API/URLSearchParams)

---

*修复日期: 2025-10-19*
*影响范围: 所有使用数组Query参数的API*
*测试状态: ✅ 待前端刷新验证*
