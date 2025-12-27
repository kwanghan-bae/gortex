# Next Session

## Session Goal
- **Local CLI Bootstrap**: `claude-code` 수준의 사용자 경험을 제공하는 로컬 터미널 인터페이스(`gortex-cli`) 구축.

## Context
- 사용자의 전략 변경 요청: 분산/Swarm 기능 개발을 잠시 중단하고, 로컬에서 즉시 사용 가능한 강력한 CLI 도구 개발에 집중.
- 벤치마크: `claude-code` (REPL, 컨텍스트 인식, 파일 직접 수정, 안전 모드).

## Scope
### Do
- `cli.py` 기반의 `typer` 애플리케이션 스캐폴딩.
- `Rich` 라이브러리를 활용한 이쁘고 가독성 높은 TUI(Text User Interface).
- REPL(Read-Eval-Print Loop) 내에서 LLM과 대화하며 도구(파일 읽기/쓰기, 쉘 실행) 실행.
- **Safety**: 도구 실행 시 사용자 승인(Y/n) 절차 구현.
### Do NOT
- 복잡한 Swarm(집단 지성) 로직이나 Redis 의존성.
- 웹 대시보드 연동.

## 🏁 Documentation Sync Checklist
- [ ] `SPEC_CATALOG.md` (CLI 기능 명세 추가)
- [ ] `TECHNICAL_SPEC.md` (CLI 아키텍처 추가)

## Completion Criteria
- 터미널에서 `python cli.py chat` 실행 시 대화형 인터페이스 진입.
- 사용자가 "README.md 읽어서 요약해줘"라고 하면 `read_file` 도구를 사용하여 수행.
- 사용자가 "새로운 파일 hello.py 만들어줘"라고 하면 `write_file` 도구 승인 요청 후 수행.