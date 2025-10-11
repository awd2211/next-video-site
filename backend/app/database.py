from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, event, pool
from sqlalchemy.orm import sessionmaker
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Connection pool configuration
# 根据应用规模和负载调整这些参数
POOL_SIZE = 20  # 连接池大小（默认5）- 增加以支持更多并发请求
MAX_OVERFLOW = 40  # 超出pool_size后可以创建的连接数（默认10）
POOL_TIMEOUT = 30  # 获取连接的超时时间（秒）
POOL_RECYCLE = 3600  # 连接回收时间（秒）- 1小时，防止数据库断开长时间空闲的连接
POOL_PRE_PING = True  # 在使用连接前检查连接是否有效

# Async engine for FastAPI
# 注意：异步引擎会自动使用 AsyncAdaptedQueuePool，不需要显式指定
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=POOL_PRE_PING,  # 在每次连接使用前ping数据库，确保连接有效
    pool_size=POOL_SIZE,  # 连接池维持的连接数
    max_overflow=MAX_OVERFLOW,  # 允许创建的额外连接数
    pool_timeout=POOL_TIMEOUT,  # 等待可用连接的超时时间
    pool_recycle=POOL_RECYCLE,  # 自动回收超过此时间的连接
    # 异步引擎默认使用 AsyncAdaptedQueuePool，适合高并发场景
    # 连接参数优化
    connect_args={
        "server_settings": {
            "application_name": "video_platform_async",  # 用于数据库监控
        },
    },
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Alias for compatibility
async_session_maker = AsyncSessionLocal

# Sync engine for Alembic migrations
sync_engine = create_engine(
    settings.DATABASE_URL_SYNC,
    echo=settings.DEBUG,
    pool_pre_ping=POOL_PRE_PING,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT,
    pool_recycle=POOL_RECYCLE,
    poolclass=pool.QueuePool,
)

# Sync session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)

# Base class for models
Base = declarative_base()


# 连接池事件监听器 - 用于监控和调试
@event.listens_for(async_engine.sync_engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """当创建新连接时触发"""
    logger.debug(f"New database connection established: {id(dbapi_conn)}")


@event.listens_for(async_engine.sync_engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """当从连接池取出连接时触发"""
    logger.debug(f"Connection checked out from pool: {id(dbapi_conn)}")


@event.listens_for(async_engine.sync_engine, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    """当连接返回到连接池时触发"""
    logger.debug(f"Connection returned to pool: {id(dbapi_conn)}")


# 连接池状态查询函数
def get_pool_status():
    """获取连接池状态信息"""
    pool_obj = async_engine.pool
    return {
        "pool_size": pool_obj.size(),  # type: ignore
        "checked_in": pool_obj.checkedin(),  # type: ignore
        "checked_out": pool_obj.checkedout(),  # type: ignore
        "overflow": pool_obj.overflow(),  # type: ignore
        "total_connections": pool_obj.size() + pool_obj.overflow(),  # type: ignore
    }


# Dependency for getting async DB session
async def get_db():
    """
    获取数据库session（自动commit）
    适用于大多数场景
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db_read_only():
    """
    获取只读数据库session（不commit）
    适用于纯查询场景，性能更好
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # 只读操作不需要commit
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
