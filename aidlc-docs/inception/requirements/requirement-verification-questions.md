# Requirements Verification Questions — V-Suitcase

아래 질문에 답변해 주세요. 각 질문의 [Answer]: 태그 뒤에 선택지 알파벳(A, B, C, D, E)을 기입하거나, E를 선택한 경우 직접 설명을 작성해 주세요.

---

## Q1. 프론트엔드 프레임워크 선택

아키텍처 문서에 "React (또는 Vue.js)"로 기재되어 있습니다. 어떤 프레임워크를 사용하시겠습니까?

- A) React (권장 — 생태계 풍부, 가상 피팅 UI 라이브러리 지원)
- B) Vue.js
- C) Next.js (React 기반 SSR/SSG 포함)
- E) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Q2. 초기 개발 범위 (MVP Scope)

요구사항에 3개 핵심 기능(가상 피팅, 배경 생성, 공간 스타일링)이 있습니다. MVP로 어디까지 구현하시겠습니까?

- A) 가상 피팅 기능만 (REQ-01~03 + REQ-04~05)
- B) 가상 피팅 + 커스텀 배경 생성
- C) 전체 기능 (가상 피팅 + 배경 + 공간 스타일링)
- D) 가상 피팅 + 배경 생성 + 관리/모니터링(REQ-06~07)
- E) Other (please describe after [Answer]: tag below)

[Answer]: B

---

## Q3. 인증 및 사용자 관리 범위

Firebase Authentication 사용이 명시되어 있습니다. 초기 지원할 인증 방식은?

- A) 이메일/비밀번호만
- B) 이메일/비밀번호 + Google 소셜 로그인
- C) 이메일/비밀번호 + Google + Kakao (한국 사용자 대상)
- D) 게스트 모드(비회원 제한적 체험) + 이메일/비밀번호 + Google
- E) Other (please describe after [Answer]: tag below)

[Answer]: E (AWS 서비스들을 이용하여 서비리스 개발 방법 말고 EC2 S3등을 이용하여 서버에 배포 할 예정)

---

## Q4. AI 파이프라인 구현 방식

실제 AWS 서비스(Rekognition, SAM, Bedrock)를 바로 연동할 계획인지, 아니면 프론트엔드 UI를 먼저 구축하고 AI는 목업(Mock)으로 진행할지 결정이 필요합니다.

- A) 실제 AWS AI 서비스 즉시 연동 (AWS 계정 및 API 키 준비됨)
- B) 프론트엔드 UI 먼저 구축 + AI 파이프라인은 Mock API로 대체 (이후 연동)
- C) 프론트엔드 + Firebase 인증/Storage 연동까지만, Lambda는 Mock
- E) Other (please describe after [Answer]: tag below)

[Answer]: B

---

## Q5. 상품 데이터 소스

가상 피팅에 사용할 의류/상품 이미지는 어디서 가져옵니까?

- A) 직접 관리하는 상품 DB (Firebase Firestore에 수동 등록)
- B) 외부 쇼핑몰 API 연동 (특정 쇼핑몰이 있다면 명시해 주세요)
- C) 샘플 이미지로 시작 (MVP 단계에서는 하드코딩된 샘플 상품)
- D) 사용자가 직접 의류 이미지를 업로드
- E) Other (please describe after [Answer]: tag below)

[Answer]:  D

---

## Q6. 다국어 지원

- A) 한국어 전용
- B) 한국어 + 영어 (i18n 기반 구조 설계)
- C) 한국어 우선, 향후 다국어 확장 가능 구조만 마련
- E) Other (please describe after [Answer]: tag below)

[Answer]:  C

---

## Q7. 배포 환경 확인

Vercel 배포가 명시되어 있습니다. 현재 Vercel 계정이 준비되어 있습니까?

- A) 예, Vercel 계정 준비됨 (바로 배포 가능)
- B) 아직 없음, 로컬 개발만 먼저 진행
- C) Vercel 대신 다른 호스팅 사용 희망 (명시해 주세요)
- E) Other (please describe after [Answer]: tag below)

[Answer]:  C (AWS EC2)

---

## Q8. Security Extension Opt-In

보안 확장 규칙(SECURITY-01~15)을 블로킹 제약조건으로 적용하시겠습니까?

- A) Yes — 모든 SECURITY 규칙을 블로킹 제약으로 적용 (프로덕션 수준 권장)
- B) No — SECURITY 규칙 건너뛰기 (프로토타입/실험 프로젝트에 적합)
- C) 일부만 적용 (어떤 규칙을 적용할지 설명해 주세요)
- E) Other (please describe after [Answer]: tag below)

[Answer]:  B

---

## 답변 방법

각 질문의 `[Answer]:` 뒤에 선택 알파벳을 적어주세요. 예시:
```
[Answer]: B
```

모든 답변이 완료되면 Requirements Analysis를 진행하겠습니다.
