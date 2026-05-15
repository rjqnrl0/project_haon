# unit-core — Domain Entities

## 1. Configuration Entities

### AppSettings (Pydantic BaseSettings)

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| env | str | ENV var | 환경 (local/dev/staging/prod) |
| db_host | str | Parameter Store | RDS 호스트 |
| db_port | int | Parameter Store | RDS 포트 |
| db_name | str | Parameter Store | DB 이름 |
| db_username | str | Secrets Manager | DB 사용자 |
| db_password | str | Secrets Manager | DB 비밀번호 |
| cognito_pool_id | str | Parameter Store | Cognito Pool ID |
| cognito_client_id | str | Parameter Store | Cognito Client ID |
| cognito_client_secret | str | Secrets Manager | Cognito 시크릿 |
| s3_temp_bucket | str | Parameter Store | 임시 파일 버킷 |
| s3_region | str | Parameter Store | AWS 리전 |
| file_expiry_hours | int | Parameter Store | 기본 만료 시간 (기본: 1) |
| share_expiry_hours | int | Parameter Store | 공유 링크 만료 시간 (기본: 24) |

---

## 2. Database Base Model

### Base Entity (SQLAlchemy)

모든 테이블의 공통 필드:

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | PK, gen_random_uuid() |
| created_at | TIMESTAMP WITH TZ | 생성 일시, default=NOW() |

---

## 3. Shared Enums

### TaskStatus
| Value | Description |
|-------|-------------|
| `pending` | 생성됨, 처리 대기 |
| `processing` | 처리 중 |
| `completed` | 완료 |
| `failed` | 실패 |

### TaskType
| Value | Description |
|-------|-------------|
| `fitting` | 가상 피팅 |
| `background` | 배경 생성 |

### ClothingCategory
| Value | Description |
|-------|-------------|
| `top` | 상의 |
| `bottom` | 하의 |
| `dress` | 원피스 |
| `outer` | 아우터 |
| `accessory` | 액세서리 |

### FileCategory (업로드 파일 분류)
| Value | Description |
|-------|-------------|
| `body` | 전신 사진 |
| `clothing` | 의류 이미지 |
| `result` | 결과 이미지 |
| `background_input` | 배경 입력 이미지 |
| `watermarked` | 워터마크 결과 |

---

## 4. Error Domain

### AppError (기본 예외 클래스)

| Field | Type | Description |
|-------|------|-------------|
| code | str | 에러 코드 (예: `FILE_TOO_LARGE`) |
| detail | str | 사용자 친화 메시지 |
| status_code | int | HTTP 상태 코드 |

### Error Hierarchy
```
AppError (base)
├── AuthError (401)
├── ForbiddenError (403)
├── NotFoundError (404)
├── ValidationError (422)
├── FileError (413, 415)
│   ├── FileTooLargeError
│   └── FileTypeInvalidError
├── TaskExpiredError (410)
└── InternalError (500)
```

---

## 5. File Management Entities

### UploadedFile (DTO)

| Field | Type | Description |
|-------|------|-------------|
| s3_key | str | S3 객체 키 |
| original_filename | str | 원본 파일명 |
| content_type | str | MIME type |
| size_bytes | int | 파일 크기 |
| uploaded_at | datetime | 업로드 시간 |

### FileValidation (규칙)

| Rule | Value |
|------|-------|
| max_size_bytes | 10,485,760 (10MB) |
| allowed_content_types | image/jpeg, image/png, image/webp |
| allowed_extensions | .jpg, .jpeg, .png, .webp |
