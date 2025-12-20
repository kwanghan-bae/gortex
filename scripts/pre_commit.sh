#!/bin/bash
# Gortex Pre-Commit Check Script v1.1
# Features: Syntax Check, Unit Tests, Documentation Check, Test Coverage Check

set -e
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🔍 Starting Pre-Commit Checks...${NC}"

# ==========================================
# 1. Syntax Check (Build)
# ==========================================
echo -e "📦 Checking syntax..."
find . -name "*.py" -not -path "./venv/*" | xargs python3 -m py_compile
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Syntax Error Detected! Aborting commit.${NC}"
    exit 1
fi

# ==========================================
# 2. Unit Tests
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
# 3. Documentation & Test Coverage (Warnings)
# ==========================================
WARNINGS=0
echo -e "📝 Verifying documentation and test coverage..."

# 3.1 Get list of staged files
STAGED_FILES=$(git diff --cached --name-only)

# 3.2 Check Release Notes
if ! echo "$STAGED_FILES" | grep -q "release_note.md"; then
    echo -e "${YELLOW}⚠️  Warning: 'release_note.md' is NOT updated in this commit.${NC}"
    WARNINGS=$((WARNINGS+1))
fi

# 3.3 Check Next Session
if ! echo "$STAGED_FILES" | grep -q "next_session.md"; then
    echo -e "${YELLOW}⚠️  Warning: 'next_session.md' is NOT updated in this commit.${NC}"
    WARNINGS=$((WARNINGS+1))
fi

# 3.4 Check Test Existence for Python files
for file in $STAGED_FILES; do
    if [[ $file == *.py ]] && [[ $file != tests/* ]]; then
        # agents/coder.py -> tests/test_coder.py
        filename=$(basename "$file")
        test_file="tests/test_${filename}"
        
        if [ ! -f "$test_file" ]; then
             echo -e "${YELLOW}⚠️  Warning: No matching test file found for '$file' (Expected: $test_file)${NC}"
             WARNINGS=$((WARNINGS+1))
        fi
    fi
done

# ==========================================
# 4. Final Decision
# ==========================================
if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}🚨 Total Warnings: $WARNINGS${NC}"
    
    # 대화형 모드(터미널)인 경우에만 사용자 입력 대기
    if [ -t 0 ]; then
        read -p "경고를 무시하고 커밋을 진행하시겠습니까? (y/N): " choice
        case "$choice" in 
          y|Y ) echo -e "${GREEN}✅ 경고를 무시하고 진행합니다.${NC}";;
          * ) echo -e "${RED}❌ 사용자에 의해 커밋이 중단되었습니다.${NC}"; exit 1;;
        esac
    else
        # 비대화형 환경(Agent)에서는 경고를 로그에 남기고 통과
        echo -e "${YELLOW}⚠️  비대화형 모드 감지: 경고를 무시하고 진행합니다.${NC}"
    fi
else

    echo -e "${GREEN}✅ All Checks Passed! Ready to commit.${NC}"
    echo -e "\n${YELLOW}💡 Commit Message Guide:${NC}"
    echo -e "   Format: type: description (in Korean)"
    echo -e "   Types: feat, fix, docs, style, refactor, test, chore"
    echo -e "   Example: 'feat: 사용자 로그인 기능 구현 (테스트 완료)'"
fi

exit 0
