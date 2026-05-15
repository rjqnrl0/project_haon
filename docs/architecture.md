# V-Suitcase — 시스템 아키텍처 및 기술 스택

## 1. 기술 스택 (Tech Stack)

> 백엔드 구축 및 API 키 관리 부담을 최소화하고 프론트엔드 기능에 집중하는 Serverless 환경

| 레이어 | 기술 | 비고 |
|--------|------|------|
| **Frontend** | React (또는 Vue.js), Tailwind CSS | 컴포넌트 기반 UI |
| **Build Tool** | Vite | 빠른 HMR 및 번들링 |
| **Deployment** | Vercel | CI/CD 및 정적 호스팅 |
| **BaaS** | Firebase | 인증, 실시간 DB, Storage |
| **AI — 이미지 분석** | AWS Rekognition | 인물/의류 영역 감지 |
| **AI — 이미지 분할** | SAM (Segment Anything Model) | 정밀 마스킹 |
| **AI — 이미지 생성** | AWS Bedrock Titan | In-painting / 배경 합성 |
| **AI — 텍스트 분석** | Claude 3.5 Sonnet | 스타일링 추천 생성 |
| **Serverless** | AWS Lambda | 이미지 전처리·생성 파이프라인 |
| **모니터링** | AWS CloudWatch | 추론 실패율, 사용자 통계 |
| **Version Control** | Git / GitHub | 소스 관리 및 협업 |

---

## 2. 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────┐
│                        Client (Vercel)                       │
│              React + Tailwind CSS + Vite                     │
│  ① 전신 사진 업로드   ④ 결과 렌더링 & SNS 공유(워터마크)    │
└────────────┬─────────────────────────────┬───────────────────┘
             │ Upload                      │ Result
             ▼                             ▲
┌────────────────────────┐     ┌───────────────────────────────┐
│   Firebase Storage     │     │     Firebase Firestore        │
│  (원본 이미지 저장)     │     │  (생성 결과 메타데이터 저장)  │
└────────────┬───────────┘     └───────────────────────────────┘
             │ Trigger
             ▼
┌─────────────────────────────────────────────────────────────┐
│              AWS Lambda — Pre-process                        │
│  ② 이미지 분석 및 마스킹                                     │
│  • AWS Rekognition  : 인물 감지 및 의류 영역 인식            │
│  • SAM              : 의류/인물 경계선 정밀 마스킹           │
└─────────────────────────┬───────────────────────────────────┘
                          │ Masked Image
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              AWS Lambda — Generation                         │
│  ③ 가상 피팅 이미지 생성                                     │
│  • AWS Bedrock Titan : 배경 합성 + In-painting               │
│  • 광원·그림자·텍스처 보존 처리                              │
└─────────────────────────┬───────────────────────────────────┘
                          │ Generated Image
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              AI Analysis — Claude 3.5 Sonnet                 │
│  ③-b 피팅 결과 분석 및 텍스트 생성                           │
│  • 체형(어깨선·허리선) 기반 사이즈 추천                      │
│  • 여행지 실시간 날씨 API 연동 → 날씨 맞춤 코디 제안         │
└─────────────────────────┬───────────────────────────────────┘
                          │ Image + Text
                          ▼
                   Client (Result & Share)
```

---

## 3. 데이터 흐름 요약

| 단계 | 주체 | 처리 내용 |
|------|------|-----------|
| ① 업로드 | Client → Firebase Storage | 사용자 전신 사진 저장, Signed URL 발급 |
| ② 전처리 | Lambda (Pre-process) | Rekognition으로 인물 감지 → SAM으로 의류 영역 마스킹 |
| ③ 생성 | Lambda (Generation) | Bedrock Titan In-painting으로 가상 피팅 이미지 생성 |
| ③-b 분석 | Claude 3.5 Sonnet | 피팅 이미지 분석 → 사이즈·날씨 추천 텍스트 생성 |
| ④ 반환 | Client ← Firebase | 최종 이미지 + 텍스트 렌더링, 워터마크 처리 후 SNS 공유 |

---

## 4. 보안 설계

- **Signed URL**: Firebase Storage 원본 및 Lambda 결과 이미지 모두 Signed URL로만 접근 허용 — 무단 직접 접근 차단
- **API Key 격리**: 모든 외부 서비스 API Key는 Lambda 환경변수(AWS Secrets Manager) 또는 Firebase 서버 사이드에서만 관리 — 클라이언트 노출 금지
- **인증**: Firebase Authentication을 통한 사용자 세션 관리

---

## 5. 확장 고려사항

| 항목 | 현재 | 확장 방향 |
|------|------|-----------|
| 이미지 생성 모델 | Bedrock Titan | 고품질 모델(SDXL 등) 교체 가능 |
| 상품 데이터 파이프라인 | 수동 등록 | 제휴 쇼핑몰 연동 → 자동 배경 제거 스케줄러 (REQ-06) |
| 공간 스타일링 | 미구현 (확장 기능) | AI My Room Interior — 가전·가구 가상 배치 |
| 모니터링 | CloudWatch 기본 | 추론 실패율·UX 퍼널 통계 대시보드 고도화 (REQ-07) |
