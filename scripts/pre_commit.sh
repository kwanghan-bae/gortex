#!/bin/bash

# 🛡️ SOVEREIGN GUARD PRE-COMMIT V8.3 (Ultimate Integrity)
# Features: Context-Aware, Hidden Error Scan, Full Build Guard, Scratchpad Validation.

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🔒 [Guard] Starting comprehensive multi-layer quality audit...${NC}"

# 1. AI Laziness & Hallucination Guard
LAZY_RE="\/\/[[:space:]]*\.\.\.|#[[:space:]]*\.\.\.|\/\*[:space:]]*\.\.\.*\*\/|// existing code|// rest of code|// same as before|# remains unchanged|TODO: Implement|\(중략\)|\(생략\)|// 기존 로직과 동일|// 상동|// 이전과 동일"
CODE_BAD_RE="@org\.springframework|kotlinx\.coroutines|@java\.util|@org\.apache|@com\.google"

STAGED_FILES=$(git diff --cached --name-only | grep -v "scripts/pre_commit.sh" | grep -v "docs/init/templates/" || true)

if [ -n "$STAGED_FILES" ]; then
    # 1.1 전역 나태함 검사
    if git diff --cached $STAGED_FILES | grep "^+" | grep -Ei "$LAZY_RE" > /dev/null; then
        echo -e "${RED}❌ [ABSOLUTE BLOCK] AI Laziness Detected!${NC}"
        exit 1
    fi

    # 1.2 소스 코드 전용 정밀 검사
    SOURCE_FILES=$(echo "$STAGED_FILES" | grep -E "\.(kt|java|ts|tsx|dart|cs)$" || true)
    if [ -n "$SOURCE_FILES" ]; then
        if git diff --cached $SOURCE_FILES | grep "^+" | grep -v "^+import " | grep -Ei "$CODE_BAD_RE" > /dev/null; then
            echo -e "${RED}❌ [CODE STANDARD VIOLATION] Lazy full-package call detected!${NC}"
            exit 1
        fi
    fi
fi

# 2. Path & Documentation Guard (Hard Binding)
STAGED_ALL=$(git diff --cached --name-only --diff-filter=ACM)
HAS_LOGIC=$(echo "$STAGED_ALL" | grep -E "\.(kt|java|ts|tsx|dart|cs|py)$" || true)
HAS_DOCS=$(echo "$STAGED_ALL" | grep -E "(\.md|docs/)" || true)

if [ -n "$HAS_LOGIC" ] && [ -z "$HAS_DOCS" ]; then
    echo -e "${RED}❌ [DOC DEBT] Logic changed but NO docs updated!${NC}"
    exit 1
fi

# 3. Scratchpad Health Check
# 연습장 파일이 초기화되지 않은 상태로 작업을 진행했는지 감사합니다.
if [ -f "docs/SCRATCHPAD.md" ]; then SP_PATH="docs/SCRATCHPAD.md"
elif [ -f "docs/*/SCRATCHPAD.md" ]; then SP_PATH=$(ls docs/*/SCRATCHPAD.md | head -n 1)
else SP_PATH=""
fi

if [ -n "$SP_PATH" ]; then
    if grep -q "{현재 달성하려는 목표}" "$SP_PATH"; then
        echo -e "${YELLOW}⚠️ [SCRATCHPAD] Thinking process is not updated for the current task!${NC}"
    fi
fi

# 4. Language Specific High-Rigor Audits
# 4.1 React Native / TypeScript
if echo "$STAGED_ALL" | grep -q "frontend/"; then
    echo "🧪 Verifying Frontend (RN + Full Build Guard)..."
    cd frontend
    npm test -- --watchAll=false 2>&1 | tee /tmp/test_log.txt
    if [ ${PIPESTATUS[0]} -ne 0 ] || grep -Ei "ERROR:|Failed to collect coverage|SyntaxError" /tmp/test_log.txt > /dev/null; then
        echo -e "${RED}❌ [TEST FAILURE] Critical errors detected!${NC}"
        exit 1
    fi
    cd ..
fi

# 4.2 Kotlin & Java
if echo "$STAGED_ALL" | grep -E "(\.kt|\.java)$" | grep -q "backend/"; then
    echo "🧪 Verifying JVM Backend (Kotlin/Java + ktlint)..."
    (cd backend && ./gradlew ktlintCheck test --quiet) || exit 1
fi

echo -e "${GREEN}✅ [Guard] Audit successful. Total Integrity Guaranteed.${NC}"
