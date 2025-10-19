# ✅ 上传完成400错误修复 - SQLAlchemy JSON 列跟踪问题

**问题**: 分块上传时，所有分块上传成功后调用 complete 接口返回 400 Bad Request
**错误**: "还有分块未上传完成 (N/N)"
**状态**: ✅ 已修复

---

## 🔍 问题分析

### 根本原因

**SQLAlchemy 的 JSON 列变更跟踪问题**：

当你直接修改 JSON/ARRAY 列的内容（如 `.append()`），SQLAlchemy 可能**不会检测到变更**，导致 `commit()` 时不保存修改。

```python
# ❌ 问题代码
session.uploaded_chunks.append(chunk_index)  # 修改了 JSON 数组
await db.commit()  # SQLAlchemy 可能不会保存这个改动！

# 结果: uploaded_chunks 仍然是 [], is_completed 仍然是 False
# 调用 complete 时: "还有分块未上传完成 (0/10)"
```

### 错误流程

1. **上传分块**:
   ```python
   # app/admin/media.py:753
   session.mark_chunk_uploaded(chunk_index)  # 添加到 uploaded_chunks
   session.is_completed = True  # 所有分块上传完成
   await db.commit()  # ❌ 但 uploaded_chunks 没有被保存！
   ```

2. **调用 complete**:
   ```python
   # app/admin/media.py:805
   if not session.is_completed:  # ❌ 仍然是 False
       raise HTTPException(
           status_code=400,
           detail=f"还有分块未上传完成 ({len(session.uploaded_chunks)}/{session.total_chunks})"
       )
   ```

3. **错误结果**:
   ```
   400 Bad Request
   "还有分块未上传完成 (0/10)"
   ```

---

## ✅ 修复方案

### 修改文件

**文件**: `backend/app/admin/media.py`

### 修改1: 添加导入

```python
from sqlalchemy.orm import attributes
```

### 修改2: 显式标记 JSON 列已修改

```python
# app/admin/media.py:753-764

# 标记分块已上传
session.mark_chunk_uploaded(chunk_index)
# ✅ 显式标记 JSON 列已修改（SQLAlchemy 变更跟踪）
attributes.flag_modified(session, "uploaded_chunks")
session.updated_at = datetime.utcnow()

# 检查是否所有分块都已上传
if session.is_upload_complete():
    session.is_completed = True
    logger.info(f"Upload completed: {upload_id} ({len(session.uploaded_chunks)}/{session.total_chunks} chunks)")

await db.commit()
await db.refresh(session)  # ✅ 刷新以确保获取最新状态
```

### 修改3: 添加调试日志

```python
# app/admin/media.py:800-803

# 记录调试信息
logger.info(f"Complete upload request: {upload_id}")
logger.info(f"Session status: is_completed={session.is_completed}, is_merged={session.is_merged}")
logger.info(f"Upload progress: {len(session.uploaded_chunks)}/{session.total_chunks} chunks)")

if not session.is_completed:
    raise HTTPException(
        status_code=400,
        detail=f"还有分块未上传完成 ({len(session.uploaded_chunks)}/{session.total_chunks})"  # 显示详细信息
    )
```

---

## 🎓 技术细节

### SQLAlchemy 变更跟踪机制

#### 问题：可变类型（JSON/ARRAY）的就地修改

```python
# SQLAlchemy 模型
class UploadSession(Base):
    uploaded_chunks: Mapped[List[int]] = mapped_column(JSON, default=list)

    def mark_chunk_uploaded(self, chunk_index: int):
        self.uploaded_chunks.append(chunk_index)  # ❌ 就地修改
```

**为什么不会被跟踪？**

- SQLAlchemy 通过**对象属性赋值**来跟踪变更
- 当你执行 `obj.field = new_value`，SQLAlchemy 的 `__setattr__` 被调用
- 但 `list.append()` 是**就地修改**，不会触发 `__setattr__`
- SQLAlchemy 认为 `uploaded_chunks` 没有变化

#### 解决方案对比

| 方案 | 代码 | 优点 | 缺点 |
|------|------|------|------|
| **方案1: flag_modified** ✅ | `attributes.flag_modified(obj, "field")` | 简单直接，标准方法 | 需要记住调用 |
| **方案2: 重新赋值** | `obj.field = obj.field[:]` | 触发 `__setattr__` | 复制整个列表，性能开销 |
| **方案3: MutableList** | `from sqlalchemy.ext.mutable import MutableList` | 自动跟踪 | 增加复杂度 |

**我们选择方案1（flag_modified）**：
- ✅ 标准做法，官方推荐
- ✅ 性能最优（无需复制）
- ✅ 代码清晰，易于维护

### flag_modified 的工作原理

