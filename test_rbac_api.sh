#!/bin/bash

# 测试 RBAC API 的脚本

echo "=== RBAC API 测试 ==="
echo ""

API_URL="http://localhost:8000"

# 颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查后端
echo "1. 检查后端服务:"
if curl -s "$API_URL/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 后端服务运行正常${NC}"
else
    echo -e "${RED}✗ 后端服务未运行${NC}"
    exit 1
fi
echo ""

# 检查数据库权限数据
echo "2. 检查数据库权限数据:"
PERM_COUNT=$(docker exec videosite_postgres psql -U postgres -d videosite -t -c "SELECT COUNT(*) FROM permissions;" 2>/dev/null | tr -d ' ')
echo "权限总数: $PERM_COUNT"

if [ "$PERM_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ 权限表有数据${NC}"
else
    echo -e "${RED}✗ 权限表为空${NC}"
fi
echo ""

# 检查角色数据
echo "3. 检查数据库角色数据:"
ROLE_COUNT=$(docker exec videosite_postgres psql -U postgres -d videosite -t -c "SELECT COUNT(*) FROM roles;" 2>/dev/null | tr -d ' ')
echo "角色总数: $ROLE_COUNT"
echo ""

# 检查管理员数据
echo "4. 检查管理员账户:"
docker exec videosite_postgres psql -U postgres -d videosite -c "SELECT id, username, is_superadmin FROM admin_users;" 2>/dev/null
echo ""

# 提示测试 API
echo "5. 测试 RBAC API 端点:"
echo ""
echo "请使用以下命令测试（需要 superadmin token）:"
echo ""
echo "# 获取 token (登录)"
echo "TOKEN=\$(curl -s -X POST '$API_URL/api/v1/admin/auth/login' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"username\":\"admin\",\"password\":\"your_password\"}' | jq -r '.access_token')"
echo ""
echo "# 测试获取权限列表"
echo "curl -H \"Authorization: Bearer \$TOKEN\" '$API_URL/api/v1/admin/rbac/permissions' | jq"
echo ""
echo "# 测试获取角色列表"
echo "curl -H \"Authorization: Bearer \$TOKEN\" '$API_URL/api/v1/admin/rbac/roles' | jq"
echo ""
echo "# 测试获取管理员列表"
echo "curl -H \"Authorization: Bearer \$TOKEN\" '$API_URL/api/v1/admin/rbac/admin-users' | jq"
echo ""

# 检查前端状态
echo "6. 检查前端开发服务器:"
if lsof -i:5173 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 前端开发服务器正在运行 (端口 5173)${NC}"
else
    echo -e "${YELLOW}⚠ 前端开发服务器未运行${NC}"
fi
echo ""

echo "=== 常见问题排查 ==="
echo ""
echo "如果权限列表显示不出来，可能的原因："
echo ""
echo "1. 权限要求问题:"
echo "   - GET /api/v1/admin/rbac/permissions 需要 superadmin 权限"
echo "   - 确保你使用的是 superadmin 账户登录"
echo ""
echo "2. 前端请求错误:"
echo "   - 打开浏览器开发者工具 -> Network 标签"
echo "   - 查看 /api/v1/admin/rbac/permissions 请求"
echo "   - 检查状态码和响应内容"
echo ""
echo "3. 浏览器控制台错误:"
echo "   - 打开浏览器开发者工具 -> Console 标签"
echo "   - 查看是否有 JavaScript 错误或网络错误"
echo ""
echo "4. Token 过期:"
echo "   - 尝试重新登录"
echo "   - 检查 localStorage 中的 token"
echo ""

echo "=== 数据库权限详情 ==="
echo ""
echo "按模块查看权限分布:"
docker exec videosite_postgres psql -U postgres -d videosite -c "SELECT module, COUNT(*) as count FROM permissions GROUP BY module ORDER BY module;" 2>/dev/null
echo ""
