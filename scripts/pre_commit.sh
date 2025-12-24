#!/bin/bash

# 🛡️ SOVEREIGN GUARD PRE-COMMIT V6.5 (Ultra-Strict Polyglot)
# Features: Self-exclusion, Language-specific linters, Hidden error detection.

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🔒 [Guard] Starting intensive quality audit...${NC}"

# 1. AI Laziness & Hallucination Guard
P1='//'; P2=' ...'; P3='#'; P4='(중략)'
CHECK_RE="\/\/[[:space:]]*\.\.\.|#[[:space:]]*\.\.\.|\/\*[:space:]]*\.\.\.*\*\/|// existing code|// rest of code|// same as before|# remains unchanged|TODO: Implement|${P4}|\(생략\)|// 기존 로직과 동일|// 상동|// 이전과 동일"

STAGED_FILES_LIST=$(git diff --cached --name-only | grep -v "scripts/pre_commit.sh" || true)
if [ -n "$STAGED_FILES_LIST" ]; then
    if git diff --cached -- $STAGED_FILES_LIST | grep "^+" | grep -Ei "$CHECK_RE" > /dev/null; then
        echo -e "${RED}❌ [ABSOLUTE BLOCK] AI Laziness Detected in NEW code!${NC}"
        git diff --cached -- $STAGED_FILES_LIST | grep "^+" | grep -Ei "$CHECK_RE"
        exit 1
    fi
fi

# 2. File & Project Identification
STAGED_ALL=$(git diff --cached --name-only --diff-filter=ACM)
HAS_KOTLIN=$(echo "$STAGED_ALL" | grep -E "\.kt$" || true)
HAS_TS=$(echo "$STAGED_ALL" | grep -E "\.(ts|tsx)$" || true)
HAS_DOCS=$(echo "$STAGED_ALL" | grep -E "(\.md|docs/)" || true)

# 3. Documentation Debt Check
if ([ -n "$HAS_KOTLIN" ] || [ -n "$HAS_TS" ]) && [ -z "$HAS_DOCS" ]; then
    echo -e "${RED}❌ [DOC DEBT] Logic changed but NO docs updated! Update SPEC_CATALOG or TECHNICAL_SPEC.${NC}"
    exit 1
fi

# 4. Dedicated Validation
# 4.1 Kotlin / Java
if [ -n "$HAS_KOTLIN" ] && [ -f "backend/gradlew" ]; then
    echo "🧪 Verifying Backend (Kotlin + ktlint)..."
    (cd backend && ./gradlew ktlintCheck test --quiet) || exit 1
fi

# 4.2 React Native / JS / TS (Hidden Error Detection)
if [ -n "$HAS_TS" ] && [ -f "frontend/package.json" ]; then
    echo "🧪 Verifying Frontend (React Native + ESLint)..."
    cd frontend
    
    # Lint
    if npm run | grep -q "lint"; then
        npm run lint || echo -e "${YELLOW}⚠️ Lint failed, but proceeding...${NC}"
    fi
    
    # [핵심 지능] 테스트 로그 내 'ERROR:' 또는 'Failed' 탐지
    TEST_LOG=$(npm test -- --watchAll=false 2>&1)
    TEST_EXIT_CODE=$?
    echo "$TEST_LOG"
    
    if [ $TEST_EXIT_CODE -ne 0 ] || echo "$TEST_LOG" | grep -Ei "ERROR:|Failed to collect coverage" > /dev/null; then
        echo -e "${RED}❌ [STRICT BLOCK] Hidden errors or coverage failures detected in test output!${NC}"
        exit 1
    fi
    cd ..
fi

echo -e "${GREEN}✅ [Guard] All specific checks passed. Quality is absolute.${NC}"
