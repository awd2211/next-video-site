# 管理员账户信息

## 超级管理员账户 (Superadmin)

### 1. superadmin (推荐使用)
```
用户名: superadmin
邮箱:   superadmin@videosite.com
密码:   superadmin123
权限:   ✅ Superadmin (完全权限)
```

### 2. admin
```
用户名: admin
邮箱:   admin@videosite.com
密码:   admin123456
权限:   ✅ Superadmin (完全权限)
```

### 3. ai_admin
```
用户名: ai_admin
邮箱:   ai_admin@videosite.com
密码:   (需要重置)
权限:   ✅ Superadmin (完全权限)
```

## 普通管理员账户

### 4. editor
```
用户名: editor
邮箱:   editor@videosite.com
密码:   (需要重置)
权限:   ❌ 普通 Admin (有限权限)
```

## 登录方式

### 管理后台
- **URL**: http://localhost:3001
- **开发服务器**: http://localhost:5173 (如果使用 pnpm run dev)

### 登录步骤
1. 访问上述 URL
2. 输入用户名和密码
3. 点击登录

## 权限说明

### Superadmin 权限
✅ 查看所有权限列表
✅ 创建/编辑/删除权限
✅ 查看所有角色列表
✅ 创建/编辑/删除角色
✅ 查看所有管理员列表
✅ 分配角色给管理员
✅ 访问所有管理功能

### 普通 Admin 权限
✅ 查看权限列表（只读）
✅ 查看角色列表（只读）
✅ 查看管理员列表（只读）
❌ 不能创建/修改权限
❌ 不能创建/修改角色
❌ 不能分配角色

## 快速测试

### 测试权限列表是否显示

1. **使用 superadmin 登录**
   ```
   用户名: superadmin
   密码: superadmin123
   ```

2. **导航到角色管理**
   - 点击侧边栏"系统设置" → "角色管理"
   - 或直接访问: http://localhost:3001/roles

3. **切换到"权限列表"标签页**
   - 应该能看到 36 个权限
   - 按模块分组显示

4. **验证数据**
   - 应该看到 video, user, system, comment 等模块
   - 每个模块下有对应的权限

## 重置密码

如果需要重置任何账户的密码，运行：

```bash
cd /home/eric/video/backend
source venv/bin/activate
python << 'EOF'
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.models.user import AdminUser
from app.utils.security import get_password_hash
from app.config import settings

username = "要重置的用户名"  # 修改这里
new_password = "新密码"      # 修改这里

engine = create_engine(settings.DATABASE_URL_SYNC)
with Session(engine) as session:
    stmt = select(AdminUser).where(AdminUser.username == username)
    admin = session.execute(stmt).scalar_one_or_none()

    if admin:
        admin.hashed_password = get_password_hash(new_password)
        session.commit()
        print(f"✓ {username} 的密码已重置为: {new_password}")
    else:
        print(f"✗ 未找到用户: {username}")
EOF
```

## 创建新的超级管理员

```bash
cd /home/eric/video
python create_superadmin.py
```

或使用上面的重置密码脚本修改用户名和密码。

## 安全建议

⚠️ **生产环境注意事项:**

1. **修改默认密码**
   - 不要在生产环境使用这些简单密码
   - 使用强密码（至少 12 字符，包含大小写字母、数字、特殊字符）

2. **删除不需要的账户**
   - 如果不需要多个 superadmin，删除多余的
   - 只保留必要的管理员账户

3. **定期审计**
   - 定期检查管理员列表
   - 删除离职员工的账户
   - 检查角色分配是否合理

4. **启用日志**
   - 所有管理员操作都会记录在 `permission_logs` 表
   - 定期审查操作日志

## 当前系统状态

- ✅ 数据库已修复（email_configurations 表已恢复）
- ✅ 权限 API 已放宽（允许所有 admin 查看）
- ✅ VideoStatus 验证已修复
- ✅ 超级管理员账户已创建
- ✅ 总共 36 个权限
- ✅ 总共 9 个角色
- ✅ 总共 4 个管理员账户

## 故障排除

### 如果登录失败

1. **检查后端是否运行**
   ```bash
   curl http://localhost:8000/health
   ```

2. **检查密码是否正确**
   - 使用上面提供的密码
   - 注意大小写

3. **清除浏览器缓存**
   ```javascript
   // 在浏览器控制台执行
   localStorage.clear()
   location.reload()
   ```

### 如果权限列表不显示

1. **确认使用 superadmin 账户**
2. **打开浏览器开发者工具 (F12)**
3. **查看 Network 标签**
   - 找到 `/api/v1/admin/rbac/permissions` 请求
   - 状态码应该是 200
   - 响应应该包含 36 个权限

4. **查看 Console 标签**
   - 检查是否有 JavaScript 错误

## 联系支持

如果仍有问题，请提供：
- 使用的账户名
- 浏览器控制台截图
- Network 请求响应
- 错误消息

---

**最后更新**: 2025-10-14
**创建的账户**: superadmin
**状态**: ✅ 可用
