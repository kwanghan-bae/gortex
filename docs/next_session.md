# Next Session

## Session Goal
- **Automated Regression Test Generation & Validation**: 영향력 분석 결과 위험도가 높거나 테스트 커버리지가 낮은 지역을 시스템이 스스로 식별하고, 해당 지역의 기능을 검증하는 유닛 테스트를 자동으로 생성 및 실행하여 리팩토링의 무결성을 자율적으로 보장한다.

## Context
- 현재 Gortex는 기존 테스트에 의존하여 회귀 테스트를 수행함.
- 하지만 영향력이 큰 핵심 함수 수정 시, 연결된 모든 지점을 테스트할 수 있는 충분한 케이스가 부족한 경우가 많음.
- `Analyst`가 `SynapticIndexer`와 연동하여 '취약 구역'을 찾아내고, `Coder`에게 테스트 작성을 지시하는 자율 방어 루프가 필요함.

## Scope
### Do
- `agents/analyst/base.py`: 영향력 지도를 기반으로 테스트가 필요한 'Hotspot'을 제안하는 `identify_test_hotspots` 로직 추가.
- `agents/coder.py`: 요구사항에 맞춰 자동으로 테스트 코드를 생성하고 `tests/`에 안착시키는 프롬프트 강화.
- `core/engine.py`: 자동 생성된 테스트를 즉시 실행하고 결과를 보고하는 `SelfTestingLoop` 통합.

### Do NOT
- 실제 프로덕션 데이터 기반의 테스트 생성은 배제 (순수 로직/모킹 기반 테스트).

## Expected Outputs
- `agents/analyst/base.py` (Hotspot Detection)
- `agents/coder.py` (Auto Test Generation)
- `tests/test_auto_patching.py` (New Integration Test)

## Completion Criteria
- 특정 핵심 함수를 입력했을 때, 해당 함수를 호출하는 상위 모듈 중 테스트가 없는 곳을 1개 이상 찾아내야 함.
- 자동으로 생성된 테스트 파일이 `python -m unittest`를 성공적으로 통과해야 함.
- `docs/sessions/session_0122.md` 기록.