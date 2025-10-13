# 新功能快速上手指南 🚀

> 2分钟了解并使用新实现的管理后台功能

---

## 🎯 新增功能

### 1️⃣ 实时通知系统 ✅ 已完成

在顶部导航栏的**铃铛图标**，管理员可以：
- 📬 实时接收7种类型的通知
- 👀 查看未读/已读通知
- ✓ 标记为已读
- 🗑️ 删除通知
- 🔗 点击跳转相关页面

### 2️⃣ 仪表盘自定义 ✅ API已完成

通过API可以：
- 📊 自定义仪表盘布局
- 🎨 拖拽排序组件（前端待实现）
- 👁️ 显示/隐藏组件
- 💾 保存个人布局配置

---

## ⚡ 1分钟快速测试

### 启动服务

```bash
# 终端1: 启动后端
cd backend && source venv/bin/activate
uvicorn app.main:app --reload

# 终端2: 启动前端
cd admin-frontend && pnpm run dev
```

### 测试通知系统

```bash
# 创建一个测试通知
curl -X POST http://localhost:8000/api/v1/admin/notifications/test-notification \
  -H "Authorization: Bearer YOUR_TOKEN"
```

然后打开管理面板 http://localhost:3001，点击右上角的铃铛图标！

---

## 📖 详细文档

查看完整文档了解所有功能细节：

1. **[实施总结](./ADMIN_FEATURES_IMPLEMENTATION_SUMMARY.md)** - 完整的功能说明
2. **[技术文档](./NOTIFICATION_AND_DASHBOARD_IMPLEMENTATION.md)** - 详细的实施文档

---

## 🔔 通知类型

| 图标 | 类型 | 说明 |
|-----|------|------|
| 👤 | 新用户注册 | 有新用户注册时通知 |
| 💬 | 待审核评论 | 有评论需要审核时通知 |
| ⚠️ | 系统错误 | 系统发生错误时告警 |
| 💾 | 存储警告 | 存储空间不足时警告 |
| ☁️ | 上传失败 | 视频上传失败时通知 |
| 🎬 | 处理完成 | 视频处理完成时通知 |
| 🔒 | 可疑活动 | 检测到可疑活动时警告 |

---

## 💻 API端点速查

### 通知系统

```bash
# 获取通知列表
GET /api/v1/admin/notifications

# 获取统计信息
GET /api/v1/admin/notifications/stats

# 标记为已读
PATCH /api/v1/admin/notifications/{id}

# 全部标记为已读
POST /api/v1/admin/notifications/mark-all-read

# 删除通知
DELETE /api/v1/admin/notifications/{id}

# 清空所有
POST /api/v1/admin/notifications/clear-all
```

### 仪表盘自定义

```bash
# 获取布局
GET /api/v1/admin/dashboard/layout

# 保存布局
PUT /api/v1/admin/dashboard/layout

# 重置布局
POST /api/v1/admin/dashboard/reset

# 可用组件
GET /api/v1/admin/dashboard/widgets
```

---

## 🔧 在代码中使用

### 发送通知（后端）

```python
from app.utils.admin_notification_service import AdminNotificationService

# 新用户注册通知
await AdminNotificationService.notify_new_user_registration(
    db=db,
    user_id=user.id,
    username=user.username,
    email=user.email
)

# 系统错误通知
await AdminNotificationService.notify_system_error(
    db=db,
    error_type="DatabaseError",
    error_message="Connection failed",
    error_id=error_log.id
)
```

### 获取通知（前端）

通知组件已经自动集成在 `AdminLayout` 中，无需额外代码！

---

## ✅ 验收清单

测试以下功能确认系统正常：

- [ ] 能看到铃铛图标
- [ ] 创建测试通知后，徽章显示数字
- [ ] 点击铃铛打开通知抽屉
- [ ] 能看到通知列表
- [ ] 标记已读功能正常
- [ ] 删除通知功能正常
- [ ] 筛选功能正常（全部/未读/已读）
- [ ] 国际化切换正常（中英文）
- [ ] 深色模式下显示正常

---

## 🆘 遇到问题？

### 通知不显示

1. 检查后端是否运行：`curl http://localhost:8000/api/docs`
2. 检查token是否有效：在浏览器控制台查看网络请求
3. 查看浏览器控制台是否有错误

### API调用失败

1. 确认已登录管理后台
2. 检查Authorization header
3. 查看后端日志：`backend/logs/`

### 需要帮助

查看详细文档：
- **完整功能文档**: `ADMIN_FEATURES_IMPLEMENTATION_SUMMARY.md`
- **技术实施文档**: `NOTIFICATION_AND_DASHBOARD_IMPLEMENTATION.md`
- **API文档**: http://localhost:8000/api/docs

---

## 🎉 就是这么简单！

通知系统现在已经可以使用了。只需在相应的业务逻辑中调用通知服务，管理员就能实时收到通知！

**Happy Coding! 🚀**
