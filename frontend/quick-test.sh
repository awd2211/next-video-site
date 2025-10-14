#!/bin/bash

# 快速测试脚本 - 分组运行测试避免超时

echo "🧪 前端测试快速运行脚本"
echo "================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数器
TOTAL_PASSED=0
TOTAL_FAILED=0

# 函数：运行测试组
run_test_group() {
    local group_name=$1
    local pattern=$2
    
    echo -e "${YELLOW}▶ 运行 $group_name 测试...${NC}"
    
    if pnpm vitest run "$pattern" --reporter=verbose 2>&1 | tee -a test-results.log; then
        echo -e "${GREEN}✓ $group_name 测试通过${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}✗ $group_name 测试失败${NC}"
        echo ""
        return 1
    fi
}

# 清空之前的日志
> test-results.log

echo "1️⃣  测试 Utils (工具函数)"
run_test_group "Utils" "src/utils/__tests__/*.test.ts"
UTILS_RESULT=$?

echo "2️⃣  测试 Services (服务层)"
echo "   - 核心服务..."
run_test_group "Core Services" "src/services/__tests__/{api,userService,videoService}.test.ts"
CORE_SERVICES=$?

echo "   - 业务服务..."
run_test_group "Business Services" "src/services/__tests__/{commentService,favoriteService,historyService,ratingService}.test.ts"
BIZ_SERVICES=$?

echo "   - 内容服务..."
run_test_group "Content Services" "src/services/__tests__/{actorService,directorService,seriesService,danmakuService}.test.ts"
CONTENT_SERVICES=$?

echo "   - 功能服务..."
run_test_group "Feature Services" "src/services/__tests__/{notificationService,oauthService,shareService,downloadService}.test.ts"
FEATURE_SERVICES=$?

echo "   - 辅助服务..."
run_test_group "Helper Services" "src/services/__tests__/{searchHistoryService,recommendationService,subtitleService,watchlistService}.test.ts"
HELPER_SERVICES=$?

echo "   - 数据服务..."
run_test_group "Data Services" "src/services/__tests__/{dataService,favoriteFolderService,sharedWatchlistService}.test.ts"
DATA_SERVICES=$?

echo "3️⃣  测试 Components (组件)"
run_test_group "Components" "src/components/__tests__/*.test.tsx"
COMPONENTS=$?

echo ""
echo "================================"
echo "📊 测试总结"
echo "================================"

# 统计结果
FAILED_GROUPS=0
[ $UTILS_RESULT -ne 0 ] && ((FAILED_GROUPS++))
[ $CORE_SERVICES -ne 0 ] && ((FAILED_GROUPS++))
[ $BIZ_SERVICES -ne 0 ] && ((FAILED_GROUPS++))
[ $CONTENT_SERVICES -ne 0 ] && ((FAILED_GROUPS++))
[ $FEATURE_SERVICES -ne 0 ] && ((FAILED_GROUPS++))
[ $HELPER_SERVICES -ne 0 ] && ((FAILED_GROUPS++))
[ $DATA_SERVICES -ne 0 ] && ((FAILED_GROUPS++))
[ $COMPONENTS -ne 0 ] && ((FAILED_GROUPS++))

TOTAL_GROUPS=8
PASSED_GROUPS=$((TOTAL_GROUPS - FAILED_GROUPS))

echo "✅ 通过的测试组: $PASSED_GROUPS/$TOTAL_GROUPS"
echo "❌ 失败的测试组: $FAILED_GROUPS/$TOTAL_GROUPS"
echo ""
echo "📝 详细日志已保存到: test-results.log"
echo ""

if [ $FAILED_GROUPS -eq 0 ]; then
    echo -e "${GREEN}🎉 所有测试通过！${NC}"
    exit 0
else
    echo -e "${RED}⚠️  部分测试失败，请查看日志${NC}"
    exit 1
fi

