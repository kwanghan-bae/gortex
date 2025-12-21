# Session 0014

## Goal
- 인터랙티브 의사결정 학습 및 사용자 선호도 모델링 (Decision Learning v1)

## What Was Done
- **agents/analyst.py 수정**: 에이전트의 질문과 사용자의 답변을 분석하여 개인화된 선호도 규칙을 추출하는 `learn_from_interaction` 메서드 구현.
- **agents/manager.py 수정**: `response_schema`에 `requires_user_input` 및 `question_to_user` 필드 추가. 불확실하거나 트레이드오프가 큰 상황에서 사용자에게 개입을 요청하도록 지침 보강.
- **main.py 수정**: `last_question` 변수를 통한 질문 추적 및 다음 턴의 사용자 입력을 분석하여 실시간으로 선호도 규칙을 학습하는 루프 연동.

## Decisions
- 사용자의 모든 답변이 지식화되는 것을 방지하기 위해, `Analyst`가 '취향', '기술 스택', '작업 방식'과 관련된 핵심 정보만 선별하여 규칙으로 변환하도록 함.
- 질문 발생 시 에이전트는 작업을 일시 중단하고 사용자의 명시적인 피드백을 기다리는 동기식 상호작용 모델을 채택함.

## Problems / Blockers
- 현재 터미널 환경에서는 질문이 채팅 기록 사이에 섞여 있어 사용자가 놓칠 수 있음. 향후 UI 개선을 통해 '에이전트의 질문'을 별도 패널로 분리하거나 하이라이트 처리 필요.

## Notes for Next Session
- 시스템의 '물리적 지능'을 강화하기 위해, 현재 프로젝트의 파일들 간의 의존성 및 호출 관계를 그래프로 시각화하고, 특정 파일 수정 시 영향을 받는 범위를 예측하는 'Dependency Impact Analyzer' 기능이 필요함.
