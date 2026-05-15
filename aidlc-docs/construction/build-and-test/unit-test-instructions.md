# Unit Test Instructions — V-Suitcase

## Testing Framework

| Layer | Framework | Config |
|-------|-----------|--------|
| Backend | pytest + pytest-asyncio + httpx | `backend/pytest.ini` |
| Frontend | Vitest + React Testing Library | `frontend/vitest.config.ts` |

## Backend Unit Tests

### Setup

```bash
cd backend

# Install test dependencies
pip install pytest pytest-asyncio httpx pytest-cov

# Create pytest.ini (if not exists)
cat > pytest.ini << 'EOF'
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_functions = test_*
EOF
```

### Test Directory Structure

```
backend/tests/
  conftest.py              # Fixtures: async client, mock DB session, mock S3
  test_auth_service.py     # Auth service unit tests
  test_face_service.py     # Face service unit tests
  test_fitting_service.py  # Fitting service unit tests
  test_background_service.py  # Background service unit tests
  test_recommend_service.py   # Recommend service unit tests
  test_share_service.py    # Share service unit tests
  test_file_manager.py     # File manager unit tests
  test_api_auth.py         # Auth API endpoint tests
  test_api_fitting.py      # Fitting API endpoint tests
  test_api_background.py   # Background API endpoint tests
  test_api_recommend.py    # Recommend API endpoint tests
  test_api_share.py        # Share API endpoint tests
```

### Running Backend Unit Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Run specific module
pytest tests/test_auth_service.py -v

# Run single test
pytest tests/test_fitting_service.py::test_upload_body_validates_dimensions -v
```

### Key Test Scenarios — Backend

#### Auth Service
- `test_signup_success` — creates user in Cognito (mocked) and DB
- `test_login_success` — returns tokens
- `test_login_invalid_credentials` — raises AuthError
- `test_refresh_token_success` — returns new access token
- `test_logout_clears_session` — deletes session data

#### Face Service
- `test_register_face_uploads_to_s3` — S3 upload + sets face_registered=true
- `test_verify_face_always_passes_phase1` — returns similarity=95, pass=true
- `test_register_face_validates_file_type` — rejects non-image

#### Fitting Service
- `test_upload_body_validates_minimum_dimensions` — rejects < 640x480
- `test_upload_body_stores_s3_path` — persists file path in task
- `test_upload_clothing_with_category` — validates category enum
- `test_execute_fitting_mock_returns_original` — Phase 1 mock behavior
- `test_get_result_returns_presigned_url` — generates S3 URL

#### Background Service
- `test_search_unsplash_returns_results` — mocked Unsplash API response
- `test_generate_from_text_mock_returns_original` — Phase 1 mock
- `test_generate_from_upload_stores_file` — S3 upload verification

#### Recommend Service
- `test_get_size_recommendation_returns_hardcoded` — mock data structure
- `test_get_weather_codi_with_valid_city` — OpenWeatherMap mock + template
- `test_get_weather_codi_invalid_city` — error handling

#### Share Service
- `test_create_download_adds_watermark` — watermark on JPEG output
- `test_create_share_link_generates_token` — UUID token + 30-day expiry
- `test_get_shared_image_expired` — raises NotFoundError after expiry
- `test_get_shared_image_valid` — returns presigned URL

#### File Manager
- `test_upload_file_to_s3` — successful upload
- `test_validate_file_size_exceeds_limit` — raises FileTooLargeError (>10MB)
- `test_validate_file_type_invalid` — raises FileTypeInvalidError

### Expected Results — Backend

| Category | Test Count (est.) | Expected Pass Rate |
|----------|-------------------|-------------------|
| Auth | 5 | 100% |
| Face | 3 | 100% |
| Fitting | 5 | 100% |
| Background | 3 | 100% |
| Recommend | 3 | 100% |
| Share | 4 | 100% |
| File Manager | 3 | 100% |
| **Total** | **26+** | **100%** |

---

## Frontend Unit Tests

### Setup

```bash
cd frontend

# Install test dependencies
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom @testing-library/user-event
```

Add to `package.json` scripts:
```json
"test": "vitest",
"test:coverage": "vitest run --coverage"
```

Create `frontend/vitest.config.ts`:
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    globals: true,
  },
})
```

Create `frontend/src/test/setup.ts`:
```typescript
import '@testing-library/jest-dom'
```

### Test Directory Structure

```
frontend/src/
  test/
    setup.ts
  pages/
    auth/__tests__/
      LoginPage.test.tsx
      SignupPage.test.tsx
    face/__tests__/
      FaceIDRegisterPage.test.tsx
    fitting/__tests__/
      FittingPage.test.tsx
      FittingResultPage.test.tsx
    background/__tests__/
      BackgroundPage.test.tsx
    recommend/__tests__/
      RecommendPage.test.tsx
    share/__tests__/
      ShareViewPage.test.tsx
  components/common/__tests__/
    FileUpload.test.tsx
    Toast.test.tsx
    ConfirmDialog.test.tsx
  hooks/__tests__/
    useAuth.test.ts
    useFitting.test.ts
  stores/__tests__/
    authStore.test.ts
    uiStore.test.ts
```

### Running Frontend Unit Tests

```bash
# Run all tests (watch mode)
npm test

# Run once
npx vitest run

# Run with coverage
npm run test:coverage

# Run specific file
npx vitest run src/pages/auth/__tests__/LoginPage.test.tsx
```

### Key Test Scenarios — Frontend

#### LoginPage
- Renders email/password inputs and submit button
- Shows validation errors for empty fields
- Calls login API on valid submit
- Navigates to /face-id/register on success
- Displays error toast on API failure

#### SignupPage
- Renders email/password/confirm fields
- Shows mismatch error when passwords differ
- Calls signup API on valid submit
- Navigates to /login on success

#### FaceIDRegisterPage
- Requests camera permission on mount
- Shows video preview when camera active
- Captures image on button click
- Shows confirm/retake buttons after capture
- Calls registerFace API on confirm

#### FittingPage
- Renders body upload section
- Shows clothing category selector
- Enables execute button only when body + clothing uploaded
- Displays progress during fitting execution

#### RecommendPage
- Renders weather/size tab buttons
- Shows city autocomplete suggestions on input
- Displays quick-select city chips
- Shows weather result card after API call

#### Stores
- `authStore`: setAuth stores user + token, logout clears state
- `uiStore`: showToast sets message, auto-clears after duration

### Expected Results — Frontend

| Category | Test Count (est.) | Expected Pass Rate |
|----------|-------------------|-------------------|
| Pages | 14 | 100% |
| Components | 6 | 100% |
| Hooks | 4 | 100% |
| Stores | 4 | 100% |
| **Total** | **28+** | **100%** |

---

## Cleanup

No cleanup required for unit tests — all external dependencies are mocked.
