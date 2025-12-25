# gortex Development Workflow

이 프로젝트는 AI의 자율성과 무결성을 보장하는 고도화된 워크플로우를 따릅니다.

---

## 1. 세션의 시작 (Bootstrap)
당신은 진입 시 가장 먼저 **`docs/AWAKENING_PROTOCOL.md`**를 읽고 인지 상태를 동기화해야 합니다.

## 2. 작업 사이클 (The Development Loop)

### 1단계: 설계 (Thinking)
- `docs/SCRATCHPAD.md`를 열어 현재 목표에 대한 설계 초안, 의존성 영향, 리스크를 분석하고 기록합니다.

### 2단계: 구현 (TDD)
- **Red**: 먼저 실패하는 테스트를 작성합니다.
- **Green**: 테스트를 통과하기 위한 최소한의 코드를 작성합니다.
- **Refactor**: 중복을 제거하고 스타일을 정돈합니다.

### 3단계: 검증 (Verification)
- `scripts/pre_commit.sh`를 실행하여 나태함 패턴, 문서 부채, 모든 테스트 패스 여부를 확인합니다.

### 4단계: 자율 커밋 (Commit)
- **모든 검증 통과 시 사용자의 승인 없이도 스스로 커밋을 수행합니다.**
- 커밋 메시지는 한국어로 `type: 요약 (상세)` 형식을 따릅니다.

### 5단계: 기록 (Archive)
- `docs/sessions/session_XXXX.md`를 작성하여 이번 세션의 활동과 배운 점(Lessons Learned)을 기록합니다.
- `next_session.md`를 업데이트하여 다음 AI 주자에게 목표를 넘깁니다.
