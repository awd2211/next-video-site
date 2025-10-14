# 后端测试文档

## 📚 测试结构

```
tests/
├── conftest.py                 # 共享 fixtures 和配置
├── pytest.ini                  # Pytest 配置（项目根目录）
├── README.md                   # 本文件
│
├── test_schemas.py             # ✅ Pydantic schemas 测试
├── test_validators.py          # ✅ 验证工具测试
├── test_api_endpoints.py       # ✅ 基础 API 测试
├── test_all_endpoints.py       # ✅ 公开 API 测试
├── test_comprehensive_api.py   # ✅ 综合 API 测试
│
├── admin/                      # 📁 Admin API 测试（计划中）
│   ├── test_admin_videos.py
│   ├── test_admin_users.py
│   ├── test_admin_content.py
│   └── ...
│
├── models/                     # 📁 Models 测试（计划中）
│   ├── test_user_models.py
│   ├── test_video_models.py
│   └── ...
│
├── utils/                      # 📁 Utils 测试（计划中）
│   ├── test_cache.py
│   ├── test_security.py
│   ├── test_minio.py
│   └── ...
│
├── middleware/                 # 📁 Middleware 测试（计划中）
│   ├── test_request_middleware.py
│   ├── test_security_middleware.py
│   └── ...
│
├── integration/                # 📁 集成测试（计划中）
│   ├── test_user_workflow.py
│   ├── test_video_workflow.py
│   └── ...
│
└── security/                   # 📁 安全测试（计划中）
    ├── test_injection.py
    ├── test_auth_security.py
    └── ...
```

---

## 🚀 快速开始

### 1. 安装测试依赖

```bash
cd backend

# 激活虚拟环境
source venv/bin/activate

# 安装开发和测试依赖
pip install -r requirements-dev.txt
```

### 2. 运行测试

```bash
# 快速测试（已有测试）
./run-backend-tests.sh quick

# 运行所有测试
./run-backend-tests.sh all

# 运行特定类型的测试
./run-backend-tests.sh api
./run-backend-tests.sh admin
./run-backend-tests.sh unit

# 生成覆盖率报告
./run-backend-tests.sh coverage

# 查看帮助
./run-backend-tests.sh help
```

### 3. 或使用 pytest 直接运行

```bash
# 运行所有测试
pytest

# 运行特定文件
pytest tests/test_schemas.py

# 运行特定测试用例
pytest tests/test_schemas.py::TestVideoSchema::test_video_create_schema

# 使用标记运行
pytest -m unit                # 只运行单元测试
pytest -m "api and not slow"  # API 测试但跳过慢测试

# 并行运行（需要 pytest-xdist）
pytest -n auto

# 详细输出
pytest -vv

# 只显示失败
pytest -q

# 生成覆盖率
pytest --cov=app --cov-report=html
```

---

## 🏷️ 测试标记 (Markers)

使用标记来分类和选择性运行测试：

```python
@pytest.mark.unit
def test_simple_function():
    """单元测试"""
    pass

@pytest.mark.integration
@pytest.mark.requires_db
async def test_database_integration():
    """需要数据库的集成测试"""
    pass

@pytest.mark.api
@pytest.mark.admin
async def test_admin_endpoint():
    """Admin API 测试"""
    pass

@pytest.mark.slow
def test_long_running():
    """慢测试"""
    pass
```

**运行特定标记的测试：**
```bash
pytest -m unit              # 只运行单元测试
pytest -m "api and admin"   # API 和 Admin 测试
pytest -m "not slow"        # 跳过慢测试
```

---

## 🧪 Fixtures 使用指南

### 已有的 Fixtures（在 conftest.py 中）

#### 1. 数据库相关
```python
@pytest.fixture
async def test_user():
    """创建测试用户"""
    # 返回测试用户实例

@pytest.fixture
async def test_admin():
    """获取测试管理员"""
    # 返回管理员实例

@pytest.fixture
async def test_video():
    """创建测试视频"""
    # 返回视频实例

@pytest.fixture
async def test_category():
    """创建测试分类"""
    # 返回分类实例
```

#### 2. 认证相关
```python
@pytest.fixture
async def user_token(async_client, test_user):
    """获取用户 access token"""
    # 返回 JWT token

@pytest.fixture
async def admin_token(async_client):
    """获取管理员 access token"""
    # 返回管理员 JWT token
```

