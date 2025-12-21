# Session 0025

## Goal
- 사용자의 다음 행동 예측 및 선제적 제안 (Predictive Next-Action v1)

## What Was Done
- **agents/analyst.py 수정**: 현재 대화 맥락과 작업 진행 상황을 분석하여 사용자에게 제안할 다음 행동 3가지를 예측하는 `predict_next_actions` 메서드 구현.
- **ui/dashboard.py 수정**: 사이드바 `SYSTEM STATUS` 패널에 예측된 다음 행동을 "🚀 Next?" 레이블과 함께 표시하는 시각화 로직 추가.
- **main.py 연동**: 매 턴 에이전트 루프 종료 시마다 실시간으로 사용자의 의도를 예측하고 이를 UI에 스트리밍하도록 통합.

## Decisions
- 사용자의 작업 흐름을 방해하지 않도록 '제안'의 형태를 취하며, 강제적인 자동 실행은 배제함.
- 예측 결과는 아이콘과 함께 직관적인 번호 리스트로 제공하여 사용자가 쉽게 명령어로 입력할 수 있도록 유도함.

## Problems / Blockers
- 현재 예측은 텍스트 기반 맥락 분석에 의존함. 향후 사용자의 '과거 명령어 히스토리'를 통계적으로 분석하는 로직을 결합하면 정확도가 더욱 향상될 것으로 기대됨.

## Notes for Next Session
- 시스템의 '지적 통합'을 완성하기 위해, 현재 텍스트로 저장되는 장기 기억들을 상호 연결하여 의미론적 지도를 그리는 'Knowledge Relation Mapping' 및 시각화 고도화가 필요함.
