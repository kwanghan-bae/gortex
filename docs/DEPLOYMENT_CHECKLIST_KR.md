# 최종 배포 체크리스트

## 1. 백엔드 배포 (서버 & DB)
- [ ] **데이터베이스:** Supabase 프로젝트 생성 및 `DB_URL`, `DB_USERNAME`, `DB_PASSWORD` 확인.
- [ ] **코드:** 최신 코드를 GitHub에 푸시.
- [ ] **서버:** GitHub 저장소와 연결된 Render Web Service 생성.
- [ ] **환경 변수:** Render에서 `SPRING_PROFILES_ACTIVE=prod` 및 DB 자격 증명 설정.
- [ ] **검증:** 빌드 완료 대기 및 Render URL 확인 (예: `https://backend-api.onrender.com`).

## 2. 프론트엔드 연결
- [ ] **설정 업데이트:** `lib/utils/api_config.dart` 파일 열기.
- [ ] **URL 변경:** `https://api.cloverwallet.com` 부분을 Render URL로 변경.
- [ ] **커밋:** 변경 사항 커밋 (`git commit -am "Update API URL"`).

## 3. 출시
- [ ] **빌드:** `flutter build apk` (Android) 또는 `flutter build ios` (iOS) 실행.
