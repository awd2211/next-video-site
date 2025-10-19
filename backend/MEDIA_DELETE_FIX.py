"""
Media 删除功能修复代码

使用方法:
1. 备份当前文件: cp app/admin/media.py app/admin/media.py.backup
2. 复制下面的函数，替换 media.py 中的 batch_delete_media 函数
3. 在文件顶部添加导入: from app.utils.rate_limit import limiter, RateLimitPresets
"""

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
from sqlalchemy import and_, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.media import Media
from app.models.user import AdminUser
from app.utils.dependencies import get_current_admin_user
from app.utils.minio_client import minio_client
from app.utils.rate_limit import limiter, RateLimitPresets

router = APIRouter()


@router.delete("/media/batch/delete")
@limiter.limit(RateLimitPresets.STRICT)  # 🆕 添加限流
async def batch_delete_media(
    media_ids: List[int] = Query(..., max_length=100, description="媒体ID列表，最多100个"),  # 🆕 最多100个
    permanent: bool = Query(False, description="是否永久删除"),
    recursive: bool = Query(True, description="删除文件夹时是否递归删除子项"),  # 🆕 递归选项
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """
    批量删除文件/文件夹

    特性:
    - 支持软删除和永久删除
    - 删除文件夹时自动递归删除所有子项（可选）
    - 永久删除时清理MinIO存储
    - 限流保护和批量大小限制
    """

    if len(media_ids) > 100:
        raise HTTPException(status_code=400, detail="一次最多删除100个文件")

    deleted_count = 0
    errors = []

    async def delete_item_recursive(media_id: int, permanent: bool) -> int:
        """
        递归删除项目及其子项

        Args:
            media_id: 要删除的媒体ID
            permanent: 是否永久删除

        Returns:
            删除的项目总数
        """
        # 获取媒体项
        media = await db.get(Media, media_id)

        if not media or media.is_deleted:
            return 0

        count = 0

        # 如果是文件夹且启用递归，先删除所有子项
        if media.is_folder and recursive:
            logger.info(f"Deleting folder recursively: {media.title} (id={media_id})")

            # 查找所有直接子项
            children_query = select(Media).where(
                and_(
                    Media.parent_id == media_id,
                    Media.is_deleted == False
                )
            )
            children_result = await db.execute(children_query)
            children = children_result.scalars().all()

            logger.info(f"Found {len(children)} children in folder {media.title}")

            # 递归删除每个子项
            for child in children:
                child_count = await delete_item_recursive(child.id, permanent)
                count += child_count

        # 删除当前项
        if permanent:
            # 永久删除
            logger.info(f"Permanently deleting: {media.title} (id={media_id}, is_folder={media.is_folder})")

            if not media.is_folder:
                # 删除MinIO中的文件
                try:
                    if media.file_path:
                        minio_client.delete_file(media.file_path)
                        logger.info(f"Deleted file from MinIO: {media.file_path}")

                    if media.thumbnail_path:
                        minio_client.delete_file(media.thumbnail_path)
                        logger.info(f"Deleted thumbnail from MinIO: {media.thumbnail_path}")

                except Exception as e:
                    logger.error(f"Failed to delete file from MinIO: {e}")
                    # 继续删除数据库记录，即使MinIO删除失败

            # 从数据库删除
            await db.delete(media)
        else:
            # 软删除
            logger.info(f"Soft deleting: {media.title} (id={media_id})")
            media.is_deleted = True
            media.deleted_at = datetime.utcnow()

        return count + 1

    # 处理每个请求的ID
    for media_id in media_ids:
        try:
            count = await delete_item_recursive(media_id, permanent)
            deleted_count += count

            logger.info(f"Successfully deleted media_id={media_id}, total items deleted: {count}")

        except Exception as e:
            error_msg = str(e)
            errors.append({"id": media_id, "error": error_msg})
            logger.error(f"Failed to delete media_id={media_id}: {error_msg}", exc_info=True)

    # 提交所有更改
    try:
        await db.commit()
        logger.info(f"Batch delete committed: {deleted_count} items deleted")
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to commit batch delete: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")

    return {
        "message": "批量删除完成",
        "deleted_count": deleted_count,
        "total_requested": len(media_ids),
        "errors": errors,
        "recursive": recursive,
        "permanent": permanent
    }


# ============================================================
# 性能优化版本（适用于大量子项的情况）
# ============================================================

async def batch_delete_media_optimized(
    media_ids: List[int] = Query(..., max_length=100),
    permanent: bool = Query(False),
    recursive: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """
    批量删除 - 性能优化版本

    优化点:
    - 一次查询获取所有后代
    - 使用批量UPDATE/DELETE减少数据库操作
    """

    if len(media_ids) > 100:
        raise HTTPException(status_code=400, detail="一次最多删除100个文件")

    deleted_count = 0
    errors = []

    async def get_all_descendants(media_id: int) -> List[int]:
        """获取一个项目的所有后代ID（递归）"""
        descendants = [media_id]

        # 查询直接子项
        children_query = select(Media.id).where(
            and_(
                Media.parent_id == media_id,
                Media.is_deleted == False
            )
        )
        children_result = await db.execute(children_query)
        children_ids = children_result.scalars().all()

        # 递归获取每个子项的后代
        for child_id in children_ids:
            child_descendants = await get_all_descendants(child_id)
            descendants.extend(child_descendants)

        return descendants

    # 收集所有需要删除的ID
    all_ids_to_delete = set()

    for media_id in media_ids:
        try:
            # 检查项目是否存在
            media = await db.get(Media, media_id)

            if not media or media.is_deleted:
                errors.append({"id": media_id, "error": "不存在或已删除"})
                continue

            # 如果是文件夹且启用递归，获取所有后代
            if media.is_folder and recursive:
                descendants = await get_all_descendants(media_id)
                all_ids_to_delete.update(descendants)
                logger.info(f"Folder {media.title} has {len(descendants)} total items (including descendants)")
            else:
                all_ids_to_delete.add(media_id)

        except Exception as e:
            errors.append({"id": media_id, "error": str(e)})
            logger.error(f"Error processing media_id={media_id}: {e}")

    # 获取所有要删除的项目
    if not all_ids_to_delete:
        return {
            "message": "没有项目需要删除",
            "deleted_count": 0,
            "total_requested": len(media_ids),
            "errors": errors
        }

    items_query = select(Media).where(Media.id.in_(all_ids_to_delete))
    items_result = await db.execute(items_query)
    items_to_delete = items_result.scalars().all()

    # 永久删除：先删除MinIO文件
    if permanent:
        for item in items_to_delete:
            if not item.is_folder:
                try:
                    if item.file_path:
                        minio_client.delete_file(item.file_path)
                    if item.thumbnail_path:
                        minio_client.delete_file(item.thumbnail_path)
                except Exception as e:
                    logger.error(f"Failed to delete file from MinIO: {e}")

        # 批量删除数据库记录
        await db.execute(
            delete(Media).where(Media.id.in_(all_ids_to_delete))
        )
    else:
        # 批量软删除
        await db.execute(
            update(Media)
            .where(Media.id.in_(all_ids_to_delete))
            .values(
                is_deleted=True,
                deleted_at=datetime.utcnow()
            )
        )

    deleted_count = len(all_ids_to_delete)

    await db.commit()

    logger.info(f"Batch delete (optimized) completed: {deleted_count} items")

    return {
        "message": "批量删除完成",
        "deleted_count": deleted_count,
        "total_requested": len(media_ids),
        "errors": errors,
        "recursive": recursive,
        "permanent": permanent
    }


# ============================================================
# 使用说明
# ============================================================

"""
## 如何应用此修复

### 方法1: 直接替换函数（推荐）

1. 备份原文件:
   ```bash
   cd /home/eric/video/backend
   cp app/admin/media.py app/admin/media.py.backup
   ```

2. 在 media.py 顶部添加导入:
   ```python
   from app.utils.rate_limit import limiter, RateLimitPresets
   from loguru import logger
   ```

3. 找到 batch_delete_media 函数（line 987）

4. 替换为上面的新函数

5. 重启服务:
   ```bash
   # 如果使用uvicorn
   pkill -f uvicorn
   uvicorn app.main:app --reload
   ```

### 方法2: 使用性能优化版本

如果你的文件夹包含大量子项（>100个），使用 `batch_delete_media_optimized`

优点:
- 更少的数据库查询
- 批量操作更快

缺点:
- 复杂度更高
- 调试稍难

### 测试修复

```bash
# 1. 创建测试文件夹
curl -X POST "http://localhost:8000/api/v1/admin/media/folders/create?title=TestFolder" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 2. 在文件夹中上传几个文件
# ...

# 3. 删除文件夹（软删除，递归）
curl -X DELETE "http://localhost:8000/api/v1/admin/media/batch/delete?media_ids=FOLDER_ID&permanent=false&recursive=true" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. 验证子项也被删除
# 在回收站中应该看到文件夹和所有子项
```

## 重要提醒

⚠️ **在生产环境应用前，请先在开发环境测试！**

1. 测试空文件夹删除
2. 测试包含文件的文件夹删除
3. 测试嵌套文件夹删除
4. 测试软删除和永久删除
5. 测试批量删除限制（101个ID应该失败）
"""
