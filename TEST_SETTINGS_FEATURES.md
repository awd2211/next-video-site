# Settings Enhancement 功能测试指南

## 快速测试清单

### 前置条件
- ✅ 后端运行在 http://localhost:8000
- ✅ 前端运行在 http://localhost:3001
- ✅ 数据库迁移已应用
- ✅ 有管理员账号可登录

---

## 测试步骤

### 1. 访问设置页面

```bash
# 访问管理后台
浏览器打开: http://localhost:3001

# 登录管理员账号
用户名: admin
密码: admin123（或您的管理员密码）

# 导航到设置页面
点击侧边栏 "设置" / "Settings"
```

---

### 2. 测试 SMTP 邮件功能 📧

**位置**: 设置页面 > 邮件服务配置（Email Services）面板

**步骤**:
1. 向下滚动到"邮件服务配置"面板
2. 点击"发送测试邮件"按钮
3. 在弹出的模态框中输入测试邮箱地址
4. 点击"发送测试"按钮

**预期结果**:
- ✅ 如果SMTP已配置：显示"测试邮件发送成功"提示
- ✅ 如果SMTP未配置：显示错误提示（需要先配置SMTP）
- ✅ 测试状态和时间会保存到数据库

**数据库验证**:
```bash
docker exec -i videosite_postgres psql -U postgres -d videosite -c \
  "SELECT smtp_test_email, smtp_last_test_at, smtp_last_test_status FROM system_settings;"
```

---

### 3. 测试缓存管理功能 🗄️

**位置**: 设置页面 > 缓存管理（Cache Management）面板

#### 3.1 查看缓存统计

**步骤**:
1. 找到"缓存管理"面板（Panel 6）
2. 点击"查看统计"按钮

**预期结果**:
- ✅ 弹出缓存统计模态框
- ✅ 显示总命中数、总未命中数
- ✅ 显示平均命中率（百分比）
- ✅ 显示最近7天的详细统计

#### 3.2 清除特定缓存

**步骤**:
1. 在缓存管理面板中
2. 点击以下任一按钮：
   - "清除视频缓存"
   - "清除分类缓存"
   - "清除用户缓存"
   - "清除系统设置缓存"

**预期结果**:
- ✅ 显示成功提示消息
- ✅ 对应缓存被清除
- ✅ 下次访问时会重新加载数据

#### 3.3 清除所有缓存

**步骤**:
1. 点击"清除所有缓存"按钮
2. 在确认对话框中点击"确定"

**预期结果**:
- ✅ 显示确认对话框
- ✅ 确认后显示成功提示
- ✅ 所有缓存被清空

**API测试**（需要admin token）:
```bash
# 获取缓存统计
curl -X GET "http://localhost:8000/api/v1/admin/system/cache/stats" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# 清除特定缓存
curl -X POST "http://localhost:8000/api/v1/admin/system/cache/clear" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"patterns": ["video:*"]}'

# 清除所有缓存
curl -X POST "http://localhost:8000/api/v1/admin/system/cache/clear" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"patterns": ["*"]}'
```

---

### 4. 测试配置备份/恢复功能 💾

**位置**: 设置页面 > 备份恢复（Backup & Restore）面板

#### 4.1 导出配置备份

**步骤**:
1. 找到"备份恢复"面板（Panel 7）
2. 点击"导出备份"按钮

**预期结果**:
- ✅ 自动下载JSON文件
- ✅ 文件名格式: `settings_backup_YYYYMMDD_HHMMSS.json`
- ✅ 文件包含所有系统配置

**验证备份文件**:
```bash
# 查看下载的JSON文件
cat ~/Downloads/settings_backup_*.json | python -m json.tool | head -50
```

预期JSON结构:
```json
{
  "settings": {
    "id": 1,
    "site_name": "VideoSite",
    "site_url": "http://localhost:3000",
    "upload_max_size": 524288000,
    "maintenance_mode": false,
    ...
  },
  "backup_time": "2025-10-13T13:45:00Z",
  "version": "1.0"
}
```

#### 4.2 恢复配置

**步骤**:
1. 在"备份恢复"面板中
2. 点击"导入备份"按钮
3. 选择之前导出的JSON文件
4. 在确认对话框中点击"确定"

**预期结果**:
- ✅ 显示确认对话框（警告会覆盖当前配置）
- ✅ 上传成功后显示成功提示
- ✅ 配置被恢复到备份时的状态
- ✅ 页面自动刷新显示新配置

**测试场景**:
```
1. 导出备份 A
2. 修改某些设置（如站点名称）
3. 导出备份 B
4. 恢复备份 A
5. 验证站点名称恢复到备份 A 的值
```

---

### 5. 测试已存在的功能

#### 5.1 维护模式 🔧

**位置**: 运营管理（Operations）面板

**步骤**:
1. 找到"维护模式"开关
2. 切换开关状态
3. 在前端用户界面查看效果

