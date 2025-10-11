#!/bin/bash
#
# 安全扫描脚本
# 运行多个安全工具检查代码和依赖
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}VideoSite 安全扫描${NC}"
echo -e "${BLUE}================================${NC}"
echo

# 检查虚拟环境
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}激活虚拟环境...${NC}"
    source venv/bin/activate || {
        echo -e "${RED}错误: 无法激活虚拟环境${NC}"
        exit 1
    }
fi

# 安装扫描工具（如果需要）
echo -e "${YELLOW}检查扫描工具...${NC}"
pip install -q bandit safety flake8 2>/dev/null || true

# 1. Bandit - Python安全扫描
echo -e "\n${BLUE}=== 1. Bandit 安全扫描 ===${NC}"
echo "检查常见安全问题..."
bandit -r app/ -f txt -o bandit_report.txt || true
bandit -r app/ -ll  # 只显示中高级别问题

# 2. Safety - 依赖漏洞检查
echo -e "\n${BLUE}=== 2. Safety 依赖漏洞检查 ===${NC}"
echo "检查已知漏洞..."
safety check --file requirements.txt --output text || true

# 3. Flake8 - 代码质量检查
echo -e "\n${BLUE}=== 3. Flake8 代码质量检查 ===${NC}"
echo "检查代码规范..."
flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics || true

# 4. 检查敏感信息泄露
echo -e "\n${BLUE}=== 4. 敏感信息检查 ===${NC}"
echo "搜索可能的密钥泄露..."

# 检查硬编码的密钥
echo "检查硬编码密钥..."
grep -r -i "password\s*=\s*['\"]" app/ --include="*.py" | grep -v "hashed_password" | grep -v "old_password" | grep -v "new_password" || echo "✅ 未发现硬编码密码"

# 检查DEBUG=True
echo "检查DEBUG配置..."
grep -r "DEBUG.*=.*True" app/ --include="*.py" || echo "✅ 未发现DEBUG=True"

# 检查print()语句
echo "检查print()使用..."
PRINT_COUNT=$(grep -r "print(" app/ --include="*.py" | wc -l)
echo "发现 $PRINT_COUNT 处使用print()（建议改为logging）"

# 5. 检查不安全的函数
echo -e "\n${BLUE}=== 5. 不安全函数检查 ===${NC}"
echo "检查eval/exec/os.system..."
grep -r "eval\|exec\|os\.system" app/ --include="*.py" || echo "✅ 未发现不安全函数"

# 6. 检查SQL注入风险
echo -e "\n${BLUE}=== 6. SQL注入风险检查 ===${NC}"
echo "检查原生SQL..."
grep -r "db\.execute.*f\"" app/ --include="*.py" | grep -v "# type:" || echo "✅ 未发现f-string SQL"

# 7. 生成报告
echo -e "\n${BLUE}=== 7. 生成安全报告 ===${NC}"
REPORT_FILE="security_report_$(date +%Y%m%d_%H%M%S).txt"

cat > $REPORT_FILE <<EOF
VideoSite 安全扫描报告
生成时间: $(date)
========================================

1. Bandit扫描结果:
$(cat bandit_report.txt 2>/dev/null || echo "报告生成失败")

2. Safety漏洞检查:
$(safety check --file requirements.txt 2>/dev/null || echo "检查失败")

3. 统计:
- print()使用: $PRINT_COUNT 处
- 待优化问题: 见上方扫描结果

========================================
EOF

echo -e "${GREEN}✅ 报告已生成: $REPORT_FILE${NC}"

# 汇总
echo -e "\n${BLUE}================================${NC}"
echo -e "${BLUE}扫描完成${NC}"
echo -e "${BLUE}================================${NC}"
echo
echo "详细报告: $REPORT_FILE"
echo "Bandit报告: bandit_report.txt"
echo
echo "建议："
echo "1. 查看并修复所有中高级别的安全问题"
echo "2. 更新有漏洞的依赖包"
echo "3. 将print()替换为logging"
echo "4. 定期（每月）运行此脚本"
echo

