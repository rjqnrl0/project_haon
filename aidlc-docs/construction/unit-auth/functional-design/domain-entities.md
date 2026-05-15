# Domain Entities — unit-auth

## 1. User

| 속성 | 타입 | 설명 |
|------|------|------|
| userId | string (UUID) | Cognito sub (PK) |
| email | string | 로그인 이메일 |
| createdAt | ISO timestamp | 가입일시 |
| hasFaceId | boolean | Face ID 등록 여부 |

## 2. FaceRegistration

| 속성 | 타입 | 설명 |
|------|------|------|
| userId | string (UUID) | FK → User |
| s3Key | string | S3 저장 경로 (`faces/{userId}/reference.jpg`) |
| registeredAt | ISO timestamp | 등록일시 |
| updatedAt | ISO timestamp | 마지막 재등록일시 |

## 3. AuthSession (프론트엔드 상태)

| 속성 | 타입 | 설명 |
|------|------|------|
| accessToken | string | null | Cognito AccessToken (메모리) |
| idToken | string | null | Cognito IdToken (메모리) |
| refreshToken | string | null | Cognito RefreshToken (localStorage) |
| user | User | null | 현재 로그인 사용자 정보 |
| status | AuthStatus | 인증 상태 |

## 4. AuthStatus (Enum)

| 값 | 설명 |
|----|------|
| UNAUTHENTICATED | 미인증 |
| AUTHENTICATED_NO_FACE | 인증됨, Face ID 미등록 |
| FULLY_AUTHENTICATED | 완전 인증 (서비스 접근 가능) |

## 5. VerificationResult

| 속성 | 타입 | 설명 |
|------|------|------|
| verified | boolean | 인증 성공 여부 |
| similarity | number (0-100) | 유사도 점수 |
| threshold | number | 판정 임계값 (90) |
| attemptCount | number | 현재 연속 시도 횟수 |

## 6. Entity Relationships

```
User (1) ---- (0..1) FaceRegistration
User (1) ---- (1) AuthSession [프론트엔드]
AuthSession --- references --> AuthStatus
FaceVerification --- produces --> VerificationResult
```