**预期结果**:
- ✅ 开关状态正确保存
- ✅ 启用时前端显示维护页面
- ✅ 关闭时前端正常访问

#### 5.2 文件上传限制 📁

**位置**: 上传配置（Upload Settings）面板

**步骤**:
1. 查看"最大文件大小"设置
2. 查看"允许的文件格式"设置
3. 修改并保存

**预期结果**:
- ✅ 设置正确显示和保存
- ✅ 上传文件时遵循限制

---

## API端点完整测试

### 准备工作：获取 Admin Token

```bash
# 登录获取token
curl -X POST "http://localhost:8000/api/v1/auth/admin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'

# 保存返回的access_token
export ADMIN_TOKEN="eyJ..."
```

### 测试所有新端点

```bash
# 1. 发送测试邮件
curl -X POST "http://localhost:8000/api/v1/admin/system/settings/test-email" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "test@example.com"
  }'

# 2. 获取缓存统计
curl -X GET "http://localhost:8000/api/v1/admin/system/cache/stats" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# 3. 清除缓存
curl -X POST "http://localhost:8000/api/v1/admin/system/cache/clear" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patterns": ["video:*", "category:*"]
  }'

# 4. 导出配置
curl -X GET "http://localhost:8000/api/v1/admin/system/settings/backup" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -o settings_backup.json

# 5. 恢复配置
curl -X POST "http://localhost:8000/api/v1/admin/system/settings/restore" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d @settings_backup.json
```

---

## 数据库验证

### 检查新字段

```bash
# 查看表结构
docker exec -i videosite_postgres psql -U postgres -d videosite -c "\d system_settings"

# 查看新字段的数据
docker exec -i videosite_postgres psql -U postgres -d videosite -c "
SELECT
  id,
  smtp_test_email,
  smtp_last_test_at,
  smtp_last_test_status,
  rate_limit_config,
  cache_config
FROM system_settings;
"
```

### 预期输出

```
 id | smtp_test_email | smtp_last_test_at | smtp_last_test_status | rate_limit_config | cache_config
----+-----------------+-------------------+-----------------------+-------------------+--------------
  1 | test@email.com  | 2025-10-13 13:45  | success              | null              | null
```

---

## 错误排查

### 问题1: 端点404错误

**原因**: 路由未正确注册或后端未重启

**解决**:
```bash
# 检查后端日志
docker logs videosite_backend

# 重启后端
cd /home/eric/video/backend
source venv/bin/activate
pkill -f uvicorn
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 问题2: 缓存清除无效

**原因**: Redis连接问题

**解决**:
```bash
# 检查Redis状态
docker ps | grep redis

# 测试Redis连接
redis-cli -h localhost -p 6381 ping
```

### 问题3: 邮件发送失败

**原因**: SMTP配置未正确设置

**解决**:
1. 检查 `backend/.env` 中的SMTP配置
2. 确保以下环境变量正确：
   - `SMTP_HOST`
   - `SMTP_PORT`
   - `SMTP_USER`
   - `SMTP_PASSWORD`
   - `SMTP_FROM_EMAIL`

### 问题4: 备份文件无法恢复

**原因**: JSON格式错误或版本不兼容

**解决**:
```bash
# 验证JSON格式
cat backup_file.json | python -m json.tool

# 检查是否包含必需字段
cat backup_file.json | python -c "import sys, json; data = json.load(sys.stdin); print('settings' in data)"
```

---

## 性能测试

### 缓存性能测试

```bash
# 清除所有缓存
curl -X POST "http://localhost:8000/api/v1/admin/system/cache/clear" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"patterns": ["*"]}'

# 测试第一次请求（无缓存）
time curl -X GET "http://localhost:8000/api/v1/videos?page=1&page_size=20"

# 测试第二次请求（有缓存）
time curl -X GET "http://localhost:8000/api/v1/videos?page=1&page_size=20"

# 应该看到第二次请求明显更快
```

### 备份/恢复性能测试

```bash
# 测试导出速度
time curl -X GET "http://localhost:8000/api/v1/admin/system/settings/backup" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -o backup.json

# 测试导入速度
time curl -X POST "http://localhost:8000/api/v1/admin/system/settings/restore" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d @backup.json
```

---

## 总结检查清单

完成所有测试后，请确认：

- [ ] ✅ 所有5个新端点可正常访问
- [ ] ✅ 前端UI正确显示新面板和功能
- [ ] ✅ SMTP测试邮件可发送（如果配置了SMTP）
- [ ] ✅ 缓存统计显示正确
- [ ] ✅ 缓存清除功能正常
- [ ] ✅ 配置导出为有效JSON文件
- [ ] ✅ 配置恢复功能正常
- [ ] ✅ 数据库新字段存在且可用
- [ ] ✅ 中英文切换正常
- [ ] ✅ 所有操作有适当的成功/错误提示
- [ ] ✅ 页面自动保存功能正常

---

**测试文档版本**: 1.0
**创建日期**: 2025-10-13
**适用项目**: VideoSite Settings Enhancement
