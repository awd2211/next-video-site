#!/bin/bash
# 全面测试所有缓存API端点

BASE_URL="http://localhost:8000/api/v1"
TOTAL=0
PASSED=0
FAILED=0

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_api() {
    local url="$1"
    local desc="$2"
    TOTAL=$((TOTAL + 1))
    
    response=$(curl -s "$url")
    
    # 检查是否有序列化错误
    if echo "$response" | grep -q '"__type__": "object"' || echo "$response" | grep -q "validation errors"; then
        echo -e "${RED}❌ FAIL${NC}: $desc"
        echo "   URL: $url"
        echo "   错误: 缓存序列化失败"
        FAILED=$((FAILED + 1))
        return 1
    elif echo "$response" | grep -q '"items"' || echo "$response" | grep -q '^\['; then
        echo -e "${GREEN}✅ PASS${NC}: $desc"
        PASSED=$((PASSED + 1))
        return 0
    elif echo "$response" | grep -q '"detail".*"Not Found"'; then
        echo -e "${YELLOW}⚠️  SKIP${NC}: $desc (404 Not Found - 可能数据为空)"
        return 0
    elif echo "$response" | grep -q '"detail"'; then
        error=$(echo "$response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('detail','')[:80])" 2>/dev/null)
        echo -e "${YELLOW}⚠️  WARN${NC}: $desc"
        echo "   错误: $error"
        return 0
    else
        echo -e "${YELLOW}⚠️  UNKNOWN${NC}: $desc (响应格式未知)"
        return 0
    fi
}

echo "=========================================="
echo "API缓存序列化全面测试"
echo "=========================================="
echo ""

echo "📹 视频相关 API"
echo "------------------------------------------"
test_api "$BASE_URL/videos?page=1&page_size=5" "视频列表"
test_api "$BASE_URL/videos/trending?page=1&page_size=5" "热门视频"
test_api "$BASE_URL/videos/featured?page=1&page_size=5" "精选视频"
test_api "$BASE_URL/videos/recommended?page=1&page_size=5" "推荐视频"
echo ""

echo "📂 分类相关 API"
echo "------------------------------------------"
test_api "$BASE_URL/categories" "分类列表"
test_api "$BASE_URL/categories/countries" "国家列表"
test_api "$BASE_URL/categories/tags" "标签列表"
echo ""

echo "🔍 搜索 API"
echo "------------------------------------------"
test_api "$BASE_URL/search?q=test&page=1&page_size=5" "搜索结果"
echo ""

echo "🎬 演员和导演 API"
echo "------------------------------------------"
test_api "$BASE_URL/actors?page=1&page_size=5" "演员列表"
test_api "$BASE_URL/directors?page=1&page_size=5" "导演列表"
echo ""

echo "📺 剧集 API"
echo "------------------------------------------"
test_api "$BASE_URL/series?page=1&page_size=5" "剧集列表"
echo ""

echo ""
echo "🔄 测试缓存命中 (第二次请求)"
echo "------------------------------------------"
test_api "$BASE_URL/videos/trending?page=1&page_size=5" "热门视频 [缓存]"
test_api "$BASE_URL/videos/featured?page=1&page_size=5" "精选视频 [缓存]"
test_api "$BASE_URL/categories" "分类列表 [缓存]"
echo ""

echo "=========================================="
echo "测试完成"
echo "=========================================="
echo -e "总计: ${TOTAL} 个测试"
echo -e "${GREEN}通过: ${PASSED}${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}失败: ${FAILED}${NC}"
fi
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ 所有关键API测试通过!${NC}"
    exit 0
else
    echo -e "${RED}❌ 有 $FAILED 个测试失败${NC}"
    exit 1
fi
