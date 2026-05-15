# Code Generation Plan — unit-auth

## Unit Context
- **Unit**: unit-auth
- **Purpose**: 사용자 인증 및 Face ID 본인 확인
- **Stories**: US-01 (회원가입), US-02 (로그인/로그아웃), US-03 (Face ID 등록), US-04 (본인 인증)

## Dependencies
- unit-core (DB, Config, FileManagerService, AuthGuard, authStore)

---

## Code Generation Steps

### Backend

- [x] Step 1: Auth API routes — `backend/app/api/auth.py` (signup, login, logout, me)
- [x] Step 2: Auth service — `backend/app/services/auth_service.py` (Cognito 연동)
- [x] Step 3: Auth dependency — `backend/app/core/auth.py` (토큰 검증, get_current_user)
- [x] Step 4: Face ID API routes — `backend/app/api/face.py` (register, verify)
- [x] Step 5: Face verification service — `backend/app/services/face_service.py` (등록/검증 Mock)

### Frontend

- [x] Step 6: Auth pages — `frontend/src/pages/auth/` (LoginPage, SignupPage)
- [x] Step 7: useAuth hook — `frontend/src/hooks/useAuth.ts`
- [x] Step 8: Face ID pages — `frontend/src/pages/face/` (FaceIDRegisterPage)
- [x] Step 9: useFaceID hook — `frontend/src/hooks/useFaceID.ts`
- [x] Step 10: Update App.tsx routes with actual page components

### Documentation

- [x] Step 11: Code summary — `aidlc-docs/construction/unit-auth/code/code-summary.md`
