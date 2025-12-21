# Next Session

## Session Goal
- 파일 수정 영향 범위 분석 및 시각화 (Dependency Impact Analyzer v1)

## Context
- 시스템이 복잡해짐에 따라, 한 파일을 수정했을 때 예상치 못한 모듈에서 버그가 발생하는 리스크가 커지고 있음.
- `Synaptic Map`과 `Call Graph` 데이터를 활용하여, 특정 파일 수정 시 직접/간접적으로 영향을 받는 파일 목록을 추출하고 이를 대시보드에 경고로 표시해야 함.

## Scope
### Do
- `utils/indexer.py` (또는 관련 로직)를 확장하여 파일 간 의존성 역추적 로직 구현.
- `agents/planner.py`에서 계획 수립 시 '영향 범위 분석' 단계를 포함하고, 위험 모듈을 보고함.
- 웹 대시보드 3D 그래프에서 영향 받는 노드들을 붉게 하이라이트 처리하는 데이터 스트리밍.

### Do NOT
- 단순 Import 관계뿐만 아니라 실제 함수 호출 관계까지 고려할 것.

## Expected Outputs
- `utils/indexer.py`, `agents/planner.py`, `main.py` 수정.

## Completion Criteria
- 특정 파일 수정 계획이 수립될 때, 그로 인해 영향을 받는 다른 파일 목록이 로그와 대시보드에 명확히 표시되는 것이 확인되어야 함.
