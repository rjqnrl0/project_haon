# V-Suitcase — Application Design Summary

## Architecture Overview

```
+---------------------------------------------------+
|              S3 + CloudFront (CDN)                 |
|              React + Tailwind + Vite              |
+------------------------+--------------------------+
                         | HTTPS API
                         v
+---------------------------------------------------+
|              AWS Cognito (Auth)                    |
+---------------------------------------------------+
                         |
                         v
+---------------------------------------------------+
|              EC2 — FastAPI Backend                 |
|                                                   |
|  +-------------+  +------------------+            |
|  | AuthService |  | FileManagerService|           |
|  +------+------+  +--------+---------+            |
|         |                   |                     |
|  +------v------+  +--------v---------+            |
|  | FaceVerify  |  | FittingService   |            |
|  | Service     |  | BackgroundService|            |
|  +-------------+  | RecommendService |            |
|                   | ShareService     |            |
|                   +------------------+            |
+------------------------+--------------------------+
                         |
              +----------+----------+
              |                     |
              v                     v
+-------------------+  +------------------------+
| RDS PostgreSQL    |  | AI Services (Mock/Real)|
| - user_profiles   |  | - Rekognition          |
| - face_references |  | - Stability AI         |
| - fitting_tasks   |  | - Claude Opus 4.6      |
| - share_links     |  | - Weather API          |
+-------------------+  +------------------------+
```

## Database Schema (PostgreSQL)

### users
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | PK |
| cognito_sub | VARCHAR | Cognito 사용자 ID |
| email | VARCHAR | 이메일 |
| face_registered | BOOLEAN | Face ID 등록 여부 |
| face_reference_key | VARCHAR | Rekognition face ID |
| created_at | TIMESTAMP | 가입일 |

### fitting_tasks
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | PK |
| user_id | UUID | FK → users |
| status | VARCHAR | pending/processing/completed/failed |
| clothing_category | VARCHAR | 상의/하의/원피스/아우터/액세서리 |
| created_at | TIMESTAMP | 생성일 |
| expires_at | TIMESTAMP | 임시 파일 만료 시간 |

### share_links
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | PK |
| task_id | UUID | FK → fitting_tasks |
| share_url | VARCHAR | 공유 URL 경로 |
| expires_at | TIMESTAMP | 만료 시간 (24h) |
| created_at | TIMESTAMP | 생성일 |

## Key Design Decisions

| 결정 | 이유 |
|------|------|
| 이미지 서버 휘발성 | 사용자 프라이버시 보호, 클라우드 저장 지양 |
| Mock API first | UI 빠르게 완성 후 AI 연동으로 점진적 전환 |
| Task-based 비동기 처리 | 이미지 생성 7초 이상 소요 가능, 폴링 방식 |
| Cognito + Face ID 이중 인증 | 계정 인증 + 본인 사진 확인 분리 |
| 단일 EC2 백엔드 | MVP 단계 단순성, 이후 분리 가능 |

## Technology Choices

| Category | Choice | Rationale |
|----------|--------|-----------|
| Frontend State | Zustand | 경량, 간단한 API |
| HTTP Client | Axios | 인터셉터로 토큰 자동 첨부 |
| Form Handling | React Hook Form | 경량, 성능 좋음 |
| Image Processing (BE) | Pillow | 워터마크, 리사이즈 |
| Task Queue | Background Tasks (FastAPI) | MVP에 충분, 이후 Celery 전환 가능 |
| Temp File | Python tempfile + cron cleanup | 단순하고 신뢰성 있음 |
