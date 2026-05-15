# V-Suitcase — Services & API Design

## API Endpoints (FastAPI)

### Authentication
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/signup` | 회원가입 (Cognito) | No |
| POST | `/api/auth/login` | 로그인 (Cognito) | No |
| POST | `/api/auth/logout` | 로그아웃 | Yes |
| GET | `/api/auth/me` | 현재 사용자 정보 | Yes |

### Face Verification
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/face/register` | 기준 얼굴 등록 (셀피) | Yes |
| POST | `/api/face/verify` | 본인 확인 (전신 사진 얼굴 비교) | Yes |

### Fitting
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/fitting/upload-body` | 전신 사진 업로드 | Yes |
| POST | `/api/fitting/upload-clothing` | 의류 이미지 업로드 | Yes |
| POST | `/api/fitting/generate` | 가상 피팅 실행 | Yes |
| GET | `/api/fitting/result/{task_id}` | 피팅 결과 조회 | Yes |

### Background
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/background/generate-text` | 텍스트 프롬프트 배경 생성 | Yes |
| POST | `/api/background/generate-image` | 이미지 업로드 배경 합성 | Yes |

### Recommend
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/recommend/size` | 체형 분석 사이즈 추천 | Yes |
| POST | `/api/recommend/weather` | 날씨 기반 코디 추천 | Yes |

### Result & Share
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/result/download/{task_id}` | 결과 이미지 다운로드 | Yes |
| POST | `/api/result/share/{task_id}` | SNS 공유용 임시 URL 생성 | Yes |
| GET | `/api/share/{share_id}` | 공유 이미지 접근 (임시, 24h 만료) | No |

---

## Orchestration Flow

### 가상 피팅 메인 플로우
```
Client                    FastAPI                   AI (Mock/Phase2)
  |                         |                          |
  |-- upload-body --------->|                          |
  |                         |-- face/verify ---------->|
  |                         |<-- verify result --------|
  |<-- verify OK -----------|                          |
  |                         |                          |
  |-- upload-clothing ----->|                          |
  |                         |                          |
  |-- fitting/generate ---->|                          |
  |                         |-- [Mock: return sample] -|
  |                         |<-- fitting image --------|
  |<-- result (task_id) ----|                          |
  |                         |                          |
  |-- result/download ----->|                          |
  |<-- image file ----------|                          |
```

### 배경 생성 플로우
```
Client                    FastAPI                   AI (Mock/Phase2)
  |                         |                          |
  |-- background/text ----->|                          |
  |                         |-- [Mock: return sample] -|
  |                         |<-- background image -----|
  |<-- result (task_id) ----|                          |
```
