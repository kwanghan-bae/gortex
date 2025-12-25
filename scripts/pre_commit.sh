#!/bin/bash

# 🛡️ SOVEREIGN GUARD PRE-COMMIT (Python Edition)
# Checks: Syntax, Tests, Imports

export GORTEX_CI=true

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🔒 [Guard] Starting Gortex integrity check...${NC}"

# 1. Syntax Check (Compile only)
echo "🔍 Checking Python syntax..."
find . -name "*.py" -not -path "*/venv/*" -not -path "*/__pycache__/*" | xargs -n 1 python3 -m py_compile
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Syntax Error detected!${NC}"
    exit 1
fi

# 2. Critical Tests (No Mocking)
echo "🧪 Running Smoke Tests (Environment, UI & Main Integrity)..."
if ! venv/bin/python -m unittest tests/test_environment_integrity.py tests/test_main_integrity.py tests/test_ui_smoke.py; then
    echo -e "${RED}❌ Smoke Tests Failed!${NC}"
    exit 1
fi

# 3. Unit Tests (All)
echo "🧪 Running Unit Tests..."
if ! venv/bin/python -m unittest discover tests; then
    echo -e "${RED}❌ Unit Tests Failed!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ [Guard] All checks passed. Gortex is safe to launch.${NC}"
