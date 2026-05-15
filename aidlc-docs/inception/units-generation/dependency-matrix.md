# V-Suitcase — Unit Dependency Matrix

## Dependency Graph

```
unit-core (기반)
  |
  +-- unit-auth (인증)
  |     |
  |     +-- unit-fitting (피팅) ----+
  |     |     |                     |
  |     |     +-- unit-background   +-- unit-result (결과/공유)
  |     |     |                     |
  |     |     +-- unit-recommend ---+
  |     |
  |     (모든 유닛은 unit-auth에 의존)
```

## Dependency Matrix

| Unit | Depends On | Blocked By | Blocks |
|------|-----------|------------|--------|
| unit-core | - | - | unit-auth, unit-fitting, unit-background, unit-recommend, unit-result |
| unit-auth | unit-core | unit-core | unit-fitting, unit-background, unit-recommend, unit-result |
| unit-fitting | unit-core, unit-auth | unit-core, unit-auth | unit-background, unit-recommend, unit-result |
| unit-background | unit-core, unit-auth, unit-fitting | unit-fitting | unit-result |
| unit-recommend | unit-core, unit-auth, unit-fitting | unit-fitting | unit-result |
| unit-result | unit-core, unit-auth, unit-fitting | unit-fitting, unit-background, unit-recommend | - |

## Build Order (구현 순서)

```
Phase 1: unit-core        (독립, 기반 구조)
Phase 2: unit-auth        (unit-core 완료 후)
Phase 3: unit-fitting     (unit-auth 완료 후)
Phase 4: unit-background  (unit-fitting 완료 후, unit-recommend와 병렬 가능)
Phase 4: unit-recommend   (unit-fitting 완료 후, unit-background와 병렬 가능)
Phase 5: unit-result      (unit-background, unit-recommend 완료 후)
```

## Interface Contracts

### unit-core → unit-auth
- DB session 제공
- 공통 설정 (Cognito pool ID, region 등)
- FileManagerService 인스턴스

### unit-auth → unit-fitting
- 인증 미들웨어 (토큰 검증 데코레이터)
- 현재 사용자 정보 (user_id, face_registered)

### unit-fitting → unit-background
- fitting_task_id (피팅 완료된 결과 참조)
- 피팅 결과 이미지 임시 경로

### unit-fitting → unit-recommend
- fitting_task_id
- 피팅 결과 이미지 임시 경로 (체형 분석용)

### unit-fitting/background/recommend → unit-result
- task_id (결과 이미지 참조)
- 임시 파일 경로
