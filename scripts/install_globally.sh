#!/bin/bash
# Gortex Global Installer
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_SCRIPT="$PROJECT_ROOT/run.sh"

GREEN='\033[0;32m'
NC='\033[0m'

echo -e "Gortex를 어디서든 실행할 수 있도록 설정합니다."

# 시스템 경로에 등록 시도 (macOS/Linux)
if [ -w "/usr/local/bin" ]; then
    sudo ln -sf "$RUN_SCRIPT" /usr/local/bin/gortex
    echo -e "${GREEN}✅ '/usr/local/bin/gortex' 심볼릭 링크가 생성되었습니다.${NC}"
    echo -e "이제 터미널 어디서든 'gortex'라고 입력하여 실행할 수 있습니다."
else
    # 권한이 없는 경우 alias 제안
    SHELL_RC="$HOME/.zshrc"
    [ ! -f "$SHELL_RC" ] && SHELL_RC="$HOME/.bashrc"
    
    echo "alias gortex='$RUN_SCRIPT'" >> "$SHELL_RC"
    echo -e "${GREEN}✅ '$SHELL_RC'에 alias가 추가되었습니다.${NC}"
    echo -e "새 터미널을 열거나 'source $SHELL_RC'를 실행한 후 'gortex'를 입력하세요."
fi
