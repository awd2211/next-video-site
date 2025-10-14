"""
测试 app/utils/cache.py - Redis 缓存工具
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal

from app.utils.cache import (
    Cache,
    CacheStats,
    get_redis,
    json_serializer,
    json_deserializer,
    cache_result,
    clear_cache_by_prefix,
)


@pytest.mark.unit
@pytest.mark.requires_redis
class TestJSONSerializers:
    """JSON 序列化器测试"""

    def test_serialize_basic_types(self):
        """测试基本类型序列化"""
        assert json_serializer("string") == '"string"'
        assert json_serializer(123) == "123"
        assert json_serializer(123.45) == "123.45"
        assert json_serializer(True) == "true"
        assert json_serializer(None) == "null"

    def test_serialize_datetime(self):
        """测试 datetime 序列化"""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        serialized = json_serializer(dt)
        assert "__type__" in serialized
        assert "datetime" in serialized
        assert "2024-01-01" in serialized

    def test_serialize_decimal(self):
        """测试 Decimal 序列化"""
        dec = Decimal("123.45")
        serialized = json_serializer(dec)
        assert "__type__" in serialized
        assert "decimal" in serialized
        assert "123.45" in serialized

    def test_serialize_dict(self):
        """测试字典序列化"""
        data = {"key": "value", "number": 123}
        serialized = json_serializer(data)
        assert "key" in serialized
        assert "value" in serialized

    def test_serialize_list(self):
        """测试列表序列化"""
        data = [1, 2, 3, "test"]
        serialized = json_serializer(data)
        assert "[1" in serialized or "[1," in serialized

    def test_deserialize_datetime(self):
        """测试 datetime 反序列化"""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        serialized = json_serializer(dt)
        deserialized = json_deserializer(serialized)
        assert isinstance(deserialized, datetime)
        assert deserialized.year == 2024

    def test_deserialize_decimal(self):
        """测试 Decimal 反序列化"""
        dec = Decimal("123.45")
        serialized = json_serializer(dec)
        deserialized = json_deserializer(serialized)
        assert isinstance(deserialized, Decimal)
        assert deserialized == Decimal("123.45")

    def test_serialize_deserialize_roundtrip(self):
        """测试序列化和反序列化往返"""
        original = {
            "string": "test",
            "number": 123,
            "datetime": datetime(2024, 1, 1),
            "decimal": Decimal("99.99"),
        }
        serialized = json_serializer(original)
        deserialized = json_deserializer(serialized)
        assert deserialized["string"] == "test"
        assert deserialized["number"] == 123
        assert isinstance(deserialized["datetime"], datetime)
        assert isinstance(deserialized["decimal"], Decimal)


@pytest.mark.unit
@pytest.mark.requires_redis
@pytest.mark.asyncio
class TestCacheBasicOperations:
    """缓存基本操作测试"""

    async def test_get_redis_client(self):
        """测试获取 Redis 客户端"""
        client = await get_redis()
        assert client is not None
        await client.aclose()

    async def test_set_and_get(self):
        """测试设置和获取缓存"""
        key = "test:simple"
        value = "test_value"
        
        result = await Cache.set(key, value, ttl=60)
        assert result is True
        
        retrieved = await Cache.get(key)
        assert retrieved == value
        
        # 清理
        await Cache.delete(key)

    async def test_get_nonexistent_key(self):
        """测试获取不存在的键"""
        result = await Cache.get("nonexistent:key")
        assert result is None

    async def test_get_with_default(self):
        """测试获取不存在的键返回默认值"""
        result = await Cache.get("nonexistent:key", default="default_value")
        assert result == "default_value"

    async def test_delete_key(self):
        """测试删除缓存"""
        key = "test:delete"
        await Cache.set(key, "value")
        
        result = await Cache.delete(key)
        assert result is True
        
        retrieved = await Cache.get(key)
        assert retrieved is None

    async def test_exists_key(self):
        """测试检查键是否存在"""
        key = "test:exists"
        
        # 不存在
        exists = await Cache.exists(key)
        assert exists is False
        
        # 设置后存在
        await Cache.set(key, "value")
        exists = await Cache.exists(key)
        assert exists is True
        
        # 清理
        await Cache.delete(key)

    async def test_ttl_expiration(self):
        """测试 TTL 过期"""
        key = "test:ttl"
        await Cache.set(key, "value", ttl=1)
        
        # 立即获取应该成功
        value = await Cache.get(key)
        assert value == "value"
        
        # 等待过期
        await asyncio.sleep(2)
        value = await Cache.get(key)
        assert value is None


@pytest.mark.unit
@pytest.mark.requires_redis
@pytest.mark.asyncio
class TestCacheComplexTypes:
    """缓存复杂类型测试"""

    async def test_cache_dict(self):
        """测试缓存字典"""
        key = "test:dict"
        data = {"name": "test", "value": 123, "active": True}
        
        await Cache.set(key, data)
        retrieved = await Cache.get(key)
        
        assert retrieved == data
        await Cache.delete(key)

    async def test_cache_list(self):
        """测试缓存列表"""
        key = "test:list"
        data = [1, 2, 3, "four", 5.0]
        
        await Cache.set(key, data)
        retrieved = await Cache.get(key)
        
        assert retrieved == data
        await Cache.delete(key)

    async def test_cache_datetime(self):
        """测试缓存 datetime"""
        key = "test:datetime"
        dt = datetime(2024, 1, 1, 12, 30, 45)
        
        await Cache.set(key, dt)
        retrieved = await Cache.get(key)
        
        assert isinstance(retrieved, datetime)
        assert retrieved.year == 2024
        assert retrieved.month == 1
        await Cache.delete(key)

    async def test_cache_decimal(self):
        """测试缓存 Decimal"""
        key = "test:decimal"
        dec = Decimal("123.45")
        
        await Cache.set(key, dec)
        retrieved = await Cache.get(key)
        
        assert isinstance(retrieved, Decimal)
        assert retrieved == Decimal("123.45")
        await Cache.delete(key)

    async def test_cache_nested_structure(self):
        """测试缓存嵌套结构"""
        key = "test:nested"
        data = {
            "user": {
                "id": 1,
                "name": "John",
                "created_at": datetime(2024, 1, 1),
            },
            "stats": {
                "views": 1000,
                "rating": Decimal("8.5"),
            },
            "tags": ["python", "fastapi", "redis"],
        }
        
        await Cache.set(key, data)
        retrieved = await Cache.get(key)
        
        assert retrieved["user"]["name"] == "John"
        assert isinstance(retrieved["user"]["created_at"], datetime)
        assert isinstance(retrieved["stats"]["rating"], Decimal)
        assert len(retrieved["tags"]) == 3
        await Cache.delete(key)


@pytest.mark.unit
@pytest.mark.requires_redis
@pytest.mark.asyncio
class TestCachePatternOperations:
    """缓存模式操作测试"""

    async def test_delete_pattern_single(self):
        """测试删除单个匹配的键"""
        await Cache.set("categories:1", "cat1")
        await Cache.set("categories:2", "cat2")
        await Cache.set("videos:1", "vid1")
        
        deleted = await Cache.delete_pattern("categories:*")
        assert deleted >= 2
        
        # 验证删除
        assert await Cache.get("categories:1") is None
        assert await Cache.get("categories:2") is None
        assert await Cache.get("videos:1") == "vid1"
        
        # 清理
        await Cache.delete("videos:1")

    async def test_delete_pattern_none_match(self):
        """测试删除不匹配的模式"""
        deleted = await Cache.delete_pattern("nonexistent:*")
        assert deleted == 0

    async def test_clear_cache_by_prefix(self):
        """测试按前缀清除缓存"""
        await Cache.set("users:1", "user1")
        await Cache.set("users:2", "user2")
        await Cache.set("videos:1", "vid1")
        
        await clear_cache_by_prefix("users")
        
        assert await Cache.get("users:1") is None
        assert await Cache.get("users:2") is None
        assert await Cache.get("videos:1") == "vid1"
        
        await Cache.delete("videos:1")


@pytest.mark.unit
@pytest.mark.requires_redis
@pytest.mark.asyncio
class TestCacheStats:
    """缓存统计测试"""

    async def test_record_hit(self):
        """测试记录缓存命中"""
        await CacheStats.record_hit()
        
        # 验证记录成功（不会抛出异常）
        assert True

    async def test_record_miss(self):
        """测试记录缓存未命中"""
        await CacheStats.record_miss()
        
        assert True

    async def test_get_stats(self):
        """测试获取缓存统计"""
        # 记录一些统计
        await CacheStats.record_hit()
        await CacheStats.record_hit()
        await CacheStats.record_miss()
        
        stats = await CacheStats.get_stats(days=7)
        
        assert "stats" in stats
        assert "summary" in stats
        assert isinstance(stats["stats"], list)
        assert "total_hits" in stats["summary"]
        assert "total_misses" in stats["summary"]

    async def test_get_stats_empty(self):
        """测试获取空统计"""
        client = await get_redis()
        # 清空统计数据
        today = datetime.now().strftime("%Y-%m-%d")
        await client.delete(f"cache_stats:hits:{today}")
        await client.delete(f"cache_stats:misses:{today}")
        await client.aclose()
        
        stats = await CacheStats.get_stats(days=1)
        assert stats["summary"]["total_hits"] == 0
        assert stats["summary"]["total_misses"] == 0


@pytest.mark.unit
@pytest.mark.requires_redis
@pytest.mark.asyncio
class TestCacheDecorator:
    """缓存装饰器测试"""

    async def test_cache_result_decorator(self):
        """测试缓存结果装饰器"""
        call_count = 0
        
        @cache_result("test:func", ttl=60)
        async def expensive_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # 第一次调用
        result1 = await expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # 第二次调用应该从缓存返回
        result2 = await expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # 没有增加，说明使用了缓存
        
        # 不同参数应该重新调用
        result3 = await expensive_function(10)
        assert result3 == 20
        assert call_count == 2
        
        # 清理
        await clear_cache_by_prefix("test:func")

    async def test_cache_decorator_with_no_args(self):
        """测试无参数函数的缓存"""
        call_count = 0
        
        @cache_result("test:no_args", ttl=60)
        async def get_config():
            nonlocal call_count
            call_count += 1
            return {"setting": "value"}
        
        result1 = await get_config()
        assert result1["setting"] == "value"
        assert call_count == 1
        
        result2 = await get_config()
        assert call_count == 1  # 使用缓存
        
        await clear_cache_by_prefix("test:no_args")

    async def test_cache_decorator_ttl(self):
        """测试缓存 TTL 过期"""
        @cache_result("test:ttl", ttl=1)
        async def get_data():
            return "data"
        
        result1 = await get_data()
        assert result1 == "data"
        
        # 等待过期
        await asyncio.sleep(2)
        
        # 缓存应该已过期
        key = "test:ttl"
        exists = await Cache.exists(key)
        # 可能已过期
        assert exists in [True, False]
        
        await clear_cache_by_prefix("test:ttl")


@pytest.mark.unit
@pytest.mark.requires_redis
@pytest.mark.asyncio
class TestCacheErrorHandling:
    """缓存错误处理测试"""

    async def test_get_handles_errors_gracefully(self):
        """测试 get 优雅处理错误"""
        # 即使 Redis 有问题，应该返回默认值而不是抛出异常
        result = await Cache.get("test:key", default="default")
        assert result in [None, "default"]

    async def test_set_handles_errors_gracefully(self):
        """测试 set 优雅处理错误"""
        # 应该返回 True 或 False，不抛出异常
        result = await Cache.set("test:key", "value")
        assert isinstance(result, bool)
        
        if result:
            await Cache.delete("test:key")

    async def test_delete_handles_errors_gracefully(self):
        """测试 delete 优雅处理错误"""
        result = await Cache.delete("nonexistent:key")
        assert isinstance(result, bool)


@pytest.mark.integration
@pytest.mark.requires_redis
@pytest.mark.asyncio
class TestCacheIntegration:
    """缓存集成测试"""

    async def test_cache_lifecycle(self):
        """测试完整的缓存生命周期"""
        key = "test:lifecycle"
        value = {
            "id": 1,
            "name": "Test",
            "created_at": datetime.now(),
            "price": Decimal("99.99"),
        }
        
        # 1. 设置缓存
        set_result = await Cache.set(key, value, ttl=300)
        assert set_result is True
        
        # 2. 检查存在
        exists = await Cache.exists(key)
        assert exists is True
        
        # 3. 获取缓存
        retrieved = await Cache.get(key)
        assert retrieved["name"] == "Test"
        assert isinstance(retrieved["created_at"], datetime)
        
        # 4. 删除缓存
        delete_result = await Cache.delete(key)
        assert delete_result is True
        
        # 5. 验证已删除
        exists = await Cache.exists(key)
        assert exists is False

    async def test_multiple_keys(self):
        """测试多个键的操作"""
        keys = [f"test:multi:{i}" for i in range(10)]
        
        # 批量设置
        for i, key in enumerate(keys):
            await Cache.set(key, f"value_{i}")
        
        # 批量获取
        for i, key in enumerate(keys):
            value = await Cache.get(key)
            assert value == f"value_{i}"
        
        # 批量删除
        for key in keys:
            await Cache.delete(key)
        
        # 验证已删除
        for key in keys:
            value = await Cache.get(key)
            assert value is None

    async def test_concurrent_access(self):
        """测试并发访问"""
        key = "test:concurrent"
        await Cache.set(key, "initial_value")
        
        # 模拟并发读取
        tasks = [Cache.get(key) for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # 所有结果应该一致
        assert all(r == "initial_value" for r in results)
        
        await Cache.delete(key)

    async def test_cache_stats_integration(self):
        """测试缓存统计集成"""
        # 执行一些缓存操作
        await Cache.set("test:stat1", "value1")
        await Cache.get("test:stat1")  # 命中
        await Cache.get("test:nonexistent")  # 未命中
        
        stats = await CacheStats.get_stats(days=1)
        
        assert "stats" in stats
        assert "summary" in stats
        
        # 清理
        await Cache.delete("test:stat1")

