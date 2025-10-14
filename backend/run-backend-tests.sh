#!/bin/bash

# Backend 测试运行脚本

set -e

echo "🐍 Backend 测试运行脚本"
echo "================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 检查虚拟环境
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}⚠️  未激活虚拟环境，尝试激活...${NC}"
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo -e "${GREEN}✓ 虚拟环境已激活${NC}"
    else
        echo -e "${RED}❌ 未找到虚拟环境，请先运行: python -m venv venv${NC}"
        exit 1
    fi
fi

# 检查测试依赖
echo "📦 检查测试依赖..."
python -c "import pytest" 2>/dev/null || {
    echo -e "${YELLOW}安装测试依赖...${NC}"
    pip install -r requirements-dev.txt
}
echo -e "${GREEN}✓ 依赖检查完成${NC}"
echo ""

# 函数：运行测试组
run_test_group() {
    local group_name=$1
    local test_path=$2
    local marker=$3
    
    echo -e "${BLUE}▶ 运行 $group_name${NC}"
    
    if [ -n "$marker" ]; then
        if pytest "$test_path" -m "$marker" -v --tb=short; then
            echo -e "${GREEN}✓ $group_name 通过${NC}"
            echo ""
            return 0
        else
            echo -e "${RED}✗ $group_name 失败${NC}"
            echo ""
            return 1
        fi
    else
        if pytest "$test_path" -v --tb=short; then
            echo -e "${GREEN}✓ $group_name 通过${NC}"
            echo ""
            return 0
        else
            echo -e "${RED}✗ $group_name 失败${NC}"
            echo ""
            return 1
        fi
    fi
}

# 解析命令行参数
TEST_TYPE=${1:-all}

case "$TEST_TYPE" in
    "quick")
        echo "⚡ 快速测试模式"
        echo "================================"
        run_test_group "Schemas 测试" "tests/test_schemas.py"
        run_test_group "Validators 测试" "tests/test_validators.py"
        ;;
    
    "unit")
        echo "🧪 单元测试模式"
        echo "================================"
        run_test_group "单元测试" "tests/" "unit"
        ;;
    
    "api")
        echo "🌐 API 测试模式"
        echo "================================"
        run_test_group "API 端点测试" "tests/" "api"
        ;;
    
    "admin")
        echo "🔐 Admin API 测试模式"
        echo "================================"
        run_test_group "Admin API 测试" "tests/admin/" "admin"
        ;;
    
    "integration")
        echo "🔗 集成测试模式"
        echo "================================"
        run_test_group "集成测试" "tests/integration/" "integration"
        ;;
    
    "coverage")
        echo "📊 覆盖率测试模式"
        echo "================================"
        pytest tests/ --cov=app --cov-report=term --cov-report=html --cov-report=xml -v
        echo ""
        echo -e "${GREEN}✓ 覆盖率报告已生成${NC}"
        echo "  HTML 报告: htmlcov/index.html"
        echo "  XML 报告: coverage.xml"
        ;;
    
    "security")
        echo "🔒 安全测试模式"
        echo "================================"
        if [ -d "tests/security" ]; then
            run_test_group "安全测试" "tests/security/" "security"
        else
            echo -e "${YELLOW}⚠️  安全测试目录不存在${NC}"
        fi
        ;;
    
    "performance")
        echo "⚡ 性能测试模式"
        echo "================================"
        if [ -d "tests/performance" ]; then
            run_test_group "性能测试" "tests/performance/" "performance"
        else
            echo -e "${YELLOW}⚠️  性能测试目录不存在${NC}"
        fi
        ;;
    
    "all")
        echo "🎯 完整测试模式"
        echo "================================"
        echo ""
        
        echo "1️⃣  Schemas 和 Validators 测试"
        run_test_group "Schemas" "tests/test_schemas.py"
        run_test_group "Validators" "tests/test_validators.py"
        
        echo "2️⃣  API 端点测试"
        run_test_group "API Endpoints" "tests/test_api_endpoints.py"
        run_test_group "All Endpoints" "tests/test_all_endpoints.py"
        
        echo "3️⃣  综合测试"
        run_test_group "Comprehensive API" "tests/test_comprehensive_api.py"
        
        if [ -d "tests/admin" ]; then
            echo "4️⃣  Admin API 测试"
            run_test_group "Admin API" "tests/admin/"
        fi
        
        if [ -d "tests/models" ]; then
            echo "5️⃣  Models 测试"
            run_test_group "Models" "tests/models/"
        fi
        
        if [ -d "tests/utils" ]; then
            echo "6️⃣  Utils 测试"
            run_test_group "Utils" "tests/utils/"
        fi
        
        if [ -d "tests/middleware" ]; then
            echo "7️⃣  Middleware 测试"
            run_test_group "Middleware" "tests/middleware/"
        fi
        
        if [ -d "tests/integration" ]; then
            echo "8️⃣  集成测试"
            run_test_group "Integration" "tests/integration/"
        fi
        
        echo ""
        echo "📊 生成覆盖率报告..."
        pytest tests/ --cov=app --cov-report=term --cov-report=html -v || true
        ;;
    
    "help"|"-h"|"--help")
        echo "用法: ./run-backend-tests.sh [选项]"
        echo ""
        echo "选项:"
        echo "  all           运行所有测试 (默认)"
        echo "  quick         快速测试 (schemas + validators)"
        echo "  unit          只运行单元测试"
        echo "  api           只运行 API 测试"
        echo "  admin         只运行 Admin API 测试"
        echo "  integration   只运行集成测试"
        echo "  coverage      生成覆盖率报告"
        echo "  security      运行安全测试"
        echo "  performance   运行性能测试"
        echo "  help          显示此帮助信息"
        echo ""
        echo "示例:"
        echo "  ./run-backend-tests.sh quick      # 快速测试"
        echo "  ./run-backend-tests.sh coverage   # 覆盖率报告"
        echo "  ./run-backend-tests.sh admin      # Admin API 测试"
        exit 0
        ;;
    
    *)
        echo -e "${RED}❌ 未知选项: $TEST_TYPE${NC}"
        echo "运行 './run-backend-tests.sh help' 查看帮助"
        exit 1
        ;;
esac

echo ""
echo "================================"
echo -e "${GREEN}🎉 测试完成！${NC}"
echo "================================"

