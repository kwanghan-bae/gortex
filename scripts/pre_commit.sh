#!/bin/bash

# 🛡️ SOVEREIGN GUARD PRE-COMMIT V6.3 (Language-Specific Edition)
# Enforces specific linters and tests based on changed file types.

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🔒 [Guard] Starting language-specific quality audit...${NC}"

# 1. AI Laziness & Hallucination Guard
P1='//'; P2=' ...'; P3='#'; P4='(중략)'
JOINED_PATTERNS="${P1}${P2}|${P3}${P2}|\/\* ${P2} \*\/|// existing code|// rest of code|// same as before|# remains unchanged|TODO: Implement|${P4}|\(생략\)|// 기존 로직과 동일|// 상동|// 이전과 동일"

if git diff --cached -- . ':!scripts/pre_commit.sh' | grep "^+" | grep -Ei "$JOINED_PATTERNS" > /dev/null; then
    echo -e "${RED}❌ [ABSOLUTE BLOCK] AI Laziness Detected!${NC}"
    exit 1
fi

# 2. File Identification
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)
HAS_KOTLIN=$(echo "$STAGED_FILES" | grep -E "\.kt$" || true)
HAS_TS=$(echo "$STAGED_FILES" | grep -E "\.(ts|tsx)$" || true)
HAS_PYTHON=$(echo "$STAGED_FILES" | grep -E "\.py$" || true)
HAS_DART=$(echo "$STAGED_FILES" | grep -E "\.dart$" || true)
HAS_CSHARP=$(echo "$STAGED_FILES" | grep -E "\.cs$" || true)

# 3. Dedicated Linting & Testing
# 3.1 C# / Unity
if [ -n "$HAS_CSHARP" ]; then
    if command -v dotnet &> /dev/null; then
        echo "🧪 Linting C# (dotnet format)..."
        dotnet format --verify-no-changes || exit 1
    else
        echo -e "${YELLOW}⚠️ dotnet SDK not found, skipping C# format check...${NC}"
    fi
fi

# 3.2 Kotlin (ktlint)
if [ -n "$HAS_KOTLIN" ] && [ -f "backend/gradlew" ]; then
    echo "🧪 Linting Kotlin (ktlint)..."
    (cd backend && ./gradlew ktlintCheck test --quiet) || exit 1
fi

# 3.2 React Native / TS (ESLint)
if [ -n "$HAS_TS" ] && [ -f "frontend/package.json" ]; then
    echo "🧪 Linting TypeScript (ESLint)..."
    (cd frontend && npm run lint && npm test -- --watchAll=false) || exit 1
fi

# 3.3 Python (Ruff)
if [ -n "$HAS_PYTHON" ]; then
    if command -v ruff &> /dev/null; then
        echo "🧪 Linting Python (Ruff)..."
        ruff check . || exit 1
    fi
fi

# 3.4 Flutter (Analyzer)
if [ -n "$HAS_DART" ] && [ -f "pubspec.yaml" ]; then
    echo "🧪 Linting Dart (Analyzer)..."
    flutter analyze || exit 1
fi

echo -e "${GREEN}✅ [Guard] All specific checks passed.${NC}"
