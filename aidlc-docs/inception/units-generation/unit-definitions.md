# V-Suitcase — Unit Definitions

## Unit 1: unit-core

| 항목 | 내용 |
|------|------|
| **이름** | unit-core |
| **설명** | 프로젝트 기반 구조, 설정, DB 마이그레이션, 공통 유틸리티 |
| **범위** | FastAPI 앱 초기화, DB 연결, 설정 관리, 임시 파일 관리 서비스 |
| **Backend 컴포넌트** | BC-06 FileManagerService, 공통 설정/미들웨어 |
| **Frontend 컴포넌트** | FC-07 LayoutModule (라우팅, 공통 레이아웃) |
| **Stories** | - (인프라 기반, 모든 스토리의 전제조건) |
| **산출물** | FastAPI 앱 구조, DB 스키마, 마이그레이션, 공통 설정 |

---

## Unit 2: unit-auth

| 항목 | 내용 |
|------|------|
| **이름** | unit-auth |
| **설명** | 사용자 인증 및 Face ID 본인 확인 |
| **범위** | Cognito 연동, 회원가입/로그인, Face ID 등록/검증 |
| **Backend 컴포넌트** | BC-01 AuthService, BC-02 FaceVerificationService |
| **Frontend 컴포넌트** | FC-01 AuthModule, FC-02 FaceIDModule |
| **Stories** | US-01, US-02, US-03, US-04 |
| **산출물** | 인증 API, Face ID API, 로그인/가입 UI, 셀피 촬영 UI |

---

## Unit 3: unit-fitting

| 항목 | 내용 |
|------|------|
| **이름** | unit-fitting |
| **설명** | AI 가상 피팅 핵심 엔진 |
| **범위** | 전신/의류 이미지 업로드, 마스킹, 피팅 이미지 생성 (Mock) |
| **Backend 컴포넌트** | BC-03 FittingService |
| **Frontend 컴포넌트** | FC-03 FittingModule |
| **Stories** | US-05, US-06, US-07 |
| **산출물** | 이미지 업로드 API, 피팅 생성 API (Mock), 피팅 UI |

---

## Unit 4: unit-background

| 항목 | 내용 |
|------|------|
| **이름** | unit-background |
| **설명** | 커스텀 배경 생성 및 합성 |
| **범위** | 텍스트 프롬프트/이미지 업로드 기반 배경 변경 (Mock) |
| **Backend 컴포넌트** | BC-04 BackgroundService |
| **Frontend 컴포넌트** | FC-04 BackgroundModule |
| **Stories** | US-08, US-09 |
| **산출물** | 배경 생성 API (Mock), 배경 변경 UI |

---

## Unit 5: unit-recommend

| 항목 | 내용 |
|------|------|
| **이름** | unit-recommend |
| **설명** | AI 추천 (사이즈 조언 + 날씨 코디) |
| **범위** | 체형 분석, 날씨 API 연동, Claude 기반 추천 텍스트 (Mock) |
| **Backend 컴포넌트** | BC-05 RecommendService |
| **Frontend 컴포넌트** | FC-05 RecommendModule |
| **Stories** | US-10, US-11 |
| **산출물** | 추천 API (Mock), 추천 결과 UI |

---

## Unit 6: unit-result

| 항목 | 내용 |
|------|------|
| **이름** | unit-result |
| **설명** | 결과 이미지 다운로드 및 SNS 공유 |
| **범위** | 로컬 다운로드, 워터마크 삽입, 임시 공유 URL 생성 |
| **Backend 컴포넌트** | BC-07 ShareService |
| **Frontend 컴포넌트** | FC-06 ResultModule |
| **Stories** | US-12, US-13 |
| **산출물** | 다운로드 API, 공유 API, 결과 관리 UI |
