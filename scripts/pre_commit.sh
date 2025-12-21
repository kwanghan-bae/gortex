#!/bin/bash
# Gortex Pre-Commit Check Script v1.2 (Non-blocking & Auto-pass)

set -e
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🔍 Starting Pre-Commit Checks...${NC}"

# ==========================================
# 1. Syntax Check (Build) - CRITICAL (Fail on Error)
# ==========================================
echo -e "📦 Checking syntax..."
find . -name "*.py" -not -path "./venv/*" | xargs python3 -m py_compile
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Syntax Error Detected! Aborting commit.${NC}"
    exit 1
fi

# ==========================================
# 2. Unit Tests - CRITICAL (Fail on Error)
# ==========================================
echo -e "🧪 Running tests..."
if [ -d "venv" ]; then
    PYTHON_CMD="venv/bin/python"
elif [ -d "../venv" ]; then
    PYTHON_CMD="../venv/bin/python"
else
    PYTHON_CMD="python3"
fi
export PYTHONPATH=$PYTHONPATH:..

$PYTHON_CMD -m unittest discover tests
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Tests Failed! Aborting commit.${NC}"
    exit 1
fi

# ==========================================
# 3. Documentation & Test Coverage (Warnings only)
# ==========================================
WARNINGS=0
echo -e "📝 Verifying documentation and test coverage..."

STAGED_FILES=$(git diff --cached --name-only)

# Check Release Notes (Warning)
if ! echo "$STAGED_FILES" | grep -q "release_note.md"; then
    echo -e "${YELLOW}⚠️  Warning: 'release_note.md' not updated.${NC}"
    WARNINGS=$((WARNINGS+1))
fi

# Check Next Session (Warning)
if ! echo "$STAGED_FILES" | grep -q "next_session.md"; then
    echo -e "${YELLOW}⚠️  Warning: 'next_session.md' not updated.${NC}"
    WARNINGS=$((WARNINGS+1))
fi

# Check Test Existence (Warning)
for file in $STAGED_FILES; do
    if [[ $file == *.py ]] && [[ $file != tests/* ]]; then
        filename=$(basename "$file")
        test_file="tests/test_${filename}"
        if [ ! -f "$test_file" ]; then
             echo -e "${YELLOW}⚠️  Warning: No test found for '$file'.${NC}"
             WARNINGS=$((WARNINGS+1))
        fi
    fi
done

# ==========================================
# 4. Final Result
# ==========================================
if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}🚨 Total Warnings: $WARNINGS (Proceeding automatically in 1s...)${NC}"
    sleep 1 # 에이전트가 로그를 볼 수 있도록 잠시 대기
else
    echo -e "${GREEN}✅ All Checks Passed!${NC}"
fi

# Always return 0 unless critical checks failed
echo -e "${GREEN}🚀 Ready to commit.${NC}"

# Guide for Agent
echo -e "\n${YELLOW}💡 Commit Message Guide:${NC}"
echo -e "   Format: type: description (in Korean)"
echo -e "   Types: feat, fix, docs, style, refactor, test, chore"
echo -e "   Example: 'feat: 사용자 로그인 기능 구현 (테스트 완료)'"

exit 0