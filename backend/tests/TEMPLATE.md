# 测试模板

## 📋 各种测试的模板代码

### 1. Utils 函数测试模板

```python
"""
测试 app/utils/example.py
"""
import pytest
from app.utils.example import function_to_test

@pytest.mark.unit
class TestExampleUtils:
    """Example 工具函数测试"""
    
    def test_basic_functionality(self):
        """测试基本功能"""
        result = function_to_test("input")
        assert result == "expected_output"
    
    def test_edge_case_empty_input(self):
        """测试边界情况 - 空输入"""
        result = function_to_test("")
        assert result is None
    
    def test_error_handling(self):
        """测试错误处理"""
        with pytest.raises(ValueError):
            function_to_test(None)
    
    @pytest.mark.parametrize("input,expected", [
        ("input1", "output1"),
        ("input2", "output2"),
        ("input3", "output3"),
    ])
    def test_multiple_inputs(self, input, expected):
        """测试多种输入"""
        assert function_to_test(input) == expected
```

---

### 2. Admin API 测试模板

```python
"""
测试 app/admin/example.py
"""
import pytest
from httpx import AsyncClient

@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminExampleAPI:
    """Admin Example API 测试"""
    
    async def test_list_items_success(
        self, 
        async_client: AsyncClient, 
        admin_token: str
    ):
        """测试获取列表 - 成功"""
        response = await async_client.get(
            "/api/v1/admin/example",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
    
    async def test_create_item_success(
        self, 
        async_client: AsyncClient, 
        admin_token: str
    ):
        """测试创建项目 - 成功"""
        item_data = {
            "name": "Test Item",
            "description": "Test Description"
        }
        response = await async_client.post(
            "/api/v1/admin/example",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=item_data
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["name"] == "Test Item"
    
    async def test_update_item(
        self, 
        async_client: AsyncClient, 
        admin_token: str
    ):
        """测试更新项目"""
        update_data = {"name": "Updated Name"}
        response = await async_client.put(
            "/api/v1/admin/example/1",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=update_data
        )
        assert response.status_code == 200
    
    async def test_delete_item(
        self, 
        async_client: AsyncClient, 
        admin_token: str
    ):
        """测试删除项目"""
        response = await async_client.delete(
            "/api/v1/admin/example/1",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 204]
    
    async def test_unauthorized_access(self, async_client: AsyncClient):
        """测试未授权访问"""
        response = await async_client.get("/api/v1/admin/example")
        assert response.status_code in [401, 403]
    
    async def test_non_admin_access(
        self, 
        async_client: AsyncClient, 
        user_token: str
    ):
        """测试普通用户访问管理员 API"""
        response = await async_client.get(
            "/api/v1/admin/example",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 403
    
    async def test_validation_error(
        self, 
        async_client: AsyncClient, 
        admin_token: str
    ):
        """测试验证错误"""
        invalid_data = {"invalid_field": "value"}
        response = await async_client.post(
            "/api/v1/admin/example",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=invalid_data
        )
        assert response.status_code == 422
```

---

### 3. Model 测试模板

```python
"""
测试 app/models/example.py
"""
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.example import ExampleModel
from app.database import AsyncSessionLocal

@pytest.mark.model
@pytest.mark.requires_db
@pytest.mark.asyncio
class TestExampleModel:
    """Example 模型测试"""
    
    async def test_create_instance(self):
        """测试创建实例"""
        async with AsyncSessionLocal() as db:
            instance = ExampleModel(
                name="Test",
                value="123"
            )
            db.add(instance)
            await db.commit()
            await db.refresh(instance)
            
            assert instance.id is not None
            assert instance.name == "Test"
    
    async def test_unique_constraint(self):
        """测试唯一性约束"""
        async with AsyncSessionLocal() as db:
            # 创建第一个实例
            instance1 = ExampleModel(name="unique", value="1")
            db.add(instance1)
            await db.commit()
            
            # 尝试创建重复的实例
            instance2 = ExampleModel(name="unique", value="2")
            db.add(instance2)
            
            with pytest.raises(IntegrityError):
                await db.commit()
    
    async def test_relationship(self):
        """测试模型关系"""
        async with AsyncSessionLocal() as db:
            # 测试关联关系
            parent = ParentModel(name="Parent")
            child = ChildModel(name="Child", parent=parent)
            
            db.add(parent)
            db.add(child)
            await db.commit()
            await db.refresh(child)
            
            assert child.parent_id == parent.id
            assert child.parent.name == "Parent"
    
    async def test_cascade_delete(self):
        """测试级联删除"""
        async with AsyncSessionLocal() as db:
            parent = ParentModel(name="Parent")
            child = ChildModel(name="Child", parent=parent)
            
            db.add(parent)
            db.add(child)
            await db.commit()
            
            # 删除父对象
            await db.delete(parent)
            await db.commit()
            
            # 检查子对象是否也被删除
            result = await db.execute(
                select(ChildModel).where(ChildModel.id == child.id)
            )
            assert result.scalar_one_or_none() is None
```

