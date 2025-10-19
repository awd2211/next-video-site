# 🔍 Media 删除目录功能分析

**问题**: 删除目录功能分析和优化
**端点**: `DELETE /api/v1/admin/media/batch/delete`
**日期**: 2025-10-19

---

## 📊 当前实现分析

### 1. 前端调用

**文件**: `admin-frontend/src/pages/MediaManager/index.tsx:302`

```typescript
const handleDelete = async (mediaIds: number[], permanent: boolean = false) => {
  try {
    await axios.delete('/api/v1/admin/media/batch/delete', {
      params: {
        media_ids: mediaIds,  // 可以是文件或文件夹的ID
        permanent,            // false = 软删除, true = 永久删除
      },
    })
    message.success('删除成功')
    loadFileList()
    loadFolderTree()
    loadRecycleBinCount()
    setSelectedFiles([])
  } catch (error: any) {
    message.error(error.response?.data?.detail || '删除失败')
  }
}
```

### 2. 后端实现

**文件**: `app/admin/media.py:987`

```python
@router.delete("/media/batch/delete")
async def batch_delete_media(
    media_ids: List[int] = Query(...),
    permanent: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """批量删除文件/文件夹"""

    deleted_count = 0
    errors = []

    for media_id in media_ids:
        try:
            media_query = select(Media).where(Media.id == media_id)
            media_result = await db.execute(media_query)
            media = media_result.scalar_one_or_none()

            if not media:
                errors.append({"id": media_id, "error": "不存在"})
                continue

            if permanent:
                # 永久删除
                if not media.is_folder:  # ⚠️ 只删除文件的物理存储
                    try:
                        minio_client.delete_file(media.file_path)
                    except Exception as e:
                        print(f"删除文件失败: {e}")

                await db.delete(media)  # 删除数据库记录
            else:
                # 软删除
                media.is_deleted = True
                media.deleted_at = datetime.utcnow()

            deleted_count += 1

        except Exception as e:
            errors.append({"id": media_id, "error": str(e)})

    await db.commit()

    return {
        "message": "批量删除完成",
        "deleted_count": deleted_count,
        "total_count": len(media_ids),
        "errors": errors
    }
```

---

## ⚠️ 发现的问题

### 🔴 HIGH PRIORITY

#### 1. **删除文件夹时子项未处理**

**问题**: 删除文件夹时，文件夹下的所有文件和子文件夹**没有被一起删除**！

**影响**:
- 删除父文件夹后，子项变成"孤儿"（`parent_id` 指向已删除的文件夹）
- 这些子项在UI中不可见（因为父文件夹已删除）
- 但仍然占用存储空间
- 数据库中留下垃圾数据

**示例**:
```
删除前:
📁 Projects (id=1)
  ├─ 📁 2024 (id=2, parent_id=1)
  │   ├─ 📄 video1.mp4 (id=3, parent_id=2)
  │   └─ 📄 video2.mp4 (id=4, parent_id=2)
  └─ 📄 readme.txt (id=5, parent_id=1)

删除 Projects (id=1) 后:
❌ Projects 被删除
⚠️  2024 (id=2, parent_id=1) - 孤儿！parent_id指向已删除的文件夹
⚠️  video1.mp4 (id=3, parent_id=2) - 孤儿！
⚠️  video2.mp4 (id=4, parent_id=2) - 孤儿！
⚠️  readme.txt (id=5, parent_id=1) - 孤儿！
```

#### 2. **缺少级联删除逻辑**

**当前代码**:
```python
# ❌ 只删除文件夹本身
await db.delete(media)  # 如果是文件夹，子项怎么办？
```

**应该**:
```python
# ✅ 递归删除所有子项
if media.is_folder:
    await delete_folder_recursively(db, media.id, permanent)
await db.delete(media)
```

#### 3. **软删除时子项状态不一致**

**问题**: 软删除文件夹时，只标记文件夹为 `is_deleted=True`，但子项仍然是 `is_deleted=False`

**影响**:
- 子项在"正常文件"列表中仍然可见，但点击无法访问（因为父文件夹已删除）
- 恢复文件夹后，路径可能断裂

### 🟡 MEDIUM PRIORITY

#### 4. **缺少限流保护**

```python
@router.delete("/media/batch/delete")  # ❌ 没有限流
async def batch_delete_media(...):
```

**风险**: 可能被滥用批量删除大量文件

#### 5. **没有批量大小限制**

```python
media_ids: List[int] = Query(...)  # ❌ 可以传入无限多个ID
```

**风险**: 可能导致超时或数据库锁定

#### 6. **错误处理不够细致**

```python
try:
    minio_client.delete_file(media.file_path)
except Exception as e:
    print(f"删除文件失败: {e}")  # ❌ 只打印，不记录到日志
```

---

## ✅ 修复方案

### 方案1: 递归删除子项（推荐）

