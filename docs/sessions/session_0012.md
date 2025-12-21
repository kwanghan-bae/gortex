# Session 0012

## Goal
- 아키텍처 및 정책 준수 실시간 검증 (Constraint Validator v1)

## What Was Done
- **agents/analyst.py 수정**: 현재 활성화된 제약 조건(`active_constraints`)과 에이전트의 도구 호출을 대조 분석하여 위반 여부를 판정하는 `validate_constraints` 메서드 구현.
- **agents/coder.py 수정**: 도구를 실행하기 직전(`function_calls` 처리 시점)에 Analyst의 검증을 거치도록 워크플로우 연동. 위반 시 즉시 실행을 차단하고 사유와 해결책을 보고함.
- **연속성 확보**: 이제 시스템 규칙은 단순한 참고 자료를 넘어, 실행 시점에 강제되는 'Hard Constraint'로 작동함.

## Decisions
- 검증 로직은 Gemini 1.5 Flash 모델을 사용하여 지연 시간을 최소화하고, "Compliance Officer" 페르소나를 통해 엄격한 잣대를 적용함.
- 위반 사유뿐만 아니라 '해결책(Remedy)'을 함께 제시하여 에이전트가 스스로 교정할 수 있도록 함.

## Problems / Blockers
- 복잡한 비즈니스 규칙의 경우 단순 텍스트 매칭만으로는 검증에 한계가 있을 수 있음. 향후 특정 코드 패턴을 정의하는 정규식이나 AST 기반 검증 규칙 도입 검토 필요.

## Notes for Next Session
- 시스템의 '사회적 지능'을 강화하기 위해, 에이전트들이 작업 도중 발생한 의사결정의 트레이드오프를 사용자에게 질문하고 답변을 학습하는 'Interactive Decision Learning' 기능이 필요함.
