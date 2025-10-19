# 🔍 Request Validation Failed - 诊断指南

**问题**: 遇到 "Request validation failed" 错误
**状态**: ✅ 服务端代码正常，没有语法错误
**日志**: ✅ 当前日志中没有验证错误

---

## 📊 当前状态

### ✅ 已检查项目

1. **语法检查** - 通过 ✅
   ```bash
   python -c "from app.main import app; print('App loaded successfully')"
   # 输出: ✅ App loaded successfully
   ```

2. **验证错误日志** - 无错误 ✅
   ```bash
   python scripts/check_validation_errors.py
   # 输出: ✅ No validation errors found!
   ```

3. **应用启动** - 正常 ✅

---

## 🔍 排查步骤

### Step 1: 确定具体的错误端点

如果你在前端或API调用中遇到 "Request validation failed"，首先需要知道：

#### 方法A: 查看浏览器开发者工具

1. 打开 Chrome DevTools (F12)
2. 切换到 **Network** 标签
3. 重现错误
4. 找到**红色**的请求（状态码422）
5. 点击该请求，查看：
   - **Request URL**: 具体的API端点
   - **Request Payload**: 发送的数据
   - **Response**: 错误详情

**示例错误响应**:
```json
{
  "detail": "Request validation failed",
  "error_code": "VALIDATION_ERROR",
  "errors": [
    {
      "field": "title",
      "message": "field required",
      "type": "value_error.missing"
    },
    {
      "field": "media_type",
      "message": "value is not a valid enumeration member; permitted: 'image', 'video'",
      "type": "type_error.enum"
    }
  ],
  "request_id": "abc-123-def"
}
```

#### 方法B: 检查后端日志

```bash
cd /home/eric/video/backend

# 实时查看日志
tail -f uvicorn.log | grep -i "validation"

# 或者使用诊断工具
python scripts/check_validation_errors.py --recent 100
```

---

### Step 2: 常见验证错误类型

#### 🔴 错误类型1: 缺少必需字段

**错误**:
```json
{
  "field": "title",
  "message": "field required",
  "type": "value_error.missing"
}
```

**原因**: 请求中缺少必需的字段

**解决方案**:
```typescript
// ❌ 错误 - 缺少 title
const response = await axios.post('/api/v1/admin/media/upload', {
  description: "My image"
})

// ✅ 正确 - 包含所有必需字段
const response = await axios.post('/api/v1/admin/media/upload', {
  title: "My Image",  // 必需
  description: "My image"
})
```

---

#### 🔴 错误类型2: 数据类型不匹配

**错误**:
```json
{
  "field": "page_size",
  "message": "value is not a valid integer",
  "type": "type_error.integer"
}
```

**原因**: 发送的数据类型与后端期望的不同

**解决方案**:
```typescript
// ❌ 错误 - page_size 是字符串
const response = await axios.get('/api/v1/admin/media', {
  params: { page: 1, page_size: "20" }  // 字符串
})

// ✅ 正确 - page_size 是数字
const response = await axios.get('/api/v1/admin/media', {
  params: { page: 1, page_size: 20 }  // 数字
})
```

---

#### 🔴 错误类型3: 枚举值无效

**错误**:
```json
{
  "field": "media_type",
  "message": "value is not a valid enumeration member; permitted: 'image', 'video'",
  "type": "type_error.enum"
}
```

**原因**: 枚举字段的值不在允许的范围内

**解决方案**:
```typescript
// ❌ 错误 - 'picture' 不是有效值
const response = await axios.get('/api/v1/admin/media', {
  params: { media_type: "picture" }
})

// ✅ 正确 - 使用允许的值
const response = await axios.get('/api/v1/admin/media', {
  params: { media_type: "image" }  // 或 "video"
})
```

---

#### 🔴 错误类型4: Query参数格式错误

**错误**:
```json
{
  "field": "media_ids",
  "message": "value is not a valid list",
  "type": "type_error.list"
}
```

**原因**: Query参数需要数组但发送的是字符串

**解决方案**:
```typescript
// ❌ 错误 - media_ids 是字符串
await axios.post('/api/v1/admin/media/batch/delete', null, {
  params: { media_ids: "1,2,3" }
})

// ✅ 正确 - media_ids 是数组
await axios.post('/api/v1/admin/media/batch/delete', null, {
  params: { media_ids: [1, 2, 3] }
})
```

---

#### 🔴 错误类型5: Body vs Query 混淆

