# unit-core — Frontend Layout Module (FC-07)

## 1. Routing Structure

React Router v6 + 인증/비인증 레이아웃 분리

### Route Map

```
/                       → Redirect to /login or /fitting
/login                  → PublicLayout > LoginPage
/signup                 → PublicLayout > SignupPage
/face-register          → AuthLayout > FaceRegisterPage
/fitting                → AuthLayout > FittingPage (메인)
/fitting/result/:id     → AuthLayout > FittingResultPage
/background/:id         → AuthLayout > BackgroundPage
/recommend              → AuthLayout > RecommendPage
/recommend/weather      → AuthLayout > WeatherRecommendPage
/result/:id             → AuthLayout > ResultPage
/share/:shareId         → PublicLayout > SharedViewPage (인증 불요)
```

---

## 2. Layout Components

### PublicLayout (비인증)
```
+---------------------------------------+
|           V-Suitcase 로고              |
+---------------------------------------+
|                                       |
|         [Page Content]                |
|         (로그인, 회원가입 등)           |
|                                       |
+---------------------------------------+
|         Copyright Footer              |
+---------------------------------------+
```

- 네비게이션 바 없음
- 중앙 정렬 카드 형태
- 브랜드 로고만 표시

### AuthLayout (인증 후)
```
+---------------------------------------+
|  Logo  |  Nav Tabs  |  User Menu  ▼  |
+---------------------------------------+
|                                       |
|         [Page Content]                |
|         (피팅, 결과, 추천 등)          |
|                                       |
+---------------------------------------+
|         Bottom Nav (모바일)            |
+---------------------------------------+
```

- 상단 네비게이션: 피팅 | 추천 | 마이페이지
- 모바일: 하단 탭 네비게이션
- User Menu: 프로필, 로그아웃

---

## 3. Route Guards

### AuthGuard
```
인증 토큰 존재 여부 확인
  → 없음: /login으로 redirect
  → 있음: 토큰 유효성 확인
    → 만료: refresh 시도 → 실패 시 /login
    → 유효: children 렌더링
```

### FaceIDGuard
```
Face ID 등록 여부 확인 (user.face_registered)
  → 미등록: /face-register로 redirect
  → 등록됨: children 렌더링
```

### Route Guard 적용:
| Route | Guards |
|-------|--------|
| /login, /signup | 없음 (이미 로그인 시 /fitting redirect) |
| /face-register | AuthGuard |
| /fitting, /background, /recommend, /result | AuthGuard + FaceIDGuard |
| /share/:id | 없음 (공개 링크) |

---

## 4. Global State (Zustand)

### AuthStore
| Field | Type | Description |
|-------|------|-------------|
| user | User or null | 현재 로그인 사용자 |
| accessToken | string or null | Cognito access token |
| isAuthenticated | boolean | 로그인 상태 |
| login() | function | 로그인 처리 |
| logout() | function | 로그아웃 처리 |
| refreshToken() | function | 토큰 갱신 |

### UIStore
| Field | Type | Description |
|-------|------|-------------|
| isLoading | boolean | 전역 로딩 상태 |
| toast | ToastMessage or null | 알림 메시지 |
| showToast() | function | 토스트 표시 |

---

## 5. Axios Configuration

### Request Interceptor
```
모든 요청에 Authorization 헤더 자동 첨부:
  Authorization: Bearer {accessToken}
```

### Response Interceptor
```
401 응답 수신 시:
  1. refreshToken() 시도
  2. 성공: 원래 요청 재시도
  3. 실패: logout() + /login redirect
```

---

## 6. Common UI Components (unit-core 제공)

| Component | Purpose |
|-----------|---------|
| LoadingSpinner | 전역/로컬 로딩 인디케이터 |
| Toast | 알림 메시지 (성공/에러/경고) |
| ErrorBoundary | React 에러 경계 |
| FileUpload | 공통 이미지 업로드 컴포넌트 (drag & drop) |
| ImagePreview | 업로드 이미지 미리보기 |
| ConfirmDialog | 확인 다이얼로그 |
