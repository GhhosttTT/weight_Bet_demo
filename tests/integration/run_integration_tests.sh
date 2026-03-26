#!/bin/bash

# 跨平台集成测试执行脚本

set -e

echo "========================================="
echo "减肥对赌 APP - 跨平台集成测试"
echo "========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Python 环境
echo "检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 Python 3${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 环境正常${NC}"
echo ""

# 检查依赖
echo "检查依赖..."
pip3 install -q pytest requests
echo -e "${GREEN}✓ 依赖安装完成${NC}"
echo ""

# 检查后端服务
echo "检查后端服务..."
if ! curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${YELLOW}警告: 后端服务未运行${NC}"
    echo "请先启动后端服务:"
    echo "  cd backend && python manage.py runserver"
    echo ""
    read -p "是否继续测试? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓ 后端服务正常${NC}"
fi
echo ""

# 创建测试报告目录
REPORT_DIR="test_reports"
mkdir -p $REPORT_DIR
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="$REPORT_DIR/integration_test_report_$TIMESTAMP.html"

echo "========================================="
echo "开始执行集成测试"
echo "========================================="
echo ""

# 运行测试
echo "1. 运行跨平台基础功能测试..."
pytest test_cross_platform.py \
    -v \
    --html=$REPORT_FILE \
    --self-contained-html \
    --tb=short \
    --color=yes

TEST_EXIT_CODE_1=$?

echo ""
echo "2. 运行结算流程测试..."
pytest test_settlement.py -v -s --tb=short --color=yes

TEST_EXIT_CODE_2=$?

echo ""
echo "3. 运行支付流程测试..."
pytest test_payment.py -v -s --tb=short --color=yes

TEST_EXIT_CODE_3=$?

# 计算总体测试结果
TEST_EXIT_CODE=$((TEST_EXIT_CODE_1 + TEST_EXIT_CODE_2 + TEST_EXIT_CODE_3))

echo ""
echo "========================================="
echo "测试完成"
echo "========================================="
echo ""

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ 所有测试通过${NC}"
    echo ""
    echo "测试报告已生成: $REPORT_FILE"
    exit 0
else
    echo -e "${RED}✗ 部分测试失败${NC}"
    echo ""
    echo "测试报告已生成: $REPORT_FILE"
    echo "请查看报告了解详细信息"
    exit 1
fi