#### 3. HTTP 客户端
```python
@pytest.fixture
async def async_client():
    """创建异步 HTTP 客户端"""
    # 返回 AsyncClient 实例
```

### 使用示例

```python
@pytest.mark.asyncio
async def test_get_profile(async_client, user_token):
    """测试获取用户资料"""
    response = await async_client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "username" in data
```

---

## 📖 测试编写指南

### 1. Utils 函数测试

```python
"""
tests/utils/test_cache.py
测试缓存工具函数
"""
import pytest
from app.utils.cache import CacheManager

@pytest.mark.unit
@pytest.mark.requires_redis
@pytest.mark.asyncio
class TestCacheManager:
    """缓存管理器测试"""
    
    async def test_set_get(self):
        """测试设置和获取缓存"""
        cache = CacheManager()
        await cache.set("test_key", "test_value", ttl=60)
        value = await cache.get("test_key")
        assert value == "test_value"
    
    async def test_delete(self):
        """测试删除缓存"""
        cache = CacheManager()
        await cache.set("key", "value")
        await cache.delete("key")
        value = await cache.get("key")
        assert value is None
```

### 2. Admin API 测试

```python
"""
tests/admin/test_admin_videos.py
测试管理员视频管理 API
"""
import pytest
from httpx import AsyncClient

@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminVideosAPI:
    """管理员视频 API 测试"""
    
    async def test_list_videos(self, async_client, admin_token):
        """测试获取视频列表"""
        response = await async_client.get(
            "/api/v1/admin/videos",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
    
    async def test_create_video(self, async_client, admin_token):
        """测试创建视频"""
        video_data = {
            "title": "Test Video",
            "slug": "test-video",
            "video_type": "movie",
            "status": "draft"
        }
        response = await async_client.post(
            "/api/v1/admin/videos",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=video_data
        )
        assert response.status_code in [200, 201]
```

### 3. Model 测试

```python
"""
tests/models/test_video_models.py
测试视频相关模型
"""
import pytest
from sqlalchemy import select
from app.models.video import Video, VideoType, VideoStatus
from app.database import AsyncSessionLocal

@pytest.mark.model
@pytest.mark.requires_db
@pytest.mark.asyncio
class TestVideoModel:
    """Video 模型测试"""
    
    async def test_create_video(self):
        """测试创建视频"""
        async with AsyncSessionLocal() as db:
            video = Video(
                title="Test",
                slug="test",
                video_type=VideoType.MOVIE,
                status=VideoStatus.DRAFT
            )
            db.add(video)
            await db.commit()
            await db.refresh(video)
            
            assert video.id is not None
```

### 4. Middleware 测试

```python
"""
tests/middleware/test_request_id.py
测试请求 ID 中间件
"""
import pytest
from httpx import AsyncClient

@pytest.mark.middleware
@pytest.mark.asyncio
async def test_request_id_header(async_client):
    """测试请求 ID 头"""
    response = await async_client.get("/")
    assert "x-request-id" in response.headers
    assert len(response.headers["x-request-id"]) > 0
```

---

## 🔍 测试最佳实践

### 1. 测试命名
```python
# ✅ 好的命名
def test_user_can_login_with_valid_credentials():
    pass

def test_video_creation_fails_without_title():
    pass

# ❌ 差的命名
def test_1():
    pass

def test_user():
    pass
```

### 2. AAA 模式（Arrange-Act-Assert）
```python
async def test_create_comment():
    # Arrange - 准备测试数据
    user = await create_test_user()
    video = await create_test_video()
    comment_data = {"content": "Great!"}
    
    # Act - 执行操作
    response = await async_client.post("/comments", json=comment_data)
    
    # Assert - 验证结果
    assert response.status_code == 201
    assert response.json()["content"] == "Great!"
```

### 3. 使用参数化减少重复
```python
@pytest.mark.parametrize("status_code,email,password", [
    (401, "wrong@example.com", "password123"),
    (401, "test@example.com", "wrongpassword"),
    (422, "invalid-email", "password123"),
    (422, "test@example.com", "123"),  # 密码太短
])
async def test_login_failures(async_client, status_code, email, password):
    """测试登录失败场景"""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    assert response.status_code == status_code
```

