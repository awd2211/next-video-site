# 🧪 API 测试指南

本项目提供多种专业的 API 测试方法和工具。

## 📋 目录

1. [Pytest + HTTPX (推荐)](#1-pytest--httpx-推荐)
2. [Postman/Newman](#2-postmannewman)
3. [Swagger UI (交互式)](#3-swagger-ui-交互式)
4. [cURL 脚本](#4-curl-脚本)
5. [负载测试](#5-负载测试)

---

## 1. Pytest + HTTPX (推荐) ⭐

**最专业的测试方式** - FastAPI 官方推荐

### 安装依赖

```bash
cd backend
pip install pytest pytest-asyncio httpx
```

### 运行测试

```bash
# 运行所有测试
PYTHONPATH=. pytest tests/ -v

# 运行特定测试文件
PYTHONPATH=. pytest tests/test_api_endpoints.py -v

# 显示详细输出
PYTHONPATH=. pytest tests/ -v -s

# 生成覆盖率报告
PYTHONPATH=. pytest tests/ --cov=app --cov-report=html

# 只运行失败的测试
PYTHONPATH=. pytest tests/ --lf

# 并行运行（需要 pytest-xdist）
PYTHONPATH=. pytest tests/ -n auto
```

### 测试文件示例

```python
# tests/test_videos_api.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_get_videos():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/videos")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
```

---

## 2. Postman/Newman

**图形化 + 自动化测试**

### 导出 OpenAPI 规范

```bash
# 访问
http://localhost:8000/api/openapi.json

# 或使用curl
curl http://localhost:8000/api/openapi.json > openapi.json
```

### 导入 Postman

1. 打开 Postman
2. File → Import → openapi.json
3. 自动生成所有 API 请求

### Newman 命令行测试

```bash
# 安装Newman
npm install -g newman

# 运行测试集合
newman run postman_collection.json -e postman_environment.json

# 生成HTML报告
newman run postman_collection.json --reporters html,cli
```

---

## 3. Swagger UI (交互式) 🚀

**最直观的测试方式** - 无需编程

### 访问地址

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

### 使用步骤

1. 打开 http://localhost:8000/api/docs
2. 点击 "Authorize" 按钮
3. 输入 token（格式：`Bearer <your_token>`）
4. 展开任意端点
5. 点击 "Try it out"
6. 填写参数
7. 点击 "Execute"
8. 查看响应

### 获取 Token（用于 Authorize）

**普通用户：**

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123456"}' | jq -r '.access_token'
```

**管理员：**
需要验证码，建议通过前端登录后从浏览器 DevTools 复制 token

---

## 4. cURL 脚本

**快速脚本测试**

### 创建测试脚本

```bash
#!/bin/bash
# test_apis.sh

BASE_URL="http://localhost:8000"

# 获取token
TOKEN=$(curl -s -X POST $BASE_URL/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123456"}' | jq -r '.access_token')

echo "Token: $TOKEN"

# 测试公开API
echo "\n测试视频列表..."
curl -s $BASE_URL/api/v1/videos | jq '.total'

# 测试需要认证的API
echo "\n测试用户信息..."
curl -s $BASE_URL/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN" | jq '.username'

echo "\n测试收藏列表..."
curl -s $BASE_URL/api/v1/favorites/ \
  -H "Authorization: Bearer $TOKEN" | jq '.total'
```

```bash
chmod +x test_apis.sh
./test_apis.sh
```

---

## 5. 负载测试

### 使用 Locust

```bash
# 安装
pip install locust

# 创建locustfile.py
# 运行
locust -f locustfile.py --host=http://localhost:8000
```

### 使用 k6

```bash
# 安装k6
# macOS: brew install k6
# Linux: 见 https://k6.io/docs/getting-started/installation/

# 运行负载测试
k6 run load_test.js

# 100个虚拟用户，持续30秒
k6 run --vus 100 --duration 30s load_test.js
```

---

## 📊 推荐的测试策略

### 开发阶段

1. **Swagger UI** - 快速手动测试
2. **pytest** - 编写单元测试和集成测试
3. **cURL** - 快速脚本验证

### CI/CD 阶段

1. **pytest** - 自动化测试
2. **Newman** - API 集合测试
3. **覆盖率检查** - 确保>=80%

### 上线前

1. **负载测试** - Locust 或 k6
2. **安全测试** - OWASP ZAP
3. **性能测试** - Apache JMeter

---

## 🎯 快速开始

### 方案 A：使用 Swagger UI (最简单) ⭐

```bash
# 1. 确保后端运行
make backend-run

# 2. 打开浏览器
open http://localhost:8000/api/docs

# 3. 点击任意端点的 "Try it out" 测试
```

### 方案 B：使用 pytest (最专业) ⭐⭐⭐

```bash
# 1. 运行现有测试
cd backend
PYTHONPATH=. pytest tests/ -v

# 2. 添加新测试
# 编辑 tests/test_api_endpoints.py

# 3. 重新运行
PYTHONPATH=. pytest tests/ -v
```

### 方案 C：使用自动化脚本 (最快速)

```bash
# 运行提供的测试脚本
cd backend
python test_all_apis.py
```

---

## 📝 测试检查清单

- [ ] 所有公开 API（无认证）正常响应
- [ ] 用户登录和 token 刷新正常
- [ ] 管理员登录和验证码正常
- [ ] CRUD 操作完整（创建、读取、更新、删除）
- [ ] 分页参数正常（page, page_size, total, pages）
- [ ] 错误处理正确（400, 401, 403, 404, 422, 500）
- [ ] 响应 schema 符合定义
- [ ] 数据验证正确（Pydantic）
- [ ] 权限检查生效
- [ ] 限流（rate limiting）生效

---

## 🔧 常用测试命令

```bash
# 测试单个端点
curl http://localhost:8000/api/v1/videos | jq

# 测试带参数
curl "http://localhost:8000/api/v1/videos?page=1&page_size=10" | jq

# 测试POST
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123456"}' | jq

# 测试带认证
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_TOKEN" | jq

# 健康检查
curl http://localhost:8000/health

# 查看所有路由
curl http://localhost:8000/api/openapi.json | jq '.paths | keys'
```

---

## 📚 相关资源

- [FastAPI Testing Documentation](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest Documentation](https://docs.pytest.org/)
- [Postman API Testing](https://www.postman.com/api-platform/api-testing/)
- [httpx Documentation](https://www.python-httpx.org/)

---

**当前项目状态：**

- ✅ 后端: 216 个 API 端点
- ✅ Swagger UI: 已启用
- ✅ 测试框架: pytest 已配置
- ✅ 自动化脚本: 已提供
