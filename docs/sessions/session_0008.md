# Session 0008

## Goal
- 실시간 API 문서 학습 및 기술 활용 (Live Documentation Learning v1)

## What Was Done
- **agents/researcher.py 수정**: 특정 라이브러리의 공식 문서를 정밀 스캔하고 요약하는 `fetch_api_docs` 고도화. 수집된 정보를 `LongTermMemory`에 "LiveDocs" 출처와 함께 저장하도록 개선.
- **agents/planner.py 수정**: 계획 수립 시 특정 라이브러리 사용 요청이 있을 경우 `researcher`를 통한 사전 문서 학습 단계를 반드시 포함하도록 지침 강화.
- **연속성 확보**: 이제 Coder는 자신이 써본 적 없는 라이브러리라도 Researcher가 가져온 최신 지식을 바탕으로 정확하게 코딩할 수 있게 됨.

## Decisions
- 실시간 문서는 `LongTermMemory`에 저장되어 세션 간 공유되며, 이를 통해 동일한 라이브러리에 대한 중복 검색을 방지함.
- Planner는 지식 베이스를 먼저 확인하고, 최신 정보가 없을 때만 검색 계획을 세우도록 유도함.

## Problems / Blockers
- 웹 스크래핑 시 사이트의 레이아웃이 복잡할 경우 핵심 정보 추출에 실패할 수 있음. 향후 특정 기술 문서 사이트(ReadDocs 등)에 최적화된 파서 추가 고려.

## Notes for Next Session
- 시스템의 '자가 수정' 지능을 높이기 위해, 테스트 실패 시 오류 메시지를 분석하여 해결책을 '추론'하고 이를 '경험 규칙'으로 자동 변환하는 'Self-Correction Evolution' 강화가 필요함.
