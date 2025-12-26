# Next Session

## Session Goal
- **Swarm-Driven Self-Healing Loop**: 시스템 오류 발생 시 Swarm 토론을 통해 최적의 패치 안을 도출하고, 이를 `Coder`가 실행한 뒤 `Analyst`가 최종 승인하는 '완전 자율 복구 루프'의 지능화 및 안정성 확보.

## Context
- 에이전트 경제 시스템과 기술 트리가 완성되어, 이제 각 분야의 전문가들을 선발하여 복잡한 디버깅 과제를 해결할 수 있는 기반이 마련됨.
- Swarm 토론의 합의안이 Super Rule로 저장되는 기능과 연동하여, 한 번 해결된 버그가 다시는 발생하지 않도록 지식 베이스를 공고히 함.

## Scope
### Do
- `agents/swarm.py`의 디버그 모드 시나리오 고도화.
- `Analyst`의 오류 원인 분석(RCA) 데이터와 Swarm 토론의 연동 강화.
- 복구 성공 시 파격적인 스킬 포인트 보상 체계 적용.
### Do NOT
- LLM 백엔드의 기본 API 구조 변경.

## 🏁 Documentation Sync Checklist
- [ ] `SPEC_CATALOG.md` (Swarm Debug 시나리오 반영)
- [ ] `TECHNICAL_SPEC.md` (오류 복구 상태 전이도 업데이트)

## Completion Criteria
- 의도적으로 발생시킨 `ZeroDivisionError`를 Swarm이 감지, 토론을 통해 방어 코드를 작성하고, 이후 해당 오류가 다시 발생하지 않음을 증명.
- 복구에 기여한 에이전트들의 'Analysis' 및 'Coding' 스킬 점수가 가중치에 따라 정상 반영됨.