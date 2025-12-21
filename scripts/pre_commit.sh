#!/bin/bash
# Gortex Pre-Commit Check Script v1.3 (Strict Quality Control)

set -e
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🔍 Starting High-Rigor Pre-Commit Checks...${NC}"

# Python Command Setup
if [ -d "venv" ]; then
    PYTHON_CMD="venv/bin/python"
elif [ -d "../venv" ]; then
    PYTHON_CMD="../venv/bin/python"
else
    PYTHON_CMD="python3"
fi

# Ensure PYTHONPATH include project root's parent to treat 'gortex' as package
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PARENT_DIR="$(dirname "$PROJECT_ROOT")"
export PYTHONPATH=$PARENT_DIR:$PYTHONPATH

# ==========================================
# 1. Syntax & Lint Check (CRITICAL)
# ==========================================
echo -e "📦 Checking syntax and linting (Ruff)..."
cd "$PROJECT_ROOT"

if command -v ruff &> /dev/null; then
    ruff check . --fix || { echo -e "${RED}❌ Lint errors found! Fix them before committing.${NC}"; exit 1; }
else
    echo -e "${YELLOW}⚠️  Ruff not found. Falling back to basic syntax check...${NC}"
    find . -name "*.py" -not -path "./venv/*" | xargs python3 -m py_compile || { echo -e "${RED}❌ Syntax Error Detected!${NC}"; exit 1; }
fi

# ==========================================
# 2. Strict Test Existence Check (CRITICAL)
# ==========================================
echo -e "🧪 Verifying mandatory test existence..."
STAGED_FILES=$(git diff --cached --name-only)
for file in $STAGED_FILES; do
    # src 디렉토리나 에이전트/코어 로직 파일인 경우 (tests/ 제외)
    if [[ $file == *.py ]] && [[ $file != tests/* ]] && [[ $file != scripts/* ]]; then
        filename=$(basename "$file")
        test_file="tests/test_${filename}"
        if [ ! -f "$test_file" ]; then
             echo -e "${RED}❌ CRITICAL: No test file found for '$file'.${NC}"
             echo -e "${RED}   Expected: '$test_file'${NC}"
             exit 1
        fi
    fi
done

# ==========================================
# 3. Unit Tests & Coverage (CRITICAL)
# ==========================================
echo -e "📊 Running tests with coverage..."
if $PYTHON_CMD -m coverage --version &> /dev/null; then
    $PYTHON_CMD -m coverage run -m unittest discover -s tests -p "test_*.py"
    $PYTHON_CMD -m coverage report -m
else
    $PYTHON_CMD -m unittest discover -s tests -p "test_*.py"
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Tests Failed! Aborting commit.${NC}"
    exit 1
fi

# ==========================================
# 4. Documentation Check (Warnings)
# ==========================================
WARNINGS=0
echo -e "📝 Checking session documentation..."
if ! echo "$STAGED_FILES" | grep -q "release_note.md"; then
    echo -e "${YELLOW}⚠️  Warning: 'release_note.md' not updated.${NC}"
    WARNINGS=$((WARNINGS+1))
fi
if ! echo "$STAGED_FILES" | grep -q "next_session.md"; then
    echo -e "${YELLOW}⚠️  Warning: 'next_session.md' not updated.${NC}"
    WARNINGS=$((WARNINGS+1))
fi

# ==========================================
# 5. Final Result
# ==========================================
if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}🚨 Total Warnings: $WARNINGS (Proceeding automatically...)${NC}"
else
    echo -e "${GREEN}✅ All Quality Checks Passed!${NC}"
fi

echo -e "${GREEN}🚀 Ready to commit. Follow the Korean commit guide below.${NC}"
echo -e "\n${YELLOW}💡 Commit Message Guide:${NC}"
echo -e "   Format: type: description (in Korean)"
echo -e "   Types: feat, fix, docs, style, refactor, test, chore"

exit 0
