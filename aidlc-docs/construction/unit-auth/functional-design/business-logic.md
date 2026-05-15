# Business Logic — unit-auth

## 1. AuthService (BC-01)

### 1.1 회원가입 (Sign Up)

**플로우**:
1. 사용자가 이메일, 비밀번호 입력
2. Cognito `signUp` API 호출
3. 자동 확인 (autoConfirmUser Lambda trigger) — 이메일 인증 생략
4. 가입 성공 시 자동 로그인 처리
5. Face ID 등록 화면으로 리다이렉트

**비즈니스 규칙**:
- 이메일 형식 검증 (RFC 5322)
- 비밀번호: 최소 8자, 영문+숫자+특수문자 조합
- 중복 이메일 가입 차단 (Cognito 기본)
- 가입 즉시 자동 확인 (MVP 단계)

### 1.2 로그인 (Login)

**플로우**:
1. 사용자가 이메일, 비밀번호 입력
2. Cognito `initiateAuth` (USER_PASSWORD_AUTH) 호출
3. AccessToken, IdToken, RefreshToken 수신
4. AccessToken → Zustand 메모리 저장
5. RefreshToken → localStorage 저장
6. Face ID 등록 여부 확인 → 미등록 시 등록 화면 강제 이동

**비즈니스 규칙**:
- 로그인 실패 시 일반 오류 메시지 ("이메일 또는 비밀번호가 올바르지 않습니다")
- Cognito 잠금 정책 위임 (5회 연속 실패 시 임시 잠금)
- 토큰 만료 시 RefreshToken으로 자동 갱신

### 1.3 로그아웃 (Logout)

**플로우**:
1. Cognito `globalSignOut` 호출
2. Zustand store의 AccessToken 제거
3. localStorage의 RefreshToken 제거
4. 로그인 화면으로 리다이렉트

### 1.4 토큰 관리

**자동 갱신 메커니즘**:
- AccessToken 만료 전(예: 남은 시간 5분 이하) RefreshToken으로 갱신
- 갱신 실패 시 → 로그아웃 처리 + 로그인 화면 이동
- 동시 요청 시 갱신 중복 방지 (단일 갱신 Promise 공유)

**저장 전략**:
| 토큰 | 저장 위치 | 이유 |
|------|-----------|------|
| AccessToken | Zustand (메모리) | XSS 방어 |
| IdToken | Zustand (메모리) | 사용자 정보 표시용 |
| RefreshToken | localStorage | 페이지 새로고침 생존 |

---

## 2. FaceVerificationService (BC-02)

### 2.1 Face ID 등록 (Reference Face Registration)

**플로우**:
1. 사용자가 웹캠으로 셀피 촬영
2. 이미지 품질 검증 (프론트엔드 프리체크):
   - 얼굴 감지 여부
   - 밝기/선명도 기본 확인
3. S3에 이미지 업로드 (`faces/{userId}/reference.jpg`)
4. 메타데이터 DB 저장 (userId, s3Key, registeredAt)
5. 등록 완료 상태 업데이트

**비즈니스 규칙**:
- 사용자당 1개의 기준 얼굴만 유지 (재등록 시 덮어쓰기)
- Face ID 미등록 시 피팅 기능 완전 차단
- Phase 1: 이미지 저장만 (비교 로직 Mock)
- Phase 2: AWS Rekognition `compareFaces` 연동

### 2.2 본인 인증 (Identity Verification)

**플로우**:
1. 전신 사진 업로드 시 얼굴 영역 추출
2. 등록된 기준 얼굴과 비교
3. 유사도 임계값(Threshold) 기반 판정
4. 결과 반환: PASS / FAIL

**비즈니스 규칙**:
- 유사도 임계값: 90% (Phase 2, Rekognition 기준)
- Phase 1: Mock으로 항상 PASS 반환
- 실패 시 재시도 가능 (다른 사진으로)

### 2.3 재시도 정책

| 항목 | 정책 |
|------|------|
| 재시도 횟수 | 무제한 (단, 연속 3회 실패 시 안내 메시지 표시) |
| 3회 실패 시 | "기준 얼굴을 다시 등록하시겠습니까?" 옵션 제공 |
| 기준 얼굴 재등록 | 언제든 설정에서 가능 |
| 재등록 후 | 기존 기준 이미지 교체, 즉시 재인증 가능 |

---

## 3. 인증 상태 기반 접근 제어

### Route Guard 로직

```
if (!isLoggedIn) → /login 리다이렉트
if (isLoggedIn && !hasFaceId) → /face-id/register 리다이렉트
if (isLoggedIn && hasFaceId) → 서비스 접근 허용
```

### 인증 상태 모델

| 상태 | 조건 | 접근 가능 영역 |
|------|------|----------------|
| UNAUTHENTICATED | 토큰 없음 | 로그인/회원가입만 |
| AUTHENTICATED_NO_FACE | 토큰 있음, Face ID 미등록 | Face ID 등록만 |
| FULLY_AUTHENTICATED | 토큰 있음, Face ID 등록됨 | 전체 서비스 |
