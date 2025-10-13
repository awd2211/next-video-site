# AI管理模块部署说明

## 部署步骤

### 1. 后端部署

#### 安装依赖
```bash
cd /home/eric/video/backend
source venv/bin/activate
pip install openai==1.70.0 google-generativeai==0.8.4
```

#### 验证数据库表
数据库表 `ai_providers` 已创建。验证:
```bash
docker exec -i videosite_postgres psql -U postgres -d videosite -c "\d ai_providers"
```

#### 重启后端服务
```bash
# 停止当前运行的后端
pkill -f "uvicorn app.main:app"

# 启动后端
cd /home/eric/video/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

或者使用make命令:
```bash
cd /home/eric/video
make backend-run
```

### 2. 前端部署

#### 安装依赖
```bash
cd /home/eric/video/admin-frontend
pnpm add react-markdown
```

#### 重启前端服务
```bash
# 如果需要,停止当前前端
pkill -f "vite"

# 启动前端
cd /home/eric/video/admin-frontend
pnpm run dev
```

或者使用make命令:
```bash
cd /home/eric/video
make admin-run
```

## 验证部署

### 1. 验证后端API

#### 检查API文档
访问: http://localhost:8000/api/docs

在Swagger文档中应该能看到"Admin - AI Management"标签下的所有端点:
- GET `/api/v1/admin/ai/providers`
- POST `/api/v1/admin/ai/providers`
- PUT `/api/v1/admin/ai/providers/{provider_id}`
- DELETE `/api/v1/admin/ai/providers/{provider_id}`
- POST `/api/v1/admin/ai/providers/{provider_id}/test`
- POST `/api/v1/admin/ai/chat`
- GET `/api/v1/admin/ai/models/{provider_type}`
- GET `/api/v1/admin/ai/usage`

#### 测试API端点
```bash
# 获取所有AI提供商(需要admin token)
curl -X GET "http://localhost:8000/api/v1/admin/ai/providers" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# 获取OpenAI可用模型
curl -X GET "http://localhost:8000/api/v1/admin/ai/models/openai" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### 2. 验证前端页面

#### 访问AI管理页面
1. 打开浏览器访问: http://localhost:3001
2. 使用管理员账号登录
3. 在左侧菜单的"系统"分组中找到"AI管理"
4. 点击应该能看到AI管理页面

#### 验证功能
- [ ] 页面正常加载
- [ ] 可以看到三个标签页: OpenAI, Grok, Google AI
- [ ] 顶部有使用统计卡片
- [ ] "添加提供商"按钮可点击
- [ ] 表格正常显示(即使没有数据)

### 3. 端到端测试

#### 创建测试提供商
1. 点击"添加提供商"
2. 填写测试数据:
   ```
   名称: Test OpenAI
   提供商类型: OpenAI
   描述: 测试配置
   API密钥: sk-test123456789 (测试密钥)
   模型: GPT-3.5 Turbo
   ```
3. 点击"创建"

#### 验证数据持久化
```bash
# 在数据库中查看创建的记录
docker exec -i videosite_postgres psql -U postgres -d videosite -c \
  "SELECT id, name, provider_type, model_name, enabled FROM ai_providers;"
```

## 故障排查

### 后端问题

#### API端点404
**症状**: 访问 `/api/v1/admin/ai/*` 返回404
**解决方案**:
```bash
# 1. 确认路由已注册
cd /home/eric/video/backend
grep -n "admin_ai" app/main.py

# 2. 检查导入
grep -n "import.*ai_management" app/main.py

# 3. 重启后端
pkill -f "uvicorn app.main:app"
cd /home/eric/video/backend && source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 数据库表不存在
**症状**: 查询时报错 "relation 'ai_providers' does not exist"
**解决方案**:
```bash
# 手动创建表
docker exec -i videosite_postgres psql -U postgres -d videosite << 'EOF'
-- 创建枚举类型(如果不存在)
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'aiprovidertype') THEN
        CREATE TYPE aiprovidertype AS ENUM ('openai', 'grok', 'google');
    END IF;
END $$;

-- 创建表
CREATE TABLE IF NOT EXISTS ai_providers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    provider_type aiprovidertype NOT NULL,
    description TEXT,
    api_key VARCHAR(500) NOT NULL,
    base_url VARCHAR(500),
    model_name VARCHAR(100) NOT NULL,
    max_tokens INTEGER DEFAULT 2048,
    temperature FLOAT DEFAULT 0.7,
    top_p FLOAT DEFAULT 1.0,
    frequency_penalty FLOAT DEFAULT 0.0,
    presence_penalty FLOAT DEFAULT 0.0,
    settings JSON DEFAULT '{}',
    enabled BOOLEAN DEFAULT TRUE NOT NULL,
    is_default BOOLEAN DEFAULT FALSE NOT NULL,
    total_requests INTEGER DEFAULT 0 NOT NULL,
    total_tokens INTEGER DEFAULT 0 NOT NULL,
    last_used_at TIMESTAMP,
    last_test_at TIMESTAMP,
    last_test_status VARCHAR(20),
    last_test_message TEXT,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL
);

-- 创建索引
CREATE INDEX IF NOT EXISTS ix_ai_providers_id ON ai_providers(id);
CREATE INDEX IF NOT EXISTS ix_ai_providers_provider_type ON ai_providers(provider_type);
CREATE INDEX IF NOT EXISTS ix_ai_providers_enabled ON ai_providers(enabled);

