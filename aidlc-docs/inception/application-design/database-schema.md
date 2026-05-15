# V-Suitcase — Database Schema (PostgreSQL)

## ERD Overview

```
+----------------+       +------------------+       +----------------+
|     users      |       |  fitting_tasks   |       |  share_links   |
+----------------+       +------------------+       +----------------+
| id (PK)        |<---+  | id (PK)          |<---+  | id (PK)        |
| cognito_sub    |    |  | user_id (FK)     |    |  | task_id (FK)   |
| email          |    +--| ...              |    +--| ...            |
| nickname       |       +------------------+       +----------------+
| face_registered|
| face_ref_key   |       +------------------+
| created_at     |       | weather_requests |
| updated_at     |       +------------------+
+----------------+       | id (PK)          |
                         | user_id (FK)     |
                         | ...              |
                         +------------------+
```

---

## Table: users

사용자 계정 및 Face ID 정보

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | NOT NULL | gen_random_uuid() | PK |
| cognito_sub | VARCHAR(128) | NOT NULL | - | AWS Cognito 사용자 고유 ID |
| email | VARCHAR(255) | NOT NULL | - | 이메일 주소 (unique) |
| nickname | VARCHAR(50) | NULL | - | 표시 이름 |
| face_registered | BOOLEAN | NOT NULL | false | Face ID 등록 완료 여부 |
| face_reference_key | VARCHAR(255) | NULL | - | Rekognition에 저장된 Face ID 참조 키 |
| created_at | TIMESTAMP WITH TZ | NOT NULL | NOW() | 가입 일시 |
| updated_at | TIMESTAMP WITH TZ | NOT NULL | NOW() | 최종 수정 일시 |

**Indexes:**
- `idx_users_cognito_sub` UNIQUE ON (cognito_sub)
- `idx_users_email` UNIQUE ON (email)

**Constraints:**
- PK: id
- UNIQUE: cognito_sub, email

---

## Table: fitting_tasks

가상 피팅 작업 추적 (이미지 자체는 서버 임시 저장)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | NOT NULL | gen_random_uuid() | PK |
| user_id | UUID | NOT NULL | - | FK → users.id |
| status | VARCHAR(20) | NOT NULL | 'pending' | pending / processing / completed / failed |
| task_type | VARCHAR(20) | NOT NULL | 'fitting' | fitting / background |
| clothing_category | VARCHAR(20) | NULL | - | 상의/하의/원피스/아우터/액세서리 |
| background_prompt | TEXT | NULL | - | 배경 생성 텍스트 프롬프트 (배경 생성 시) |
| result_file_path | VARCHAR(500) | NULL | - | 서버 임시 결과 파일 경로 |
| error_message | TEXT | NULL | - | 실패 시 에러 메시지 |
| created_at | TIMESTAMP WITH TZ | NOT NULL | NOW() | 작업 생성 일시 |
| completed_at | TIMESTAMP WITH TZ | NULL | - | 작업 완료 일시 |
| expires_at | TIMESTAMP WITH TZ | NOT NULL | NOW() + 1h | 임시 파일 만료 시간 |

**Indexes:**
- `idx_fitting_tasks_user_id` ON (user_id)
- `idx_fitting_tasks_status` ON (status)
- `idx_fitting_tasks_expires_at` ON (expires_at) — 만료 파일 정리 cron용

**Constraints:**
- PK: id
- FK: user_id → users(id) ON DELETE CASCADE
- CHECK: status IN ('pending', 'processing', 'completed', 'failed')
- CHECK: task_type IN ('fitting', 'background')

---

## Table: share_links

SNS 공유용 임시 링크 (24시간 만료)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | NOT NULL | gen_random_uuid() | PK |
| task_id | UUID | NOT NULL | - | FK → fitting_tasks.id |
| share_token | VARCHAR(64) | NOT NULL | - | 공유 URL에 사용되는 고유 토큰 |
| watermarked_path | VARCHAR(500) | NULL | - | 워터마크 적용된 임시 이미지 경로 |
| view_count | INTEGER | NOT NULL | 0 | 조회 수 |
| created_at | TIMESTAMP WITH TZ | NOT NULL | NOW() | 생성 일시 |
| expires_at | TIMESTAMP WITH TZ | NOT NULL | NOW() + 24h | 만료 시간 |

**Indexes:**
- `idx_share_links_token` UNIQUE ON (share_token)
- `idx_share_links_expires_at` ON (expires_at) — 만료 링크 정리 cron용

**Constraints:**
- PK: id
- FK: task_id → fitting_tasks(id) ON DELETE CASCADE
- UNIQUE: share_token

---

## Table: weather_requests

날씨 코디 추천 요청 기록

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | NOT NULL | gen_random_uuid() | PK |
| user_id | UUID | NOT NULL | - | FK → users.id |
| city_name | VARCHAR(100) | NOT NULL | - | 여행지 도시명 |
| country_code | VARCHAR(5) | NULL | - | 국가 코드 (KR, JP 등) |
| temperature | DECIMAL(5,2) | NULL | - | 조회 당시 기온 (C) |
| weather_condition | VARCHAR(50) | NULL | - | 날씨 상태 (맑음, 흐림, 비 등) |
| recommendation_text | TEXT | NULL | - | AI 생성 코디 추천 텍스트 |
| created_at | TIMESTAMP WITH TZ | NOT NULL | NOW() | 요청 일시 |

**Indexes:**
- `idx_weather_requests_user_id` ON (user_id)

**Constraints:**
- PK: id
- FK: user_id → users(id) ON DELETE CASCADE

---

## Table: size_recommendations

사이즈 추천 기록

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | NOT NULL | gen_random_uuid() | PK |
| user_id | UUID | NOT NULL | - | FK → users.id |
| task_id | UUID | NOT NULL | - | FK → fitting_tasks.id |
| shoulder_analysis | TEXT | NULL | - | 어깨선 분석 결과 |
| waist_analysis | TEXT | NULL | - | 허리선 분석 결과 |
| recommended_size | VARCHAR(10) | NULL | - | 추천 사이즈 (XS/S/M/L/XL 등) |
| recommendation_text | TEXT | NULL | - | AI 생성 사이즈 조언 텍스트 |
| created_at | TIMESTAMP WITH TZ | NOT NULL | NOW() | 생성 일시 |

**Indexes:**
- `idx_size_recommendations_user_id` ON (user_id)
- `idx_size_recommendations_task_id` ON (task_id)

**Constraints:**
- PK: id
- FK: user_id → users(id) ON DELETE CASCADE
- FK: task_id → fitting_tasks(id) ON DELETE CASCADE

---

## Cleanup Policies (임시 데이터 정리)

| 대상 | 정리 조건 | 방식 |
|------|-----------|------|
| fitting_tasks.result_file_path | expires_at < NOW() | Cron job (매 10분) — 파일 삭제 + status 업데이트 |
| share_links | expires_at < NOW() | Cron job (매 1시간) — 워터마크 파일 삭제 + row 삭제 |
| 업로드 임시 파일 | 처리 완료 후 즉시 | 코드 내 finally 블록 |

---

## Migration Strategy

```
migrations/
  001_create_users.sql
  002_create_fitting_tasks.sql
  003_create_share_links.sql
  004_create_weather_requests.sql
  005_create_size_recommendations.sql
```

ORM: **SQLAlchemy** (with Alembic for migrations)