### 4. 清理测试数据
```python
@pytest.fixture
async def test_video():
    """创建测试视频并在测试后清理"""
    async with AsyncSessionLocal() as db:
        video = Video(title="Test", slug="test")
        db.add(video)
        await db.commit()
        await db.refresh(video)
        
        yield video
        
        # 清理
        await db.delete(video)
        await db.commit()
```

---

## 📊 覆盖率报告

### 生成覆盖率报告

```bash
# HTML 报告（推荐）
pytest --cov=app --cov-report=html
# 查看: open htmlcov/index.html

# 终端报告
pytest --cov=app --cov-report=term-missing

# XML 报告（CI 用）
pytest --cov=app --cov-report=xml

# 多种格式
pytest --cov=app --cov-report=term --cov-report=html --cov-report=xml
```

### 查看覆盖率

```bash
# 浏览器打开 HTML 报告
firefox htmlcov/index.html

# 或
python -m http.server -d htmlcov 8080
# 访问 http://localhost:8080
```

---

## 🐛 调试测试

### 使用 pdb 调试

```python
def test_something():
    import pdb; pdb.set_trace()  # 设置断点
    # 测试代码...
```

或使用 pytest 的 `--pdb` 选项：
```bash
pytest --pdb  # 失败时进入调试器
pytest --pdb --maxfail=1  # 第一个失败时停止并调试
```

### 显示 print 输出

```bash
pytest -s  # 显示 print 输出
pytest -v -s  # 详细模式 + print 输出
```

### 只运行失败的测试

```bash
pytest --lf  # last failed
pytest --ff  # failed first
```

---

## 🔬 高级用法

### 1. 性能分析

```bash
# 显示最慢的 10 个测试
pytest --durations=10

# 使用 benchmark
pytest --benchmark-only
```

### 2. 并行测试

```bash
# 自动使用所有 CPU 核心
pytest -n auto

# 使用指定数量的进程
pytest -n 4
```

### 3. 测试覆盖率阈值

```bash
# 如果覆盖率低于 80% 则失败
pytest --cov=app --cov-fail-under=80
```

---

## 📝 测试检查清单

### 编写新测试前
- [ ] 确定测试类型（单元/集成/API）
- [ ] 添加适当的标记
- [ ] 准备必要的 fixtures
- [ ] 考虑边界条件

### 测试编写中
- [ ] 使用描述性的测试名称
- [ ] 遵循 AAA 模式
- [ ] 一个测试只测试一件事
- [ ] 添加必要的文档字符串

### 测试完成后
- [ ] 确保测试通过
- [ ] 检查覆盖率
- [ ] 清理测试数据
- [ ] 代码审查

---

## 🎯 当前测试状态

### ✅ 已完成
- Schemas 测试 (~280 行, ~80% 覆盖)
- Validators 测试 (~280 行, ~70% 覆盖)
- 基础 API 测试 (~320 行, ~40% 覆盖)
- 综合 API 测试 (~1000 行, ~30% 覆盖)

### ⏳ 进行中
查看 `BACKEND_TEST_PLAN.md` 了解详细计划

### ❌ 待补充
- Admin API 测试 (38 个端点)
- Utils 核心模块测试 (35+ 模块)
- Models 测试 (29 个模型)
- Middleware 测试 (9 个中间件)
- 集成测试
- 安全测试

---

## 📚 相关文档

- [BACKEND_TEST_PLAN.md](../BACKEND_TEST_PLAN.md) - 详细测试补全计划
- [TEST_COMPLETION_SUMMARY.md](../../TEST_COMPLETION_SUMMARY.md) - 整体测试总结
- [pytest.ini](../pytest.ini) - Pytest 配置
- [conftest.py](./conftest.py) - 共享 fixtures

---

## 💡 提示

1. **先写测试** - TDD 方法可以帮助你设计更好的 API
2. **保持测试独立** - 测试之间不应该有依赖
3. **使用 fixtures** - 减少重复代码
4. **测试失败场景** - 不要只测试成功路径
5. **持续运行** - 使用 `pytest --watch` 在开发时持续运行测试

---

**🚀 开始测试之旅吧！每个测试都让代码更可靠！**

