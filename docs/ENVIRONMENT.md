# 💻 Project Environment & Tooling: gortex

---

## 1. Core Stack Versions
- **Java**: 21 (Temurin)
- **Kotlin**: 1.9.23
- **React Native (Expo)**: ~54.0.30 (Custom build)
- **Node.js**: 22.16.0

## 2. Infrastructure
- **Database**: PostgreSQL (Supabase)
- **Backend Server**: Docker on Render
- **Frontend Server**: Static hosting on Render

## 3. Tooling Constraints
- 모든 코드는 `pre_commit.sh` 빌드 가드를 통과해야 함.
- Expo Web Export 환경의 호환성을 항상 고려해야 함.