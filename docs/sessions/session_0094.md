# Session 0094: Automated API Key Health Check & Rotation

## 📅 Date
2025-12-22

## 🎯 Goal
- **Automated API Key Health Check & Rotation**: API 할당량 소진 상황에 지능적으로 대응하여 시스템 중단 없이 지속 가능한 모델 공급 체계를 구축함.

## 📝 Activities
### 1. Key Pool & Cooldown System
- `core/auth.py`: `APIKeyInfo` 데이터 클래스 도입. 키별 상태(Alive, Cooldown), 실패 횟수, 쿨다운 만료 시간을 관리.
- `report_key_failure`: 429 에러 발생 시 해당 키를 쿨다운 상태로 전환하고, 실패 횟수에 비례하여 격리 시간을 증가시킴.

### 2. Intelligent Key Selection
- `_get_available_gemini_key`: 매 요청 전 쿨다운이 만료된 키를 자동으로 활성화하고, 현재 가장 건강한 키를 선택하여 반환.
- 기존의 단순 순차 로테이션에서 탈피하여 '가용성 중심' 로테이션으로 진화.

### 3. Verification
- `tests/test_auth_rotation.py`: 429 발생 시 즉시 다른 키로 전환되는지, 모든 키 소진 시 OpenAI로 정상 폴백되는지 검증 완료.

## 📈 Outcomes
- **System Resilience**: API 한 개가 막혀도 시스템 전체가 멈추지 않고 유연하게 대응 가능.
- **Reliability**: 이미 소진된 키를 반복 호출하여 발생하는 불필요한 대기 시간 및 에러 로그 최소화.

## ⏭️ Next Steps
- **Session 0095**: Energy Recovery & Maintenance Mode.
- 저에너지 상황(30% 미만)에서 시스템이 스스로 휴식하며 에너지를 회복하는 '유지보수 모드' 구현 및 아이들(Idle) 시간 동안의 자가 치유 강화.
