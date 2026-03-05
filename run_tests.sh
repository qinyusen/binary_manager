#!/bin/bash
# Release Portal V3 测试运行脚本

set -e

echo "================================================"
echo "Release Portal V3 - 集成测试套件"
echo "================================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 pytest 是否安装
if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW}pytest 未安装，正在安装...${NC}"
    pip3 install -r requirements-test.txt
fi

# 解析命令行参数
TEST_TYPE="${1:-all}"
VERBOSE="${2:-false}"

echo "运行测试类型: $TEST_TYPE"
echo ""

# 运行测试
case $TEST_TYPE in
    "all")
        echo -e "${GREEN}运行所有测试...${NC}"
        pytest tests/ -v --tb=short
        ;;
    
    "api")
        echo -e "${GREEN}运行 API 测试...${NC}"
        pytest tests/api/ -v --tb=short
        ;;
    
    "integration")
        echo -e "${GREEN}运行集成测试...${NC}"
        pytest tests/integration/ -v --tb=short
        ;;
    
    "coverage")
        echo -e "${GREEN}运行测试并生成覆盖率报告...${NC}"
        pytest tests/ --cov=release_portal --cov-report=html --cov-report=term
        echo ""
        echo -e "${GREEN}覆盖率报告已生成: htmlcov/index.html${NC}"
        ;;
    
    "quick")
        echo -e "${GREEN}运行快速测试（跳过慢速测试）...${NC}"
        pytest tests/ -v -m "not slow" --tb=short
        ;;
    
    "parallel")
        echo -e "${GREEN}并行运行测试（需要 pytest-xdist）...${NC}"
        pytest tests/ -n auto -v --tb=short
        ;;
    
    *)
        echo -e "${RED}未知的测试类型: $TEST_TYPE${NC}"
        echo ""
        echo "可用选项:"
        echo "  all         - 运行所有测试（默认）"
        echo "  api         - 仅运行 API 测试"
        echo "  integration - 仅运行集成测试"
        echo "  coverage    - 运行测试并生成覆盖率报告"
        echo "  quick       - 运行快速测试（跳过慢速测试）"
        echo "  parallel    - 并行运行测试"
        exit 1
        ;;
esac

# 检查测试结果
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}================================================${NC}"
    echo -e "${GREEN}✓ 所有测试通过！${NC}"
    echo -e "${GREEN}================================================${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}================================================${NC}"
    echo -e "${RED}✗ 测试失败${NC}"
    echo -e "${RED}================================================${NC}"
    exit 1
fi
