"""
数据库批处理优化工具
用于高效处理大量数据的插入、更新、删除操作
"""

from typing import Any, Callable, List, TypeVar

from loguru import logger
from sqlalchemy import delete as sql_delete
from sqlalchemy import select, update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BatchProcessor:
    """批处理器 - 提升大量数据操作的性能"""

    @staticmethod
    async def batch_insert(
        db: AsyncSession,
        model_class: type,
        items: List[dict],
        batch_size: int = 1000,
    ) -> int:
        """
        批量插入数据

        Args:
            db: 数据库会话
            model_class: SQLAlchemy模型类
            items: 要插入的数据列表（字典格式）
            batch_size: 每批处理的记录数

        Returns:
            插入的记录总数

        Example:
            items = [
                {"title": "Video 1", "slug": "video-1"},
                {"title": "Video 2", "slug": "video-2"},
                ...
            ]
            count = await BatchProcessor.batch_insert(db, Video, items)
        """
        total = 0

        try:
            # 分批处理
            for i in range(0, len(items), batch_size):
                batch = items[i : i + batch_size]

                # 使用bulk_insert_mappings优化性能
                # 比逐条add快10-100倍
                await db.execute(model_class.__table__.insert(), batch)

                total += len(batch)
                logger.debug(
                    f"Batch insert progress: {total}/{len(items)} ({total/len(items)*100:.1f}%)"
                )

            await db.commit()
            logger.info(f"✅ Batch insert completed: {total} records")

            return total

        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Batch insert failed: {e}")
            raise

    @staticmethod
    async def batch_update(
        db: AsyncSession,
        model_class: type,
        updates: List[dict],
        id_field: str = "id",
        batch_size: int = 1000,
    ) -> int:
        """
        批量更新数据

        Args:
            db: 数据库会话
            model_class: SQLAlchemy模型类
            updates: 更新数据列表（必须包含id字段）
            id_field: ID字段名称
            batch_size: 每批处理的记录数

        Returns:
            更新的记录总数

        Example:
            updates = [
                {"id": 1, "view_count": 100},
                {"id": 2, "view_count": 200},
            ]
            count = await BatchProcessor.batch_update(db, Video, updates)
        """
        total = 0

        try:
            for i in range(0, len(updates), batch_size):
                batch = updates[i : i + batch_size]

                # 使用bulk_update_mappings
                await db.execute(
                    sql_update(model_class.__table__),
                    batch,
                )

                total += len(batch)
                logger.debug(
                    f"Batch update progress: {total}/{len(updates)} ({total/len(updates)*100:.1f}%)"
                )

            await db.commit()
            logger.info(f"✅ Batch update completed: {total} records")

            return total

        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Batch update failed: {e}")
            raise

    @staticmethod
    async def batch_delete(
        db: AsyncSession,
        model_class: type,
        ids: List[int],
        id_field: str = "id",
        batch_size: int = 1000,
    ) -> int:
        """
        批量删除数据

        Args:
            db: 数据库会话
            model_class: SQLAlchemy模型类
            ids: 要删除的ID列表
            id_field: ID字段名称
            batch_size: 每批处理的记录数

        Returns:
            删除的记录总数

        Example:
            ids = [1, 2, 3, 4, 5]
            count = await BatchProcessor.batch_delete(db, Video, ids)
        """
        total = 0

        try:
            for i in range(0, len(ids), batch_size):
                batch_ids = ids[i : i + batch_size]

                # 使用IN查询批量删除
                result = await db.execute(
                    sql_delete(model_class).where(
                        getattr(model_class, id_field).in_(batch_ids)
                    )
                )

                total += result.rowcount  # type: ignore
                logger.debug(
                    f"Batch delete progress: {total}/{len(ids)} ({total/len(ids)*100:.1f}%)"
                )

            await db.commit()
            logger.info(f"✅ Batch delete completed: {total} records")

            return total

        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Batch delete failed: {e}")
            raise

    @staticmethod
    async def batch_process_with_callback(
        items: List[T],
        process_func: Callable[[T], Any],
        batch_size: int = 100,
        callback: Callable[[int, int], None] | None = None,
    ) -> List[Any]:
        """
        使用回调函数批量处理数据（适用于复杂逻辑）

        Args:
            items: 要处理的项目列表
            process_func: 处理函数
            batch_size: 每批处理的项目数
            callback: 进度回调函数(当前进度, 总数)

        Returns:
            处理结果列表

        Example:
            async def process_video(video):
                # 复杂处理逻辑
                return await generate_thumbnail(video)

            results = await BatchProcessor.batch_process_with_callback(
                videos,
                process_video,
                callback=lambda current, total: print(f"{current}/{total}")
            )
        """
        results = []

        for i in range(0, len(items), batch_size):
            batch = items[i : i + batch_size]

            # 处理当前批次
            for item in batch:
                result = await process_func(item) if callable(process_func) else None
                results.append(result)

            # 调用进度回调
            if callback:
                callback(min(i + batch_size, len(items)), len(items))

        return results

    @staticmethod
    async def chunked_query(
        db: AsyncSession,
        model_class: type,
        chunk_size: int = 1000,
        filters: list | None = None,
    ):
        """
        分块查询大表（生成器模式）

        Args:
            db: 数据库会话
            model_class: SQLAlchemy模型类
            chunk_size: 每块记录数
            filters: 过滤条件列表

        Yields:
            每次yield一批记录

        Example:
            async for chunk in BatchProcessor.chunked_query(db, Video, chunk_size=1000):
                for video in chunk:
                    await process_video(video)
        """
        offset = 0

        while True:
            # 构建查询
            query = select(model_class)

            if filters:
                query = query.filter(*filters)

            query = query.offset(offset).limit(chunk_size)

            # 执行查询
            result = await db.execute(query)
            chunk = result.scalars().all()

            if not chunk:
                break

            yield chunk

            # 如果返回的记录少于chunk_size，说明已经到底
            if len(chunk) < chunk_size:
                break

            offset += chunk_size


# 便捷函数
async def bulk_increment(
    db: AsyncSession,
    model_class: type,
    field_name: str,
    ids: List[int],
    increment: int = 1,
) -> int:
    """
    批量增加字段值（如view_count += 1）

    Args:
        db: 数据库会话
        model_class: SQLAlchemy模型类
        field_name: 字段名
        ids: ID列表
        increment: 增量值

    Returns:
        更新的记录数

    Example:
        # 批量增加观看次数
        await bulk_increment(db, Video, "view_count", video_ids, increment=1)
    """
    try:
        field = getattr(model_class, field_name)

        result = await db.execute(
            sql_update(model_class)
            .where(model_class.id.in_(ids))
            .values({field_name: field + increment})
        )

        await db.commit()
        return result.rowcount  # type: ignore

    except Exception as e:
        await db.rollback()
        logger.error(f"Bulk increment failed: {e}")
        raise
