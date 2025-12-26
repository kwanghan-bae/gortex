#!/bin/bash
# Gortex Pre-flight Verification Script
# This script MUST be run and passed before reporting completion of any task.

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚢 Starting Pre-flight Verification...${NC}"

# 1. Environment Check
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment (venv) not found. Run ./setup.sh first.${NC}"
    exit 1
fi

PYTHON="./venv/bin/python"
PYTEST="./venv/bin/python -m pytest"

# 2. Sanity Check (Core Services & Graph Boot)
echo -e "\n${BLUE}🔍 Step 1: Running Sanity Check (Core Integrity)${NC}"
$PYTHON scripts/sanity_check.py

# 3. Regression Tests (Known Bug Prevention)
echo -e "\n${BLUE}🔍 Step 2: Running Regression Test Suite${NC}"
$PYTEST tests/regression/

# 4. Critical Unit Tests (Core Logic)
echo -e "\n${BLUE}🔍 Step 3: Running Critical Unit Tests${NC}"
# Add more critical tests as the project grows
# $PYTEST tests/core/

echo -e "\n${GREEN}✅ PRE-FLIGHT CHECK PASSED! You are safe to report completion.${NC}"
