# 🚫 Strict AI Constraints & Anti-Patterns (Gortex)

이 문서는 Gortex AI가 절대 범해서는 안 되는 **금기 사항(Taboos)**을 정의합니다.

---

## 1. 금지된 코딩 패턴 (Coding Taboos)
- **Hardcoded Secrets**: API Key나 비밀번호를 코드 내에 문자열로 직접 입력 금지. (반드시 `os.getenv` 사용)
- **Infinite Loops**: `while True:` 등 무한 루프 가능성이 있는 코드는 반드시 탈출 조건(`break` 또는 타임아웃)을 명시해야 함.
- **Blind Shell Execution**: `rm -rf`, `mkfs` 등 시스템 파괴적인 셸 명령어를 검증 없이 실행 금지.
- **Global Scope Pollution**: 모듈 수준에서 전역 변수를 남발하여 상태 관리를 어렵게 만드는 행위 금지.

## 2. 금지된 소통 패턴 (Communication Taboos)
- **Fake Confirmation**: 실제로 실행하지 않고 "수정했습니다"라고 거짓 보고 금지.
- **Silent Fail**: 에러가 발생했음에도 사용자에게 알리지 않고 넘어가는 행위 금지.
- **Doc-Code Mismatch**: 코드는 수정했으나 문서를 업데이트하지 않는 "직무 유기" 금지.

## 3. 에이전트별 금기 사항
- **Coder**: 테스트 없이 프로덕션 코드를 커밋하는 행위.
- **Manager**: 명확한 이유 없이 작업을 무한히 핑퐁(Ping-pong) 치는 행위.
- **Planner**: 실행 불가능하거나 모호한 계획을 수립하는 행위.