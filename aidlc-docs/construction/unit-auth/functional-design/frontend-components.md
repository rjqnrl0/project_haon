# Frontend Components — unit-auth

## 1. AuthModule (FC-01)

### 1.1 SignUpPage

**역할**: 회원가입 폼 제공

**UI 요소**:
- 이메일 입력 필드
- 비밀번호 입력 필드
- 비밀번호 확인 필드
- 가입 버튼
- 로그인 링크

**동작**:
1. 입력값 실시간 유효성 검증
2. 가입 버튼 클릭 → Cognito signUp 호출
3. 성공 → 자동 로그인 → Face ID 등록 화면 이동
4. 실패 → 인라인 에러 메시지 표시

**유효성 검증**:
- 이메일: 형식 검증
- 비밀번호: 8자 이상, 영문+숫자+특수문자
- 비밀번호 확인: 일치 여부

### 1.2 LoginPage

**역할**: 로그인 폼 제공

**UI 요소**:
- 이메일 입력 필드
- 비밀번호 입력 필드
- 로그인 버튼
- 회원가입 링크

**동작**:
1. 로그인 버튼 클릭 → Cognito initiateAuth 호출
2. 성공 → 토큰 저장 → Face ID 상태 확인 → 적절한 화면 이동
3. 실패 → "이메일 또는 비밀번호가 올바르지 않습니다" 표시

### 1.3 AuthGuard (Route Protection)

**역할**: 인증 상태 기반 라우트 보호

**로직**:
```
UNAUTHENTICATED → /login 리다이렉트
AUTHENTICATED_NO_FACE → /face-id/register 리다이렉트
FULLY_AUTHENTICATED → children 렌더링
```

### 1.4 useAuth Hook

**제공 기능**:
- `login(email, password)` — 로그인 실행
- `signUp(email, password)` — 회원가입 실행
- `logout()` — 로그아웃 실행
- `user` — 현재 사용자 정보
- `status` — AuthStatus
- `isLoading` — 인증 처리 중 여부

---

## 2. FaceIDModule (FC-02)

### 2.1 FaceIDRegisterPage

**역할**: 셀피 촬영 및 Face ID 등록

**UI 요소**:
- 웹캠 미리보기 (실시간 비디오)
- 촬영 버튼
- 촬영된 이미지 프리뷰
- 재촬영 버튼
- 등록 확인 버튼
- 안내 텍스트 (올바른 셀피 촬영 가이드)

**동작 플로우**:
1. 페이지 진입 → 웹캠 권한 요청 (`getUserMedia`)
2. 실시간 비디오 스트림 표시
3. 촬영 버튼 클릭 → 캔버스에 프레임 캡처 → JPEG 변환
4. 캡처 이미지 프리뷰 표시
5. 재촬영 / 등록 선택
6. 등록 확인 → 이미지 업로드 API 호출
7. 성공 → 메인 서비스 화면 이동
8. 실패 → 에러 메시지 + 재촬영 안내

**웹캠 설정**:
- 전면 카메라 우선 (`facingMode: "user"`)
- 해상도: 최소 640x480
- 캡처 포맷: JPEG (quality: 0.8)

### 2.2 FaceIDReRegisterPage

**역할**: 기준 얼굴 재등록

**UI 요소**: FaceIDRegisterPage와 동일 + 재등록 사유 안내

**진입 경로**:
- 설정 메뉴에서 "얼굴 재등록"
- 본인 인증 3회 연속 실패 시 제안

### 2.3 VerificationFailureModal

**역할**: 본인 인증 실패 시 안내

**UI 요소**:
- 실패 메시지
- "다른 사진으로 재시도" 버튼
- "기준 얼굴 재등록" 버튼 (3회 실패 시 표시)
- 닫기 버튼

### 2.4 useFaceID Hook

**제공 기능**:
- `captureImage()` — 웹캠 프레임 캡처
- `registerFace(imageBlob)` — 기준 얼굴 등록 API 호출
- `verifyFace(imageBlob)` — 본인 인증 API 호출
- `hasFaceId` — 등록 여부
- `attemptCount` — 연속 실패 횟수
- `isProcessing` — 처리 중 여부

---

## 3. 라우트 구조

| 경로 | 컴포넌트 | 접근 조건 |
|------|----------|-----------|
| /login | LoginPage | UNAUTHENTICATED only |
| /signup | SignUpPage | UNAUTHENTICATED only |
| /face-id/register | FaceIDRegisterPage | AUTHENTICATED_NO_FACE only |
| /face-id/re-register | FaceIDReRegisterPage | FULLY_AUTHENTICATED |
| /* (서비스) | AuthGuard wrapping | FULLY_AUTHENTICATED only |
