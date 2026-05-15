# unit-core — Business Logic Specification

## 1. Application Configuration (설정 관리)

### 1.1 Configuration Schema

AWS Secrets Manager + Parameter Store 기반 설정 관리.

**Parameter Store (비밀이 아닌 설정):**
| Parameter Path | Description | Example |
|---------------|-------------|---------|
| `/v-suitcase/{env}/db/host` | RDS 호스트 | `v-suitcase-db.xxxxx.rds.amazonaws.com` |
| `/v-suitcase/{env}/db/port` | RDS 포트 | `5432` |
| `/v-suitcase/{env}/db/name` | DB 이름 | `vsuitcase` |
| `/v-suitcase/{env}/cognito/pool-id` | Cognito Pool ID | `ap-northeast-2_xxxxx` |
| `/v-suitcase/{env}/cognito/client-id` | Cognito Client ID | `xxxxxxxxxx` |
| `/v-suitcase/{env}/s3/temp-bucket` | 임시 파일 S3 버킷 | `v-suitcase-temp-dev` |
| `/v-suitcase/{env}/s3/region` | AWS 리전 | `ap-northeast-2` |
| `/v-suitcase/{env}/file/expiry-hours` | 임시 파일 만료 시간 | `1` |

**Secrets Manager (비밀 값):**
| Secret Name | Keys | Description |
|-------------|------|-------------|
| `/v-suitcase/{env}/db-credentials` | `username`, `password` | RDS 접속 정보 |
| `/v-suitcase/{env}/cognito-secret` | `client_secret` | Cognito 앱 클라이언트 시크릿 |

### 1.2 Configuration Loading Logic

```
앱 시작 시:
1. ENV 환경변수로 현재 환경 결정 (dev / staging / prod)
2. boto3로 Parameter Store에서 prefix 기반 일괄 조회
3. boto3로 Secrets Manager에서 시크릿 조회
4. Pydantic Settings 모델에 매핑하여 유효성 검증
5. 실패 시 앱 시작 중단 + 에러 로그
```

### 1.3 Local Development Override

로컬 개발 시 `.env` 파일로 오버라이드 가능:
- `.env` 파일이 존재하면 AWS 호출 스킵
- `ENV=local` 일 때만 `.env` 파일 사용
- `.env.example` 템플릿 제공

---

## 2. Database Connection Management

### 2.1 SQLAlchemy Session Lifecycle

```
요청 시작 → Dependency Injection으로 Session 생성
  → 요청 처리 (트랜잭션)
  → 정상: commit
  → 에러: rollback
  → 항상: session.close()
```

**Connection Pool 설정:**
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| pool_size | 10 | MVP 동시 접속 100명 기준 |
| max_overflow | 20 | 피크 시 추가 연결 허용 |
| pool_timeout | 30s | 연결 대기 최대 시간 |
| pool_recycle | 1800s | RDS proxy 호환 (30분) |

### 2.2 Startup Migration

앱 시작 시 Alembic 자동 실행:
```
1. DB 연결 확인
2. alembic upgrade head 실행
3. 마이그레이션 실패 시 → 앱 시작 중단 + 에러 로그
4. 성공 시 → 정상 시작 진행
```

---

## 3. FileManagerService (임시 파일 관리)

### 3.1 Core Responsibilities

S3 임시 버킷 기반 파일 관리:
- 이미지 업로드 (전신 사진, 의류 사진)
- 결과 이미지 저장 (피팅 결과, 배경 합성 결과)
- 만료 파일 자동 정리
- Pre-signed URL 생성 (다운로드/공유용)

### 3.2 Business Rules

| Rule | Description |
|------|-------------|
| BR-FILE-01 | 모든 임시 파일은 `expires_at` 기준 자동 삭제 |
| BR-FILE-02 | 기본 만료 시간: 1시간 (설정 가능) |
| BR-FILE-03 | 공유 링크용 파일: 24시간 만료 |
| BR-FILE-04 | 업로드 파일 최대 크기: 10MB |
| BR-FILE-05 | 허용 파일 형식: JPEG, PNG, WebP |
| BR-FILE-06 | S3 키 형식: `{env}/{user_id}/{task_id}/{filename}` |
| BR-FILE-07 | Pre-signed URL 유효 시간: 15분 |

### 3.3 Operations

**upload_file(user_id, task_id, file, category)**
```
1. 파일 형식 검증 (MIME type + extension)
2. 파일 크기 검증 (≤ 10MB)
3. S3 키 생성: {env}/{user_id}/{task_id}/{category}_{uuid}.{ext}
4. S3에 업로드 (ContentType 메타데이터 포함)
5. DB에 file path 기록 (fitting_tasks.result_file_path)
6. S3 키 반환
```