```python
@router.delete("/media/batch/delete")
@limiter.limit(RateLimitPresets.STRICT)  # 🆕 添加限流
async def batch_delete_media(
    media_ids: List[int] = Query(..., max_length=100),  # 🆕 最多100个
    permanent: bool = Query(False),
    recursive: bool = Query(True, description="删除文件夹时是否递归删除子项"),
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """批量删除文件/文件夹"""

    deleted_count = 0
    errors = []

    async def delete_item_recursive(media_id: int, permanent: bool) -> int:
        """递归删除项目及其子项"""
        media = await db.get(Media, media_id)

        if not media or media.is_deleted:
            return 0

        count = 0

        # 如果是文件夹，先删除所有子项
        if media.is_folder and recursive:
            # 查找所有直接子项
            children_query = select(Media).where(
                and_(
                    Media.parent_id == media_id,
                    Media.is_deleted == False
                )
            )
            children_result = await db.execute(children_query)
            children = children_result.scalars().all()

            # 递归删除每个子项
            for child in children:
                count += await delete_item_recursive(child.id, permanent)

        # 删除当前项
        if permanent:
            # 永久删除
            if not media.is_folder:
                try:
                    minio_client.delete_file(media.file_path)
                    if media.thumbnail_path:
                        minio_client.delete_file(media.thumbnail_path)
                except Exception as e:
                    logger.error(f"Failed to delete file from MinIO: {e}")
                    # 继续删除数据库记录

            await db.delete(media)
        else:
            # 软删除
            media.is_deleted = True
            media.deleted_at = datetime.utcnow()

        return count + 1

    for media_id in media_ids:
        try:
            count = await delete_item_recursive(media_id, permanent)
            deleted_count += count
        except Exception as e:
            errors.append({"id": media_id, "error": str(e)})
            logger.error(f"Failed to delete media {media_id}: {e}")

    await db.commit()

    return {
        "message": "批量删除完成",
        "deleted_count": deleted_count,
        "total_count": len(media_ids),
        "errors": errors
    }
```

### 方案2: 数据库级联删除（备选）

**修改Model**:
```python
# app/models/media.py

class Media(Base):
    # ...

    # 🆕 修改parent关系，添加级联删除
    parent = relationship(
        "Media",
        remote_side=[id],
        backref=backref("children", cascade="all, delete-orphan")
    )
```

**优点**: 数据库自动处理级联
**缺点**: 无法控制MinIO文件删除，可能导致存储泄露

---

## 🔧 立即修复（推荐步骤）

### Step 1: 备份当前实现

```bash
cd /home/eric/video/backend/app/admin
cp media.py media.py.backup
```

### Step 2: 应用修复

使用上面的"方案1"代码替换 `batch_delete_media` 函数

### Step 3: 添加必需的导入

```python
# 在文件顶部添加
from app.utils.rate_limit import limiter, RateLimitPresets
from loguru import logger
```

### Step 4: 测试

```bash
# 1. 创建测试数据（文件夹+子文件）
curl -X POST "http://localhost:8000/api/v1/admin/media/folders/create?title=TestFolder" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 2. 删除文件夹（软删除）
curl -X DELETE "http://localhost:8000/api/v1/admin/media/batch/delete?media_ids=FOLDER_ID&permanent=false" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. 检查子项是否也被标记为已删除
curl "http://localhost:8000/api/v1/admin/media?page=1&page_size=50" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🧪 测试用例

### 测试1: 删除空文件夹
```
输入: 删除空文件夹
预期: 成功删除，deleted_count=1
```

### 测试2: 删除包含文件的文件夹
```
输入:
  📁 Folder (id=1)
    ├─ 📄 file1.jpg (id=2)
    └─ 📄 file2.mp4 (id=3)

删除 Folder (id=1)

预期:
  - deleted_count=3 (文件夹+2个文件)
  - file1.jpg, file2.mp4 也被标记为 is_deleted=True
  - MinIO中的file1.jpg, file2.mp4 被删除（如果permanent=true）
```

### 测试3: 删除嵌套文件夹
```
输入:
  📁 A (id=1)
    ├─ 📁 B (id=2)
    │   └─ 📄 file.jpg (id=3)
    └─ 📄 file2.mp4 (id=4)

删除 A (id=1)

预期:
  - deleted_count=4
  - 所有子项递归删除
```

### 测试4: 批量删除限制
```
输入: media_ids = [1, 2, 3, ..., 101]  # 101个ID

预期:
  - 422 错误
  - "一次最多删除100个文件"
```

---

## 📊 性能影响

### 优化前
- 删除1个文件夹 = 1次数据库操作
- 子项变成孤儿 ❌

### 优化后
- 删除1个文件夹 = N次数据库操作（N=文件夹+所有子项）
- 所有子项正确删除 ✅

**性能对比**:
| 操作 | 旧实现 | 新实现 | 影响 |
|------|--------|--------|------|
| 删除空文件夹 | 1次查询 | 2次查询 | +100% |
| 删除含10个文件的文件夹 | 1次查询 | 11次查询 | +1000% |
| 删除含100个文件的文件夹 | 1次查询 | 101次查询 | +10000% |

**优化建议**:
```python
# 使用批量操作减少查询次数
async def delete_item_recursive(media_id: int, permanent: bool) -> int:
    # 一次查询获取所有子项
    all_descendants = await get_all_descendants(db, media_id)

    # 批量删除
    if permanent:
        await db.execute(
            delete(Media).where(Media.id.in_([d.id for d in all_descendants]))
        )
    else:
        await db.execute(
            update(Media)
            .where(Media.id.in_([d.id for d in all_descendants]))
            .values(is_deleted=True, deleted_at=datetime.utcnow())
        )
```

---

## 🎯 实施优先级

1. **立即** - 添加递归删除逻辑
2. **本周** - 添加限流和批量限制
3. **下周** - 性能优化（批量操作）
4. **长期** - 添加数据库级联约束

---

## 📚 相关文档

- [MEDIA_MODULE_ANALYSIS.md](MEDIA_MODULE_ANALYSIS.md) - Media模块完整分析
- [VALIDATION_ERROR_GUIDE.md](VALIDATION_ERROR_GUIDE.md) - 验证错误诊断

---

*分析日期: 2025-10-19*
*优先级: HIGH - 影响数据完整性*
