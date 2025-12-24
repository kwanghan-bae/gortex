#!/bin/bash

# 🛡️ SOVEREIGN GUARD PRE-COMMIT V6.0 (Final Evolution)
# High-rigor enforcement of documentation-code integrity.

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🔒 [Sovereign Guard] Executing absolute quality audit...${NC}"

# 1. AI Laziness & Placeholder Detection (Hard Block)
# 패턴 정의 (패턴 자체가 grep에 걸리지 않도록 쪼개서 작성)
P1='//'
P2=' ...'
P3='#'
P4='(중략)'
JOINED_PATTERNS="${P1}${P2}|${P3}${P2}|\/\* ${P2} \*\/|// existing code|// rest of code|// same as before|# remains unchanged|TODO: Implement|${P4}|\(생략\)|// 기존 로직과 동일|// 상동|// 이전과 동일"
if git diff --cached | grep -Ei "$JOINED_PATTERNS"; then
    echo -e "${RED}❌ [ABSOLUTE BLOCK] AI Laziness Detected!${NC}"
    exit 1
fi

# 2. Strict Documentation Enforcement (NEW: Hard Link)
# 논리적 코드 변경 시 docs/ 하위 파일이나 README.md 수정이 없으면 커밋을 막습니다.
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)
HAS_LOGIC=$(echo "$STAGED_FILES" | grep -E "\.(kt|dart|py)$" || true)
HAS_DOCS=$(echo "$STAGED_FILES" | grep -E "(\.md|docs/)" || true)

if [ -n "$HAS_LOGIC" ] && [ -z "$HAS_DOCS" ]; then
    echo -e "${RED}❌ [DOCUMENTATION DEBT] You modified code but NOT documentation!${NC}"
    echo "AI는 반드시 SPEC_CATALOG.md, TECHNICAL_SPEC.md 혹은 ADR.md 중 하나를 업데이트해야 합니다."
    exit 1
fi

# 3. TDD Enforcement (Strict Pair Matching)
for FILE in $STAGED_FILES; do
    if [[ $FILE == *.kt ]] || [[ $FILE == *.dart ]]; then
        FILENAME=$(basename "$FILE")
        if [[ $FILENAME == *Test* ]] || [[ $FILENAME == *_test* ]]; then continue; fi
        TEST_KT="${FILENAME%.*}Test.kt"
        TEST_DART="${FILENAME%.*}_test.dart"
        if ! find . -name "$TEST_KT" -o -name "$TEST_DART" | grep -q .; then
            echo -e "${RED}❌ [TDD VIOLATION] Missing test file for: $FILENAME${NC}"
            exit 1
        fi
    fi
done

# 4. Project Specific Verification
if [ -f "clover-wallet/gradlew" ]; then
    (cd clover-wallet && ./gradlew ktlintCheck test --quiet) || exit 1
fi
if [ -f "clover_wallet_app/pubspec.yaml" ]; then
    (cd clover_wallet_app && flutter analyze && flutter test) || exit 1
fi

echo -e "${GREEN}✅ [Sovereign Guard] Audit successful. Your intelligence is consistent.${NC}"
