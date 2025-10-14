#!/bin/bash

# 测试验证错误修复的脚本

echo "=== 验证错误修复测试 ==="
echo ""

# 颜色代码
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# API 基础 URL
API_URL="http://localhost:8000"

# 测试 1: 检查 email_configurations 表
echo "1. 测试数据库表 email_configurations:"
if docker exec videosite_postgres psql -U postgres -d videosite -c "\dt email_configurations" 2>/dev/null | grep -q "email_configurations"; then
    echo -e "${GREEN}✓ email_configurations 表存在${NC}"
else
    echo -e "${RED}✗ email_configurations 表不存在${NC}"
fi
echo ""

# 测试 2: 检查 email_templates 表
echo "2. 测试数据库表 email_templates:"
if docker exec videosite_postgres psql -U postgres -d videosite -c "\dt email_templates" 2>/dev/null | grep -q "email_templates"; then
    echo -e "${GREEN}✓ email_templates 表存在${NC}"
else
    echo -e "${RED}✗ email_templates 表不存在${NC}"
fi
echo ""

# 测试 3: 检查后端是否运行
echo "3. 测试后端服务状态:"
if curl -s "$API_URL/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 后端服务正常运行${NC}"
    BACKEND_RUNNING=true
else
    echo -e "${YELLOW}⚠ 后端服务未运行，跳过 API 测试${NC}"
    BACKEND_RUNNING=false
fi
echo ""

if [ "$BACKEND_RUNNING" = true ]; then
    # 测试 4: 测试无效状态值（需要token）
    echo "4. 测试无效 VideoStatus 值处理:"
    echo -e "${YELLOW}注意: 此测试需要有效的管理员 token${NC}"
    echo "请手动测试以下命令："
    echo ""
    echo "  curl -H 'Authorization: Bearer YOUR_TOKEN' \\"
    echo "    '$API_URL/api/v1/admin/videos?status=pending'"
    echo ""
    echo "预期响应: HTTP 400, 错误消息包含 'Invalid status value'"
    echo ""

    # 测试 5: 测试有效状态值
    echo "5. 测试有效 VideoStatus 值:"
    echo "有效的状态值为: draft, published, archived"
    echo ""
fi

# 测试 6: 检查 VideoStatus 枚举
echo "6. 检查 VideoStatus 枚举定义:"
if grep -q "class VideoStatus" backend/app/models/video.py; then
    echo -e "${GREEN}✓ VideoStatus 枚举已定义${NC}"
    echo "有效值:"
    grep -A4 "class VideoStatus" backend/app/models/video.py | grep "=" | sed 's/^/  /'
else
    echo -e "${RED}✗ VideoStatus 枚举未找到${NC}"
fi
echo ""

# 测试 7: 检查迁移状态
echo "7. 检查数据库迁移状态:"
cd backend
source venv/bin/activate 2>/dev/null
CURRENT_VERSION=$(alembic current 2>/dev/null | head -1)
if [ ! -z "$CURRENT_VERSION" ]; then
    echo -e "${GREEN}✓ 当前迁移版本: $CURRENT_VERSION${NC}"
else
    echo -e "${RED}✗ 无法获取迁移版本${NC}"
fi
cd ..
echo ""

# 总结
echo "=== 测试完成 ==="
echo ""
echo "如果所有数据库测试通过，请："
echo "1. 重启后端服务（如果正在运行）"
echo "2. 清除浏览器缓存"
echo "3. 测试前端视频列表页面"
echo "4. 验证状态筛选功能"
echo ""
echo "详细修复说明请查看: VALIDATION_ERROR_FIX.md"