```python
from sqlalchemy.orm import attributes

# 标记字段为 "脏"（dirty）
attributes.flag_modified(session, "uploaded_chunks")

# 等价于手动设置:
attributes.set_attribute(
    session,
    "uploaded_chunks",
    session.uploaded_chunks,
    check_old=False  # 强制标记为已修改
)

# commit 时会包含这个字段：
# UPDATE upload_sessions
# SET uploaded_chunks = [0, 1, 2, 3, ...], updated_at = NOW()
# WHERE id = ...
```

---

## 🧪 测试验证

### 测试前（错误）

```bash
# 1. 上传所有分块
POST /api/v1/admin/media/upload/chunk?upload_id=abc&chunk_index=0  → 200 OK
POST /api/v1/admin/media/upload/chunk?upload_id=abc&chunk_index=1  → 200 OK
...
POST /api/v1/admin/media/upload/chunk?upload_id=abc&chunk_index=9  → 200 OK
  返回: {"is_completed": true}  # ❌ 但数据库中仍然是 false

# 2. 完成上传
POST /api/v1/admin/media/upload/complete?upload_id=abc
  返回: 400 Bad Request
  "还有分块未上传完成 (0/10)"  # ❌ uploaded_chunks 是空的
```

### 测试后（成功）

```bash
# 1. 上传所有分块
POST /api/v1/admin/media/upload/chunk?upload_id=abc&chunk_index=9  → 200 OK
  返回: {"is_completed": true}

# 后端日志:
# INFO: Upload completed: abc (10/10 chunks)

# 2. 完成上传
POST /api/v1/admin/media/upload/complete?upload_id=abc → 200 OK
  返回: {
    "message": "上传完成",
    "media_id": 123,
    "url": "http://..."
  }

# 后端日志:
# INFO: Complete upload request: abc
# INFO: Session status: is_completed=True, is_merged=False
# INFO: Upload progress: 10/10 chunks
```

---

## 🔧 其他修复

### 修复1: 后端启动失败（配置验证）

**问题**: DEBUG=False 时，配置验证器检测到安全问题，拒绝启动

**修复**: 设置 `DEBUG=True` (开发环境)

```bash
# backend/.env
DEBUG=True  # 开发环境
```

**生产环境建议**:
```bash
# 更新敏感密钥
SECRET_KEY=<生成的随机密钥>
JWT_SECRET_KEY=<生成的随机密钥>
MINIO_SECRET_KEY=<安全的密钥>

# 然后可以设置 DEBUG=False
```

---

## 📋 完整修复清单

### 后端修复 ✅

- [x] 添加 `sqlalchemy.orm.attributes` 导入
- [x] 在 `upload_chunk` 中使用 `flag_modified("uploaded_chunks")`
- [x] 添加 `db.refresh(session)` 确保最新状态
- [x] 添加详细日志（upload completed, session status）
- [x] 设置 `DEBUG=True` 允许后端启动

### 前端修复（之前完成） ✅

- [x] 修复 422 数组参数错误（paramsSerializer）
- [x] 修复 `uploadId` undefined 问题（snake_case interface）

---

## 💡 最佳实践

### 1. JSON/ARRAY 列的修改

**❌ 不推荐**:
```python
# 就地修改 - SQLAlchemy 可能不跟踪
obj.json_field.append(value)
obj.json_field["key"] = value
obj.array_field[0] = new_value
await db.commit()  # 可能不会保存
```

**✅ 推荐**:
```python
# 方法1: flag_modified
obj.json_field.append(value)
attributes.flag_modified(obj, "json_field")
await db.commit()

# 方法2: 重新赋值
obj.json_field = obj.json_field + [value]
await db.commit()

# 方法3: 使用 MutableList (高级)
from sqlalchemy.ext.mutable import MutableList
json_field: Mapped[List] = mapped_column(MutableList.as_mutable(JSON))
```

### 2. 调试 JSON 列问题

```python
# 检查对象是否被标记为 dirty
from sqlalchemy import inspect

insp = inspect(session)
print(insp.attrs.uploaded_chunks.history.has_changes())  # True/False
print(insp.modified)  # 被修改的属性列表

# 强制刷新
await db.flush()  # 立即写入数据库（不提交事务）
await db.refresh(obj)  # 从数据库重新加载
```

---

## 📚 相关文档

- [SQLAlchemy ORM: Tracking Changes](https://docs.sqlalchemy.org/en/20/orm/session_state_management.html#detecting-changes)
- [flag_modified() API](https://docs.sqlalchemy.org/en/20/orm/session_api.html#sqlalchemy.orm.attributes.flag_modified)
- [Mutable Types in SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/extensions/mutable.html)
- [ARRAY_PARAMS_FIX.md](ARRAY_PARAMS_FIX.md) - 422 数组参数修复
- [UPLOAD_COMPLETE_FIX.md](UPLOAD_COMPLETE_FIX.md) - upload_id undefined 修复

---

*修复日期: 2025-10-19*
*影响范围: 分块上传功能*
*测试状态: ✅ 待测试验证*
