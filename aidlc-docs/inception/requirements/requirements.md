# V-Suitcase — Requirements Document

## 1. Intent Analysis

| 항목 | 분석 결과 |
|------|-----------|
| **User Request** | AI 기반 가상 피팅 시뮬레이션 플랫폼 개발 |
| **Request Type** | New Project |
| **Scope Estimate** | Multiple Components (React Frontend + FastAPI Backend + AI Pipeline) |
| **Complexity Estimate** | Complex |
| **Depth Level** | Comprehensive |

---

## 2. 확정된 기술 스택

| 레이어 | 기술 | 비고 |
|--------|------|------|
| **Frontend** | React + Tailwind CSS | 컴포넌트 기반 UI |
| **Build Tool** | Vite | 빠른 HMR 및 번들링 |
| **Frontend Hosting** | AWS S3 + CloudFront | 정적 파일 CDN 배포 |
| **Backend** | Python + FastAPI | EC2에서 운영 |
| **Authentication** | AWS Cognito | 관리형 인증 서비스 |
| **Database** | AWS RDS (PostgreSQL) | 관계형 DB |
| **File Storage** | 서버 휘발성 처리 (임시 저장 후 자동 삭제) | 사용자 로컬 다운로드 가능 |
| **AI — 본인 인증** | AWS Rekognition | Face ID 방식 본인 확인 (타인 사진 도용 방지) |
| **AI — 이미지 분할** | SAM (Segment Anything Model) | 정밀 마스킹 |
| **AI — 이미지 생성** | Stability AI (Amazon Bedrock) | In-painting / 배경 합성 |
| **AI — 텍스트 분석** | Claude Opus 4.6 (Amazon Bedrock) | 스타일링 추천 / 사이즈 조언 / 날씨 코디 |
| **Compute** | AWS EC2 | 백엔드 API 서버 |
| **Monitoring** | AWS CloudWatch | 모니터링 |
| **i18n** | 한국어 우선, 다국어 확장 가능 구조 | react-i18next 등 |

---

## 3. MVP 범위 (초기 개발 범위)

### 포함 (In Scope)
1. **AI 가상 피팅** (REQ-01 ~ REQ-03)
   - 사용자 전신 사진 업로드
   - 의류 이미지 업로드 (사용자 직접 제공)
   - AI 마스킹 + 가상 피팅 이미지 생성
2. **커스텀 배경 생성**
   - 텍스트 프롬프트 기반 배경 변경
   - 이미지 업로드 기반 배경 변경
3. **지능형 추천 및 분석** (REQ-04, REQ-05)
   - 체형별 사이즈 조언 (어깨선/허리선 분석 → 사이즈업/다운 추천)
   - 날씨 기반 코디 추천 (여행지 실시간 날씨 API 연동)
4. **본인 인증 (Face ID)**
   - AWS Rekognition 기반 얼굴 비교로 타인 사진 도용 방지
5. **인증 시스템**
   - AWS Cognito 기반 회원가입/로그인
6. **기본 UI**
   - 대한항공 벤치마킹 스타일 (신뢰감, 여행의 설렘, 여백, 직관적 플로우)

### 제외 (Out of Scope — 향후 확장)
- AI 공간 스타일링 (AI My Room Interior)
- 상품 데이터 파이프라인 (REQ-06)
- 로그/모니터링 대시보드 (REQ-07)

---

## 4. 기능 요구사항 (Functional Requirements)

### FR-01: 사용자 인증
- AWS Cognito를 통한 회원가입/로그인
- 이메일/비밀번호 기본 인증
- 세션 관리 및 토큰 기반 API 접근 제어

### FR-01b: 본인 인증 (Face ID)
- 최초 등록 시 셀피 촬영 → AWS Rekognition에 기준 얼굴 등록
- 전신 사진 업로드 시 얼굴 비교 → 본인 확인 후에만 피팅 진행
- 타인 사진 도용 방지 목적

### FR-02: 전신 사진 업로드
- 사용자가 전신 사진 1장 업로드
- 서버에서 임시 처리 후 자동 삭제 (영구 저장 안 함)
- 지원 형식: JPG, PNG (최대 10MB)

### FR-03: 의류 이미지 업로드
- 사용자가 원하는 의류/액세서리 이미지 직접 업로드
- 배경 제거(누끼) 자동 처리

### FR-04: AI 가상 피팅
- 전신 사진 + 의류 이미지 → AI 합성 결과 생성
- 자연스러운 핏, 질감, 그림자 반영
- 의류 카테고리별 자동 마스킹 (상의/하의/원피스/액세서리)

