# Integration Test Instructions — V-Suitcase

## Purpose

Validate that components work together correctly across service boundaries: API → Service → Database → S3.

## Prerequisites

- Docker Compose services running (PostgreSQL + LocalStack)
- S3 bucket created in LocalStack
- Database migrations applied
- Backend server accessible at `http://localhost:8000`

## Test Environment Setup

```bash
cd backend

# Ensure infrastructure is running
docker compose up -d

# Create S3 bucket
aws --endpoint-url=http://localhost:4566 s3 mb s3://v-suitcase-temp-local --region ap-northeast-2

# Apply migrations
alembic upgrade head

# Install test dependencies
pip install pytest pytest-asyncio httpx pytest-cov
```

### Integration Test Config

Create `backend/tests/integration/conftest.py`:
```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
```

## Test Directory Structure

```
backend/tests/integration/
  conftest.py
  test_auth_flow.py
  test_fitting_flow.py
  test_background_flow.py
  test_recommend_flow.py
  test_share_flow.py
  test_file_lifecycle.py
```

## Running Integration Tests

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific flow
pytest tests/integration/test_fitting_flow.py -v

# With coverage
pytest tests/integration/ --cov=app --cov-report=term-missing
```

## Integration Test Scenarios

### 1. Auth Flow (`test_auth_flow.py`)

| Test | Steps | Expected |
|------|-------|----------|
| `test_signup_and_login` | POST /auth/signup → POST /auth/login | 200, access_token returned |
| `test_protected_route_without_token` | GET /fitting without Authorization header | 401 Unauthorized |
| `test_protected_route_with_token` | Login → GET /fitting with token | 200 |
| `test_refresh_token` | Login → POST /auth/refresh | New access_token |

### 2. Fitting Flow (`test_fitting_flow.py`)

| Test | Steps | Expected |
|------|-------|----------|
| `test_full_fitting_flow` | Upload body → Upload clothing → Execute fitting → Get result | result_url present |
| `test_body_upload_creates_s3_object` | POST /fitting/body with image | S3 object exists |
| `test_clothing_upload_with_category` | POST /fitting/clothing with category=top | DB record has category |
| `test_execute_without_body_fails` | POST /fitting/execute without body | 400 error |
| `test_result_not_found` | GET /fitting/result/{invalid-id} | 404 |

### 3. Background Flow (`test_background_flow.py`)

| Test | Steps | Expected |
|------|-------|----------|
| `test_search_backgrounds` | GET /background/search?prompt=paris | Array of results |
| `test_text_background_generation` | Create fitting → POST /background/text | result_url present |
| `test_upload_background` | Create fitting → POST /background/upload/{id} with file | result_url present |

### 4. Recommend Flow (`test_recommend_flow.py`)

| Test | Steps | Expected |
|------|-------|----------|
| `test_weather_codi_with_city` | POST /recommend/weather {city: "Tokyo"} | codi_advice, essential_items |
| `test_weather_codi_invalid_city` | POST /recommend/weather {city: ""} | 400 error |
| `test_size_recommendation` | Create fitting → POST /recommend/size | recommended_size present |

### 5. Share Flow (`test_share_flow.py`)

| Test | Steps | Expected |
|------|-------|----------|
| `test_create_share_link` | Create fitting result → POST /share/create | share_token, share_url |
| `test_access_shared_image` | Create share → GET /share/{token} | image_url present |
| `test_expired_share_link` | Create share (mock expired) → GET /share/{token} | 404 |
| `test_download_result` | Create fitting result → POST /share/download | watermarked image URL |

### 6. File Lifecycle (`test_file_lifecycle.py`)

| Test | Steps | Expected |
|------|-------|----------|
| `test_file_upload_and_retrieval` | Upload file → Get presigned URL → Fetch file | File content matches |
| `test_file_size_validation` | Upload >10MB file | 413 FileTooLarge |
| `test_file_type_validation` | Upload .txt file | 415 FileTypeInvalid |
| `test_session_cleanup_on_logout` | Upload files → Logout → Check S3 | Files deleted |

## Expected Results

| Flow | Test Count | Expected Pass Rate |
|------|-----------|-------------------|
| Auth | 4 | 100% |
| Fitting | 5 | 100% |
| Background | 3 | 100% |
| Recommend | 3 | 100% |
| Share | 4 | 100% |
| File Lifecycle | 4 | 100% |
| **Total** | **23** | **100%** |

## Cleanup

```bash
# Reset database
alembic downgrade base
alembic upgrade head

# Clear S3 bucket
aws --endpoint-url=http://localhost:4566 s3 rm s3://v-suitcase-temp-local --recursive

# Stop infrastructure (when done)
docker compose down
```

## Notes

- Integration tests use `ENV=local` which bypasses Cognito JWT verification
- S3 operations go to LocalStack, not real AWS
- OpenWeatherMap API calls are mocked in tests (or use real key for E2E validation)
- Unsplash API calls are mocked in tests
