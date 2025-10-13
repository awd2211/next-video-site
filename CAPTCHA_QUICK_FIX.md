# 验证码加载问题 - 快速解决方案

## 🔍 问题

前端管理后台登录页面的验证码无法加载。

---

## ✅ 快速诊断

运行诊断脚本：

```bash
cd /home/eric/video
./captcha_diagnose.sh
```

---

## 🚀 快速修复（最常见）

### 问题：后端服务未运行

**症状**：
- 验证码显示"加载中..."或空白
- 浏览器控制台显示 `ERR_CONNECTION_REFUSED` 或 `Failed to connect`

**解决方案**：

```bash
# 打开终端 1 - 启动后端
cd /home/eric/video/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**预期输出**：
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
Slow query monitoring enabled
Storage monitoring started
```

**验证**：
访问 http://localhost:8000/api/docs，应该看到 API 文档页面。

---

### 问题：Redis 未运行

**症状**：
- 后端运行正常
- 验证码API返回 500 错误
- 后端日志显示 Redis 连接错误

**解决方案**：

```bash
# 方法1：如果使用 Docker
cd /home/eric/video
docker-compose -f docker-compose.dev.yml up -d redis

# 方法2：如果使用系统 Redis
sudo systemctl start redis

# 验证 Redis 运行
redis-cli ping
# 应该返回 PONG
```

---

### 问题：前端服务未运行

**症状**：
- 无法访问 http://localhost:3001
- 登录页面不显示

**解决方案**：

```bash
# 打开终端 2 - 启动前端
cd /home/eric/video/admin-frontend
pnpm run dev
```

**预期输出**：
```
VITE v5.4.20  ready in XXX ms

  ➜  Local:   http://localhost:3001/
  ➜  Network: use --host to expose
```

---

## 📋 完整启动流程

在三个独立的终端中分别执行：

### 终端 1: 基础设施（可选，如果使用 Docker）

```bash
cd /home/eric/video
docker-compose -f docker-compose.dev.yml up -d postgres redis minio
```

### 终端 2: 后端服务

```bash
cd /home/eric/video/backend
source venv/bin/activate

# 首次运行或数据库结构有变化时
alembic upgrade head

# 启动后端
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 终端 3: 前端服务

```bash
cd /home/eric/video/admin-frontend
pnpm run dev
```

---

## ✔️ 验证系统正常

### 1. 检查后端

访问：http://localhost:8000/api/docs

应该看到 Swagger API 文档界面。

### 2. 测试验证码API

```bash
curl -I http://localhost:8000/api/v1/captcha/
```

应该看到：
```
HTTP/1.1 200 OK
content-type: image/png
x-captcha-id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### 3. 检查前端

访问：http://localhost:3001/login

应该看到：
- ✅ 登录表单正常显示
- ✅ 验证码图片正常加载
- ✅ 点击验证码可以刷新

---

## 🐛 如果问题仍然存在

### 1. 查看浏览器控制台

按 `F12` 打开开发者工具：

**Console 标签**：
- 查看是否有 JavaScript 错误
- 查看是否有 `Captcha load error` 日志

**Network 标签**：
- 查找 `/api/v1/captcha/` 请求
- 检查状态码和响应
- 查看请求耗时

### 2. 查看后端日志

后端终端应该显示请求日志：
```
INFO:     127.0.0.1:xxxxx - "GET /api/v1/captcha/ HTTP/1.1" 200 OK
```

如果看到错误，检查：
- Redis 连接
- Python 依赖是否完整
- 磁盘空间

### 3. 清除浏览器缓存

有时浏览器缓存会导致问题：

- **Chrome/Edge**: `Ctrl + Shift + Delete`
- **Firefox**: `Ctrl + Shift + Delete`
- 或使用无痕模式测试

### 4. 检查防火墙

确保端口未被阻止：
```bash
# 检查端口是否被占用
sudo netstat -tlnp | grep :8000
sudo netstat -tlnp | grep :3001
```

---

## 📚 详细文档

如需更详细的诊断和解决方案，请查看：

- **[CAPTCHA_TROUBLESHOOTING.md](CAPTCHA_TROUBLESHOOTING.md)** - 完整故障排除指南
- **[CLAUDE.md](CLAUDE.md)** - 项目开发指南
- **[README.md](README.md)** - 项目概览

---

## 🆘 常见错误信息

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `ERR_CONNECTION_REFUSED` | 后端未运行 | 启动后端服务 |
| `404 Not Found` | 路由配置错误 | 检查 main.py 路由注册 |
| `500 Internal Server Error` | Redis连接失败 | 启动 Redis |
| `CORS policy` | 跨域配置错误 | 检查 CORS 或使用 Vite 代理 |
| `验证码加载超时` | 网络或性能问题 | 检查 Redis 性能 |
| 空白图片 | Blob处理错误 | 检查浏览器控制台 |

---

## 💡 提示

1. **始终先启动后端，再启动前端**
2. **确保 Redis 正在运行**（验证码存储在 Redis）
3. **使用诊断脚本快速定位问题**
4. **查看终端日志和浏览器控制台**

---

**更新日期**: 2025-10-13
**问题状态**: ✅ 已识别 - 后端服务未运行
**解决方案**: ✅ 启动后端服务即可解决
