---
description: 작업을 완료하기 전 시스템 무결성을 확인합니다.
---

모든 코딩 작업이나 버그 수정이 완료된 후, 사용자에게 보고하기 전에 반드시 다음 단계를 수행해야 합니다.

1. `scripts/preflight_check.sh`를 실행하여 모든 테스트를 통과하는지 확인합니다.
// turbo
```bash
./scripts/preflight_check.sh
```

2. 만약 하나라도 실패한다면, 해당 문제를 해결하고 다시 1단계를 수행합니다.
3. 모든 테스트가 통과(`PRE-FLIGHT CHECK PASSED`)된 후에만 `walkthrough.md`를 업데이트하고 완료 보고를 진행합니다.
