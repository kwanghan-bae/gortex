# Next Session

## Session Goal
- **Project Onboarding Automation & Documentation Overhaul**: 기획자(PM)나 비개발 직군도 쉽게 사용할 수 있도록 `README.md`를 전면 개편하고, 설치 및 실행 과정을 '원클릭' 수준으로 자동화한다.

## Context
- 현재 `README.md`는 개발자 친화적이지만, 기획자가 접근하기엔 여전히 장벽이 있음.
- 사용자가 "기획자도 사용할 수 있는 상세 가이드"와 "자동화된 준비"를 명시적으로 요청함.
- "자리를 비운다"는 시나리오에 맞춰, 누구나 프로젝트에 들어왔을 때 즉시 실행 가능한 상태(Ready-to-Use)를 보장해야 함.

## Scope
### Do
- `README.md`: 섹션 재구성 (소개 -> 설치 -> 가이드 -> FAQ). 비유와 시각적 요소(이모지)를 활용하여 친절하게 작성.
- `setup.sh`: Python 버전 감지 강화, API 키 입력 시 공백 제거 등 내구성 강화.
- `docs/GUIDE_FOR_PM.md`: 기획자를 위한 전용 가이드 문서 신설 (선택 사항이나 README에 통합 권장).

### Do NOT
- 시스템의 핵심 로직을 건드리지 않음.

## Expected Outputs
- `README.md` (Refined)
- `setup.sh` (Hardened)

## Completion Criteria
- `README.md`만 보고도 비개발자가 설치부터 실행까지 막힘없이 진행할 수 있어야 함.
- `docs/sessions/session_0083.md` 기록.