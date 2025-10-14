#!/bin/bash

# 诊断前端请求验证错误的脚本

echo "=== 前端验证错误诊断 ==="
echo ""

# 1. 检查后端日志中的验证错误
echo "1. 检查后端日志中最近的验证错误："
echo "---"
if docker ps | grep -q videosite-backend; then
    docker logs videosite-backend 2>&1 | grep -i "validation" | tail -10
    echo ""
    docker logs videosite-backend 2>&1 | grep "422" | tail -10
else
    echo "后端容器未运行，检查本地日志..."
    if [ -d "/home/eric/video/backend/logs" ]; then
        tail -50 /home/eric/video/backend/logs/*.log 2>/dev/null | grep -i "validation\|422"
    fi
fi
echo ""

# 2. 检查最近修改的前端服务文件
echo "2. 最近修改的前端服务文件："
echo "---"
cd /home/eric/video
git diff --name-only HEAD | grep -E "admin-frontend/src/services/.*\.ts$"
echo ""

# 3. 检查前端编译错误
echo "3. 检查前端类型错误："
echo "---"
cd /home/eric/video/admin-frontend
npx tsc --noEmit 2>&1 | head -20 || echo "TypeScript检查完成"
echo ""

# 4. 检查后端API schemas
echo "4. 检查后端可能的schema变更："
echo "---"
cd /home/eric/video
git diff backend/app/schemas/ | head -50
echo ""

# 5. 测试关键API端点
echo "5. 测试关键API端点（需要token）："
echo "---"
echo "提示：请手动测试以下API端点："
echo "  - GET /api/v1/admin/notifications"
echo "  - GET /api/v1/admin/scheduling/"
echo "  - GET /api/v1/admin/profile/me"
echo "  - GET /api/v1/admin/ip-blacklist/"
echo ""
echo "使用 curl 测试示例："
echo "  curl -H 'Authorization: Bearer YOUR_TOKEN' http://localhost:8000/api/v1/admin/notifications"
echo ""

echo "=== 诊断完成 ==="
echo ""
echo "如果发现错误，请提供："
echo "  1. 浏览器控制台的完整错误信息"
echo "  2. 出错的API端点路径"
echo "  3. 请求的payload（如果有）"