SELECT 'Table created successfully!' as result;
EOF
```

#### 依赖包未安装
**症状**: 导入错误 "No module named 'openai'" 或 "No module named 'google.generativeai'"
**解决方案**:
```bash
cd /home/eric/video/backend
source venv/bin/activate
pip install openai==1.70.0 google-generativeai==0.8.4
```

### 前端问题

#### 页面空白或报错
**症状**: AI管理页面无法加载
**解决方案**:
```bash
# 1. 检查react-markdown是否安装
cd /home/eric/video/admin-frontend
pnpm list react-markdown

# 2. 如果未安装,安装它
pnpm add react-markdown

# 3. 重启前端
pkill -f "vite"
pnpm run dev
```

#### 菜单中没有AI管理选项
**症状**: 左侧菜单的"系统"分组中看不到"AI管理"
**解决方案**:
```bash
# 1. 确认翻译已添加
cd /home/eric/video/admin-frontend
grep -n "aiManagement" src/i18n/locales/en-US.json
grep -n "aiManagement" src/i18n/locales/zh-CN.json

# 2. 确认路由已添加
grep -n "AIManagement" src/App.tsx
grep -n "ai-management" src/App.tsx

# 3. 确认菜单已添加
grep -n "aiManagement" src/layouts/AdminLayout.tsx

# 4. 清除缓存并重启
rm -rf node_modules/.vite
pnpm run dev
```

#### API请求失败
**症状**: 前端报错 "Network Error" 或 "Request failed"
**解决方案**:
```bash
# 1. 确认后端正在运行
curl http://localhost:8000/api/docs

# 2. 确认axios配置正确
cat admin-frontend/src/utils/axios.ts

# 3. 检查浏览器控制台的网络请求
# 打开浏览器开发者工具 -> Network标签
# 查看失败的请求详情
```

## 生产环境部署

### 环境变量配置

在 `backend/.env` 中添加(可选):
```bash
# AI相关配置(可选,如果需要在环境变量中配置默认值)
DEFAULT_OPENAI_KEY=sk-your-openai-key
DEFAULT_GROK_KEY=xai-your-grok-key
DEFAULT_GOOGLE_KEY=AIza-your-google-key
```

### 安全建议

1. **API密钥管理**
   - 使用密钥管理服务(如AWS Secrets Manager, HashiCorp Vault)
   - 定期轮换API密钥
   - 限制API密钥的权限

2. **访问控制**
   - 确保只有管理员可以访问AI管理页面
   - 实施IP白名单(如果需要)
   - 启用审计日志

3. **速率限制**
   - 在AI端点上配置速率限制
   - 监控异常的API使用模式
   - 设置预算告警

### 监控和日志

查看AI相关日志:
```bash
# 后端日志
cd /home/eric/video/backend
tail -f logs/app.log | grep -i "ai"

# 或查看uvicorn输出
# 查看运行uvicorn的终端
```

## 回滚计划

如果需要回滚AI管理模块:

### 1. 删除数据库表
```bash
docker exec -i videosite_postgres psql -U postgres -d videosite << 'EOF'
DROP TABLE IF EXISTS ai_providers;
DROP TYPE IF EXISTS aiprovidertype;
EOF
```

### 2. 移除后端代码
```bash
cd /home/eric/video/backend

# 删除模型
rm app/models/ai_config.py

# 删除schemas
rm app/schemas/ai.py

# 删除管理端点
rm app/admin/ai_management.py

# 删除服务层
rm app/utils/ai_service.py

# 从main.py移除导入和路由
# 手动编辑 app/main.py,删除相关行
```

### 3. 移除前端代码
```bash
cd /home/eric/video/admin-frontend

# 删除页面
rm -rf src/pages/AIManagement

# 删除服务
rm src/services/aiManagement.ts

# 从路由中移除
# 手动编辑 src/App.tsx

# 从菜单中移除
# 手动编辑 src/layouts/AdminLayout.tsx

# 从翻译中移除
# 手动编辑 src/i18n/locales/en-US.json 和 zh-CN.json
```

### 4. 卸载依赖
```bash
# 后端
cd /home/eric/video/backend
source venv/bin/activate
pip uninstall openai google-generativeai -y

# 前端
cd /home/eric/video/admin-frontend
pnpm remove react-markdown
```

## 性能优化

### 缓存策略
AI提供商配置会被缓存30分钟,如需修改缓存时间:
```python
# backend/app/admin/ai_management.py
# 找到 @router.get("/providers") 端点
# 修改: await Cache.set(cache_key, response.model_dump(), ttl=1800)
# ttl以秒为单位
```

### 数据库索引
已创建的索引:
- `ix_ai_providers_id` - 主键索引
- `ix_ai_providers_provider_type` - 提供商类型索引
- `ix_ai_providers_enabled` - 启用状态索引

如需添加更多索引:
```sql
CREATE INDEX ix_ai_providers_created_at ON ai_providers(created_at DESC);
CREATE INDEX ix_ai_providers_total_requests ON ai_providers(total_requests DESC);
```

## 联系支持

如有问题:
1. 查看本文档的故障排查部分
2. 查看后端日志和前端控制台
3. 检查API文档: http://localhost:8000/api/docs
4. 查看使用指南: [AI_MANAGEMENT_GUIDE.md](./AI_MANAGEMENT_GUIDE.md)

---

**部署完成后,请访问 http://localhost:3001 体验AI管理功能!**