---

### 4. Middleware 测试模板

```python
"""
测试 app/middleware/example.py
"""
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.middleware
@pytest.mark.asyncio
class TestExampleMiddleware:
    """Example 中间件测试"""
    
    async def test_middleware_processes_request(self, async_client):
        """测试中间件处理请求"""
        response = await async_client.get("/test")
        
        # 检查中间件是否添加了预期的头
        assert "x-custom-header" in response.headers
    
    async def test_middleware_modifies_response(self, async_client):
        """测试中间件修改响应"""
        response = await async_client.get("/test")
        
        # 检查响应是否被中间件修改
        assert response.headers["x-processed"] == "true"
    
    async def test_middleware_handles_errors(self, async_client):
        """测试中间件错误处理"""
        response = await async_client.get("/error-endpoint")
        
        # 中间件应该优雅地处理错误
        assert response.status_code in [500, 502, 503]
```

---

### 5. 集成测试模板

```python
"""
测试完整用户流程
"""
import pytest
from httpx import AsyncClient

@pytest.mark.integration
@pytest.mark.requires_db
@pytest.mark.asyncio
class TestUserWorkflow:
    """用户完整流程集成测试"""
    
    async def test_user_registration_and_login_flow(
        self, 
        async_client: AsyncClient
    ):
        """测试：注册 → 登录 → 获取资料 → 更新资料"""
        
        # 1. 注册
        register_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123",
            "full_name": "New User"
        }
        register_response = await async_client.post(
            "/api/v1/auth/register",
            json=register_data
        )
        assert register_response.status_code in [200, 201]
        
        # 2. 登录
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={
                "email": "newuser@example.com",
                "password": "password123"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # 3. 获取资料
        profile_response = await async_client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert profile_response.status_code == 200
        assert profile_response.json()["email"] == "newuser@example.com"
        
        # 4. 更新资料
        update_response = await async_client.put(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"full_name": "Updated Name"}
        )
        assert update_response.status_code == 200
        assert update_response.json()["full_name"] == "Updated Name"
```

---

## 🔒 安全测试模板

```python
"""
测试 SQL 注入防护
"""
import pytest
from httpx import AsyncClient

@pytest.mark.security
@pytest.mark.asyncio
class TestSQLInjectionPrevention:
    """SQL 注入防护测试"""
    
    async def test_search_sql_injection(self, async_client):
        """测试搜索接口的 SQL 注入防护"""
        malicious_queries = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users--"
        ]
        
        for query in malicious_queries:
            response = await async_client.get(
                f"/api/v1/search?q={query}"
            )
            # 应该安全处理，不应该返回 500
            assert response.status_code in [200, 400, 422]
            
            # 响应不应该包含敏感信息
            if response.status_code == 200:
                data = response.json()
                # 验证没有执行恶意查询
                assert "items" in data
```

---

## 🎓 学习资源

### 推荐阅读
1. [Pytest 官方文档](https://docs.pytest.org/)
2. [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
3. [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html)
4. [Python Testing Best Practices](https://testdriven.io/blog/testing-best-practices/)

### 示例项目
- [Full Stack FastAPI Template](https://github.com/tiangolo/full-stack-fastapi-template)
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)

---

**🎯 选择一个模板，开始编写你的第一个测试！**