**get_download_url(s3_key)**
```
1. S3 객체 존재 여부 확인
2. 존재하지 않으면 → FileNotFoundError
3. Pre-signed URL 생성 (유효시간 15분)
4. URL 반환
```

**delete_file(s3_key)**
```
1. S3 객체 삭제
2. 삭제 실패 시 → 로그 기록 (비차단)
```

**cleanup_expired_files()**
```
1. DB에서 expires_at < NOW() 인 fitting_tasks 조회
2. 각 task의 result_file_path로 S3 객체 삭제
3. task status → 'expired' 업데이트 (또는 row 삭제)
4. share_links 중 만료된 건 → watermarked_path S3 삭제 + row 삭제
5. 처리 건수 로그 기록
```

### 3.4 S3 Bucket Configuration

| Setting | Value |
|---------|-------|
| Bucket Name | `v-suitcase-temp-{env}` |
| Lifecycle Rule | 객체 48시간 후 자동 삭제 (S3 안전장치) |
| Versioning | Off |
| Encryption | SSE-S3 (기본 암호화) |
| Public Access | 완전 차단 |
| CORS | 프론트엔드 도메인만 허용 |

---

## 4. Middleware Specifications

### 4.1 CORS Middleware

| Setting | Value |
|---------|-------|
| allow_origins | 프론트엔드 도메인 (환경별 설정) |
| allow_methods | GET, POST, PUT, DELETE, OPTIONS |
| allow_headers | Authorization, Content-Type |
| allow_credentials | true |

### 4.2 Error Handling Middleware

모든 예외를 표준 응답 형식으로 변환:

```json
{
  "detail": "Human-readable error message",
  "code": "ERROR_CODE"
}
```

**에러 코드 체계:**
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTH_REQUIRED` | 401 | 인증 토큰 없음/만료 |
| `AUTH_INVALID` | 401 | 유효하지 않은 토큰 |
| `FORBIDDEN` | 403 | 권한 부족 |
| `NOT_FOUND` | 404 | 리소스 없음 |
| `VALIDATION_ERROR` | 422 | 입력값 검증 실패 |
| `FILE_TOO_LARGE` | 413 | 파일 크기 초과 |
| `FILE_TYPE_INVALID` | 415 | 지원하지 않는 파일 형식 |
| `TASK_EXPIRED` | 410 | 만료된 작업 |
| `INTERNAL_ERROR` | 500 | 서버 내부 오류 |

### 4.3 Request Logging Middleware

각 요청에 대해 로그:
- 요청: method, path, user_id (인증 시), timestamp
- 응답: status_code, response_time_ms
- 에러 시: 에러 코드 + 스택 트레이스 (500만)

---

## 5. Database Migration Strategy

### 5.1 Alembic Configuration

```
migrations/
  env.py              # Alembic 환경 설정
  versions/
    001_create_users.py
    002_create_fitting_tasks.py
    003_create_share_links.py
    004_create_weather_requests.py
    005_create_size_recommendations.py
```

### 5.2 Migration Rules

| Rule | Description |
|------|-------------|
| MIG-01 | 모든 테이블에 `id` (UUID PK) + `created_at` 필수 |
| MIG-02 | FK에는 반드시 ON DELETE 정책 명시 |
| MIG-03 | 인덱스는 조회 패턴 기반으로 생성 |
| MIG-04 | 마이그레이션 파일에 rollback(downgrade) 항상 포함 |
| MIG-05 | 번호 순서대로 실행 보장 |

---

## 6. Background Task Scheduler

### 6.1 Cleanup Schedule

FastAPI `BackgroundTasks` + `asyncio` 기반 주기적 실행:

| Task | Interval | Action |
|------|----------|--------|
| 임시 파일 정리 | 10분 | `cleanup_expired_files()` 호출 |
| 만료 공유 링크 정리 | 1시간 | 만료된 share_links 삭제 |

### 6.2 Implementation Approach

앱 시작 시 `asyncio.create_task()`로 백그라운드 루프 등록:
```
async def periodic_cleanup():
    while True:
        await cleanup_expired_files()
        await asyncio.sleep(600)  # 10분
```

---

## 7. Health Check

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | 앱 상태 확인 (DB 연결 + S3 접근 가능 여부) |
| `GET /health/ready` | 마이그레이션 완료 + 모든 서비스 준비 상태 |
