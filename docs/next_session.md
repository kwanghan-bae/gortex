# Next Session

## Session Goal
- **Autonomous Log Summarization & Archiving**: 세션이 반복되면서 비대해진 `trace.jsonl` 로그 파일에서 시스템 진화에 기여한 핵심 사건(교훈, 패턴, 주요 오류 해결)만 지능적으로 추출하여 `logs/trace_summary.md`에 보존하고, 원본 로그는 주기적으로 압축 아카이빙하여 시스템 성능을 유지한다.

## Context
- 현재 로그는 `GortexObserver`에 의해 지속적으로 누적되지만, 데이터 양이 많아질수록 조회 속도가 느려지고 모델의 인지 범위를 초과함.
- `Analyst`가 정기적으로 로그를 스캔하여 미래에 도움이 될 '압축된 역사'를 남기도록 함.
- 이는 단순한 백업을 넘어, 시스템의 과거를 자산화하는 과정임.

## Scope
### Do
- `agents/analyst/base.py`: 로그 파일을 분석하여 핵심 타임라인과 통찰을 추출하는 `summarize_system_trace` 구현.
- `core/observer.py`: 로그 아카이빙(ZIP 압축 및 순환)을 담당하는 `archive_and_reset_logs` 메서드 보강.
- `utils/tools.py`: 로그 요약본을 마크다운 형식으로 미려하게 생성하는 템플릿 지원.

### Do NOT
- 모든 로그 엔트리를 요약하지 않음 (중요도 점수가 높은 이벤트 위주).

## Expected Outputs
- `agents/analyst/base.py` (Trace Summarizer)
- `logs/trace_summary.md` (New Historical Artifact)
- `tests/test_log_summarization.py` (New)

## Completion Criteria
- `/history` 명령 시, 거대한 원본 로그 대신 정제된 `trace_summary.md`의 내용을 우선적으로 보여주어야 함.
- 10MB 이상의 로그 파일이 존재할 때, 아카이빙 후 원본 파일 크기가 0으로 리셋되어야 함.
- `docs/sessions/session_0111.md` 기록.
