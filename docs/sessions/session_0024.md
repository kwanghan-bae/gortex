# Session 0024

## Goal
- 지식 계보 시각화 및 추론 근거 노출 (Knowledge Lineage UI v1)

## What Was Done
- **utils/vector_store.py 수정**: `recall` 메서드가 단순 텍스트 대신 메타데이터(source, score 등)를 포함한 구조화된 객체를 반환하도록 개선.
- **agents/manager.py 수정**: 소환된 지식의 메타데이터를 추출하여 `knowledge_lineage` 필드에 담아 UI로 전달하는 로직 구현.
- **ui/dashboard.py 수정**: 사이드바 `SYSTEM STATUS` 패널 내에 현재 판단의 근거가 된 지식 출처와 유사도 점수를 시각적으로 표시하는 섹션 추가.
- **main.py 연동**: 에이전트의 지식 계보 정보를 실시간으로 캡처하여 UI에 반영하도록 통합.

## Decisions
- 정보 과부하를 방지하기 위해 가장 관련성이 높은 상위 2개의 지식 출처만 요약하여 노출하기로 함.
- 지식 출처는 Magenta 기울임꼴 스타일을 적용하여 시스템의 내적/외적 지식임을 명확히 구분함.

## Problems / Blockers
- 현재 3D 그래프에서의 노드 간 동적 연결(Edges) 강화는 웹 클라이언트 측의 렌더링 로직 수정이 추가로 필요함. 현재는 데이터 구조만 확보된 상태.

## Notes for Next Session
- 시스템의 '사회적 지성'을 완성하기 위해, 에이전트들이 작업 도중 발생한 모든 의사결정과 지식 활용 내역을 바탕으로 사용자의 다음 행동을 예측하여 미리 제안하는 'Predictive Next-Action' 기능이 필요함.
