#!/bin/bash

echo "🔍 检查前端测试状态"
echo "================================"
echo ""

echo "📁 测试文件统计："
echo "  Services: $(ls -1 src/services/__tests__/*.test.ts 2>/dev/null | wc -l) 个"
echo "  Components: $(ls -1 src/components/__tests__/*.test.tsx 2>/dev/null | wc -l) 个"
echo "  Utils: $(ls -1 src/utils/__tests__/*.test.ts 2>/dev/null | wc -l) 个"
echo ""

TOTAL_TESTS=$(($(ls -1 src/services/__tests__/*.test.ts 2>/dev/null | wc -l) + \
               $(ls -1 src/components/__tests__/*.test.tsx 2>/dev/null | wc -l) + \
               $(ls -1 src/utils/__tests__/*.test.ts 2>/dev/null | wc -l)))

echo "  总计: $TOTAL_TESTS 个测试文件"
echo ""

echo "📦 测试依赖："
if pnpm list vitest --depth=0 2>/dev/null | grep -q vitest; then
    echo "  ✅ vitest"
else
    echo "  ❌ vitest (未安装)"
fi

if pnpm list @testing-library/react --depth=0 2>/dev/null | grep -q @testing-library/react; then
    echo "  ✅ @testing-library/react"
else
    echo "  ❌ @testing-library/react (未安装)"
fi

if pnpm list axios-mock-adapter --depth=0 2>/dev/null | grep -q axios-mock-adapter; then
    echo "  ✅ axios-mock-adapter"
else
    echo "  ❌ axios-mock-adapter (未安装)"
fi

echo ""
echo "🧪 可用的测试命令："
echo "  pnpm test                    - 运行所有测试"
echo "  pnpm test:watch              - 监视模式"
echo "  pnpm test:ui                 - 测试 UI 界面"
echo "  pnpm test:coverage           - 覆盖率报告"
echo "  ./quick-test.sh              - 分组快速测试"
echo "  node run-service-tests.js    - 服务测试运行器"
echo ""

echo "📊 测试详细报告："
echo "  - SERVICES_TEST_REPORT.md"
echo "  - COMPONENTS_TEST_REPORT.md"
echo "  - TEST_COMPLETION_SUMMARY.md"
echo ""

echo "✨ 推荐运行："
echo "  ./quick-test.sh              (分组运行，避免超时)"
echo ""