**错误**: 参数应该在body中但放在了query中（或相反）

**解决方案**:
```python
# 后端定义 - 参数在Query中
@router.post("/media/folders/create")
async def create_folder(
    title: str = Query(...),  # Query参数
    parent_id: Optional[int] = Query(None),
    ...
):
```

```typescript
// ✅ 正确 - 使用Query参数
await axios.post('/api/v1/admin/media/folders/create', null, {
  params: { title: "My Folder", parent_id: 1 }  // params = Query
})

// ❌ 错误 - 不要放在body中
await axios.post('/api/v1/admin/media/folders/create', {
  title: "My Folder"  // 这是body，但后端期望Query
})
```

---

### Step 3: 使用诊断工具

#### 🔧 工具1: 验证错误检查器

```bash
cd /home/eric/video/backend

# 检查所有验证错误
python scripts/check_validation_errors.py

# 检查特定端点
python scripts/check_validation_errors.py --endpoint /api/v1/admin/media

# 检查最近100行日志
python scripts/check_validation_errors.py --recent 100
```

#### 🔧 工具2: API测试

```bash
# 测试端点是否正常工作
python scripts/performance_test.py --endpoint /api/v1/admin/media

# 使用curl测试
curl -X GET "http://localhost:8000/api/v1/admin/media?page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 🔧 工具3: 查看API文档

```bash
# 启动后端
uvicorn app.main:app --reload

# 访问Swagger文档
open http://localhost:8000/api/docs

# 在文档中测试API，查看：
# - 必需参数
# - 参数类型
# - 示例请求
```

---

## 🎯 快速修复清单

### 前端检查

- [ ] 确认发送的字段名称正确（无拼写错误）
- [ ] 确认所有必需字段都已发送
- [ ] 确认数据类型正确（number vs string）
- [ ] 确认枚举值在允许范围内
- [ ] 确认参数位置正确（body vs query vs path）
- [ ] 检查数组格式是否正确

### 后端检查

- [ ] 服务是否正常启动
- [ ] 是否有语法错误
- [ ] Schema定义是否正确
- [ ] 是否有缺少的导入

### 网络检查

- [ ] 前端和后端端口是否正确
- [ ] CORS是否配置正确
- [ ] 代理设置是否正确（如果使用）

---

## 📚 参考文档

### API Schema 定义位置

```
backend/app/schemas/
├── media.py         # Media相关Schema
├── video.py         # Video相关Schema
├── user.py          # User相关Schema
└── ...
```

### 常见Schema示例

**MediaUploadResponse** (`app/schemas/media.py`):
```python
class MediaUploadResponse(BaseModel):
    id: int
    title: str
    filename: str
    file_path: str
    media_type: MediaType  # Enum: "image" or "video"
    status: MediaStatus    # Enum: "uploading", "processing", "ready", "failed"
    url: str | None
    ...
```

---

## 💡 调试技巧

### 1. 启用DEBUG模式

```bash
# backend/.env
DEBUG=True  # 获取详细的错误信息
```

### 2. 添加日志

```python
# 在后端代码中添加
logger.info(f"Received data: {data}")
logger.info(f"Validation errors: {exc.errors()}")
```

### 3. 使用Postman/Insomnia测试

1. 直接测试后端API
2. 对比前端和Postman的请求差异
3. 检查请求头、参数、body是否一致

---

## 🚨 紧急处理

如果生产环境遇到大量验证错误：

```bash
# 1. 检查最近的变更
git log --since="1 day ago" --oneline

# 2. 回滚到上一个稳定版本
git checkout <stable_commit>

# 3. 重启服务
systemctl restart videosite-backend  # 或你的服务管理器

# 4. 检查错误日志
tail -f /var/log/videosite/uvicorn.log | grep validation
```

---

## 🎓 学习资源

- [FastAPI Validation](https://fastapi.tiangolo.com/tutorial/body/)
- [Pydantic Models](https://docs.pydantic.dev/latest/)
- [HTTP Status Codes](https://httpstatuses.com/422)

---

## ✅ 检查完成

**总结**:
- ✅ 服务端代码正常
- ✅ 没有发现验证错误
- ✅ 提供了完整的诊断工具和方法

**下一步**:
1. 如果仍然遇到错误，请按照上述步骤排查
2. 记录具体的错误端点和错误信息
3. 使用提供的诊断工具定位问题

---

*创建日期: 2025-10-19*
*工具位置: `scripts/check_validation_errors.py`*
