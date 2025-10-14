#!/bin/bash

# 测试登录脚本

echo "====== 测试用户登录 ======"
echo ""
echo "现有用户列表："
docker exec -i videosite_postgres psql -U postgres -d videosite -c "SELECT id, email, username FROM users ORDER BY created_at DESC LIMIT 10;"

echo ""
echo "====== 测试登录 ======"
echo "请输入邮箱："
read EMAIL
echo "请输入密码："
read -s PASSWORD

echo ""
echo "发送登录请求..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")

echo ""
echo "登录响应："
echo "$RESPONSE" | python -m json.tool 2>/dev/null || echo "$RESPONSE"

# 如果登录成功，提取token
if echo "$RESPONSE" | grep -q "access_token"; then
    echo ""
    echo "✅ 登录成功！"
    ACCESS_TOKEN=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
    if [ -n "$ACCESS_TOKEN" ]; then
        echo "Access Token: ${ACCESS_TOKEN:0:50}..."
    fi
else
    echo ""
    echo "❌ 登录失败！"
fi
