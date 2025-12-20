#!/bin/bash
# Gortex Pre-Commit Check Script (Fixed Path & PYTHONPATH & VENV)

set -e
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🔍 Starting Pre-Commit Checks...${NC}"

# 1. Syntax Check (Build)
echo -e "📦 checking syntax..."
find . -name "*.py" -not -path "./venv/*" | xargs python3 -m py_compile
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Syntax Error Detected! Aborting commit.${NC}"
    exit 1
fi

# 2. Unit Tests
echo -e "🧪 running tests..."

# venv 위치 찾기 (현재 디렉토리 또는 상위 디렉토리)
if [ -d "venv" ]; then
    PYTHON_CMD="venv/bin/python"
elif [ -d "../venv" ]; then
    PYTHON_CMD="../venv/bin/python"
else
    PYTHON_CMD="python3"
    echo -e "${RED}⚠️ No virtual environment found. Using system python.${NC}"
fi

# PYTHONPATH에 상위 디렉토리 추가 (gortex 패키지 인식용)
export PYTHONPATH=$PYTHONPATH:..

$PYTHON_CMD -m unittest discover tests
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Tests Failed! Aborting commit.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All Checks Passed! Ready to commit.${NC}"
exit 0