### FR-05: 커스텀 배경 생성
- 피팅 결과 이미지에 배경 변경 적용
- 텍스트 프롬프트 입력 방식
- 이미지 직접 업로드 방식

### FR-06: 결과 이미지 관리
- 결과 이미지는 서버에 영구 저장하지 않음
- 사용자가 로컬에 다운로드 가능
- 처리 완료 후 서버 임시 파일 자동 삭제

### FR-07: 체형별 사이즈 조언
- Claude Opus 4.6이 피팅 이미지에서 어깨선/허리선 분석
- 사이즈업/다운 추천 메시지 생성

### FR-08: 날씨 기반 코디 추천
- 여행지 실시간 날씨 API 연동 (OpenWeatherMap 등)
- 날씨에 맞는 코디 제안 텍스트 생성 (Claude Opus 4.6)

---

## 5. 비기능 요구사항 (Non-Functional Requirements)

### NFR-01: 성능
- 이미지 생성 대기 시간: 평균 7초 이내 (동시 접속 100명 기준)

### NFR-02: 정확도
- 의류 경계선 왜곡률 5% 미만

### NFR-03: 보안
- 사용자 이미지 클라우드 영구 저장 금지 (프라이버시 보호)
- 서버 임시 파일은 처리 완료 후 즉시 삭제
- API 접근은 Cognito 토큰 인증 필수
- HTTPS 통신 강제

### NFR-04: 확장성
- 다국어 확장 가능 구조 (i18n)
- AI 모델 교체 가능한 추상화 레이어

---

## 6. AI 파이프라인 전략

**MVP 단계**: 프론트엔드 UI 먼저 완성 + AI는 Mock API로 대체

```
[Phase 1 — 현재]
React UI + FastAPI Mock 엔드포인트
- /api/fitting → 샘플 결과 이미지 반환
- /api/background → 샘플 배경 합성 이미지 반환
- /api/face-verify → Mock 본인 확인 (항상 성공)
- /api/recommend/size → Mock 사이즈 추천 텍스트
- /api/recommend/weather → Mock 날씨 코디 텍스트

[Phase 2 — 이후]
실제 AWS AI 서비스 연동
- Rekognition: 얼굴 비교 본인 인증
- SAM: 의류 영역 마스킹
- Stability AI (Bedrock): 가상 피팅 이미지 생성
- Claude Opus 4.6 (Bedrock): 사이즈 조언 + 날씨 코디 추천
```

---

## 7. 시스템 아키텍처 (수정됨)

```
+------------------------------------------+
|        Client (S3 + CloudFront)          |
|         React + Tailwind + Vite          |
+------------------+-----------------------+
                   | API Calls (HTTPS)
                   v
+------------------------------------------+
|        AWS Cognito (Authentication)      |
+------------------------------------------+
                   |
                   v
+------------------------------------------+
|        EC2 — FastAPI Backend             |
|  - /api/auth   (Cognito 토큰 검증)      |
|  - /api/fitting (가상 피팅 처리)         |
|  - /api/background (배경 생성)           |
|  - 임시 파일 관리 (자동 삭제)            |
+------------------+-----------------------+
                   |
        +----------+----------+
        |                     |
        v                     v
+----------------+   +------------------+
| RDS PostgreSQL |   | AI Services      |
| (메타데이터)   |   | (Mock → Phase 2) |
+----------------+   +------------------+
```

---

## 8. 데이터 흐름

| 단계 | 주체 | 처리 내용 |
|------|------|-----------|
| 1 | Client → FastAPI | 전신 사진 + 의류 이미지 업로드 (multipart/form-data) |
| 2 | FastAPI | 임시 디렉토리에 저장, 처리 시작 |
| 2b | FastAPI → Rekognition | 업로드된 전신 사진 얼굴과 등록된 기준 얼굴 비교 (본인 확인) |
| 3 | FastAPI → AI | [Mock] 샘플 결과 반환 / [Phase 2] Stability AI 피팅 생성 |
| 4 | FastAPI → Client | 결과 이미지 Base64 또는 임시 URL 반환 |
| 5 | Client | 사용자에게 결과 표시, 로컬 다운로드 옵션 제공 |
| 6 | FastAPI | 임시 파일 자동 삭제 (TTL 기반) |

---

## 9. Extension Configuration

| Extension | Enabled | Decided At |
|---|---|---|
| Security Baseline | No | Requirements Analysis |
