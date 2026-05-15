# Functional Design Plan — unit-auth

## Unit Overview
- **Unit**: unit-auth
- **Purpose**: 사용자 인증 및 Face ID 본인 확인
- **Scope**: Cognito 연동, 회원가입/로그인, Face ID 등록/검증
- **Backend Components**: BC-01 AuthService, BC-02 FaceVerificationService
- **Frontend Components**: FC-01 AuthModule, FC-02 FaceIDModule
- **Stories**: US-01, US-02, US-03, US-04

---

## Plan Steps

- [x] Step 1: Define AuthService business logic (Cognito 연동, 토큰 관리)
- [x] Step 2: Define FaceVerificationService business logic (등록/검증 플로우)
- [x] Step 3: Define frontend AuthModule (로그인/회원가입 UI 플로우)
- [x] Step 4: Define frontend FaceIDModule (셀피 촬영, 등록 플로우)
- [x] Step 5: Define error scenarios and edge cases
- [x] Step 6: Generate functional design artifacts

---

## Clarifying Questions

아래 질문에 답변해 주세요.

---

### Q1: Cognito 회원가입 인증 방식

이메일 인증(가입 확인)을 어떻게 처리하시겠습니까?

- A) Cognito 기본 이메일 인증 코드 (6자리 코드 입력)
- B) Cognito 확인 링크 (이메일 내 링크 클릭)
- C) 자동 확인 (개발/MVP 단계에서 이메일 인증 생략)
- X) Other (please describe after [Answer]: tag below)

[Answer]:  C

---

### Q2: 토큰 저장 위치 (프론트엔드)

Cognito에서 받은 Access/Refresh 토큰을 프론트엔드에서 어디에 저장하시겠습니까?

- A) `localStorage` (간단하지만 XSS 취약)
- B) `httpOnly cookie` (보안 강화, CSRF 대응 필요)
- C) 메모리 (Zustand store) + `localStorage` refresh token만 (적절한 균형)
- X) Other (please describe after [Answer]: tag below)

[Answer]:  C

---

### Q3: Face ID 등록 시점 강제 여부

Face ID 미등록 사용자가 서비스를 이용하려 할 때 어떻게 처리하시겠습니까?

- A) 강제 등록 (Face ID 없으면 피팅 기능 완전 차단)
- B) 선택적 등록 (Face ID 없어도 피팅 가능, 본인 인증 스킵)
- C) 첫 피팅 시 강제 (최초 1회만 강제, 이후 자동)
- X) Other (please describe after [Answer]: tag below)

[Answer]:  A

---

### Q4: 얼굴 인증 실패 시 재시도 정책

본인 인증(전신 사진 얼굴 비교) 실패 시 사용자에게 어떤 옵션을 제공하시겠습니까?

- A) 무제한 재시도 (다른 사진으로 재시도 가능)
- B) 3회 제한 (3회 실패 시 일정 시간 차단)
- C) 재시도 + 기준 얼굴 재등록 옵션 제공
- X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

### Q5: 셀피 촬영 방식

Face ID 등록을 위한 셀피 촬영을 어떻게 구현하시겠습니까?

- A) 웹캠 실시간 촬영 (WebRTC)
- B) 파일 업로드만 (갤러리에서 선택)
- C) 둘 다 지원 (웹캠 촬영 + 파일 업로드)
- X) Other (please describe after [Answer]: tag below)

[Answer]:  A

---

위 질문에 답변해 주시면 unit-auth의 상세 기능 설계를 생성하겠습니다.
