# Functional Design Plan — unit-core

## Unit Overview
- **Unit**: unit-core
- **Purpose**: 프로젝트 기반 구조, 설정, DB 마이그레이션, 공통 유틸리티
- **Scope**: FastAPI 앱 초기화, DB 연결, 설정 관리, 임시 파일 관리 서비스
- **Components**: BC-06 FileManagerService, 공통 설정/미들웨어, FC-07 LayoutModule

---

## Plan Steps

- [x] Step 1: Define application configuration schema (환경 변수, .env 구조)
- [x] Step 2: Define database connection management (SQLAlchemy session lifecycle)
- [x] Step 3: Define FileManagerService business logic (임시 파일 생성/조회/삭제/TTL 만료 처리)
- [x] Step 4: Define middleware specifications (CORS, 에러 핸들링, 요청 로깅)
- [x] Step 5: Define database migration strategy (Alembic 설정, 마이그레이션 순서)
- [x] Step 6: Define frontend LayoutModule (라우팅 구조, 공통 레이아웃 컴포넌트)
- [x] Step 7: Generate functional design artifacts

---

## Clarifying Questions

아래 질문에 답변해 주세요. 각 질문의 [Answer]: 뒤에 선택지 문자(A, B, C 등)를 기입하거나, X를 선택하고 직접 설명해 주세요.

---

### Q1: 환경 설정 관리 방식

설정값(DB URL, Cognito ID, AWS 키 등)을 어떻게 관리하시겠습니까?

- A) `.env` 파일 + Pydantic Settings (로컬 개발에 적합, 가장 일반적)
- B) AWS Secrets Manager + Parameter Store (프로덕션 보안 강화)
- C) 환경 변수 직접 주입 (Docker/EC2 환경 변수)
- X) Other (please describe after [Answer]: tag below)

[Answer]: B

---

### Q2: DB 마이그레이션 실행 시점

Alembic 마이그레이션을 언제 실행하시겠습니까?

- A) 앱 시작 시 자동 실행 (`alembic upgrade head` at startup)
- B) 수동 실행만 (배포 시 별도 명령어)
- C) CI/CD 파이프라인에서 실행
- X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Q3: 임시 파일 저장 위치

피팅 결과 이미지 등 임시 파일을 어디에 저장하시겠습니까?

- A) 서버 로컬 디스크 (`/tmp/v-suitcase/` 또는 지정 경로)
- B) S3 임시 버킷 (TTL policy 적용)
- C) 인메모리 (Redis 등) — 작은 이미지만 가능
- X) Other (please describe after [Answer]: tag below)

[Answer]: B

---

### Q4: 만료 파일 정리 방식

`expires_at`이 지난 임시 파일을 어떻게 정리하시겠습니까?

- A) FastAPI BackgroundTasks로 주기적 정리 (앱 내 스케줄러)
- B) OS cron job (별도 스크립트 실행)
- C) APScheduler 라이브러리 (앱 내 스케줄러, 더 유연)
- X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Q5: 프론트엔드 라우팅 구조

React 라우팅을 어떻게 구성하시겠습니까?

- A) React Router v6 + 단일 레이아웃 (Header/Footer 공통)
- B) React Router v6 + 인증/비인증 레이아웃 분리
- C) Next.js App Router (SSR 지원)
- X) Other (please describe after [Answer]: tag below)

[Answer]: B

---

### Q6: 에러 응답 형식

API 에러 응답의 표준 형식을 어떻게 하시겠습니까?

- A) `{ "detail": "message", "code": "ERROR_CODE" }` (FastAPI 기본 확장)
- B) `{ "error": { "code": "...", "message": "...", "details": [...] } }` (중첩 구조)
- C) RFC 7807 Problem Details 표준 (`type`, `title`, `status`, `detail`)
- X) Other (please describe after [Answer]: tag below)

[Answer]:  A

---

위 질문에 답변해 주시면 unit-core의 상세 기능 설계를 생성하겠습니다.
