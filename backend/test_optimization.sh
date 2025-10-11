#!/bin/bash
# 服务器优化效果测试脚本

echo "================================"
echo "  服务器优化效果测试"
echo "================================"
echo ""

BASE_URL="http://localhost:8000"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试函数
test_endpoint() {
    local name=$1
    local url=$2
    
    echo -n "测试 $name ... "
    
    response=$(curl -s -w "\n%{http_code}" "$url")
    http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ 通过${NC}"
        return 0
    else
        echo -e "${RED}✗ 失败 (HTTP $http_code)${NC}"
        return 1
    fi
}

# 测试缓存效果
test_cache() {
    local name=$1
    local url=$2
    
    echo ""
    echo "测试 $name 缓存效果:"
    echo -n "  第1次请求 ... "
    time1=$(curl -s -o /dev/null -w "%{time_total}" "$url")
    echo "${time1}s"
    
    echo -n "  第2次请求 (缓存) ... "
    time2=$(curl -s -o /dev/null -w "%{time_total}" "$url")
    echo "${time2}s"
    
    # 计算提升百分比
    improvement=$(echo "scale=2; (($time1 - $time2) / $time1) * 100" | bc)
    if [ $(echo "$improvement > 0" | bc) -eq 1 ]; then
        echo -e "  ${GREEN}性能提升: ${improvement}%${NC}"
    else
        echo -e "  ${YELLOW}提升不明显${NC}"
    fi
}

# 测试HTTP缓存头
test_cache_headers() {
    local name=$1
    local url=$2
    
    echo -n "测试 $name HTTP缓存头 ... "
    cache_control=$(curl -s -I "$url" | grep -i "cache-control" | awk '{print $2}')
    
    if [ -n "$cache_control" ]; then
        echo -e "${GREEN}✓ 有缓存头: $cache_control${NC}"
    else
        echo -e "${YELLOW}⚠ 无缓存头${NC}"
    fi
}

echo "=== 1. 基础接口测试 ==="
test_endpoint "健康检查" "$BASE_URL/health"
test_endpoint "根路径" "$BASE_URL/"
echo ""

echo "=== 2. 缓存效果测试 ==="
test_cache "视频列表" "$BASE_URL/api/v1/videos?page=1&page_size=10"
test_cache "分类列表" "$BASE_URL/api/v1/categories"
test_cache "演员列表" "$BASE_URL/api/v1/actors/?page=1&page_size=10"
echo ""

echo "=== 3. HTTP缓存头测试 ==="
test_cache_headers "分类" "$BASE_URL/api/v1/categories"
test_cache_headers "国家" "$BASE_URL/api/v1/countries"
test_cache_headers "标签" "$BASE_URL/api/v1/tags"
test_cache_headers "演员" "$BASE_URL/api/v1/actors/"
test_cache_headers "导演" "$BASE_URL/api/v1/directors/"
echo ""

echo "=== 4. 视频接口测试 ==="
test_endpoint "视频列表" "$BASE_URL/api/v1/videos"
test_endpoint "热门视频" "$BASE_URL/api/v1/videos/trending"
test_endpoint "精选视频" "$BASE_URL/api/v1/videos/featured"
test_endpoint "推荐视频" "$BASE_URL/api/v1/videos/recommended"
echo ""

echo "=== 5. 基础数据接口测试 ==="
test_endpoint "分类列表" "$BASE_URL/api/v1/categories"
test_endpoint "国家列表" "$BASE_URL/api/v1/countries"
test_endpoint "标签列表" "$BASE_URL/api/v1/tags"
test_endpoint "演员列表" "$BASE_URL/api/v1/actors/"
test_endpoint "导演列表" "$BASE_URL/api/v1/directors/"
echo ""

echo "=== 6. 搜索接口测试 ==="
test_endpoint "搜索视频" "$BASE_URL/api/v1/search?q=video"
echo ""

echo "================================"
echo "  测试完成"
echo "================================"
echo ""
echo "说明:"
echo "  - ✓ 表示测试通过"
echo "  - ✗ 表示测试失败"
echo "  - ⚠ 表示功能正常但有改进空间"
echo ""
echo "性能提升明显表示优化生效！"
echo ""
echo "详细报告请查看:"
echo "  - FINAL_OPTIMIZATION_REPORT.md"
echo "  - OPTIMIZATION_APPLIED.md"
echo ""

