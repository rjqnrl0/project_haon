# Functional Design Plan — unit-background

## Unit Overview
- **Unit**: unit-background
- **Purpose**: 커스텀 배경 생성 및 합성
- **Scope**: 텍스트 프롬프트/이미지 업로드 기반 배경 변경 (Phase 1: Mock)
- **Backend Components**: BC-04 BackgroundService
- **Frontend Components**: FC-04 BackgroundModule
- **Stories**: US-08, US-09

---

## Plan Steps

- [x] Step 1: Define BackgroundService business logic (배경 생성 파이프라인)
- [x] Step 2: Define text prompt and image-based background workflows
- [x] Step 3: Define frontend BackgroundModule (프롬프트 입력, 결과 표시)
- [x] Step 4: Define error scenarios and edge cases
- [x] Step 5: Generate functional design artifacts

---

## Clarifying Questions

아래 질문에 답변해 주세요.

---

### Q1: 텍스트 프롬프트 배경 생성 — Phase 1 Mock 방식

텍스트 프롬프트로 배경을 요청할 때 Phase 1에서 어떻게 Mock 하시겠습니까?

- A) 사전 준비된 배경 이미지 세트에서 키워드 매칭으로 선택 (예: "파리" → 에펠탑 이미지)
- B) 단색 배경 또는 그라디언트로 대체 (프롬프트 무시)
- C) 무료 이미지 API (Unsplash 등) 에서 키워드 검색하여 배경 사용
- X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

### Q2: 이미지 업로드 배경 — 합성 방식

사용자가 배경 이미지를 직접 업로드할 때 피팅 결과와 어떻게 합성하시겠습니까?

- A) 피팅 결과에서 인물만 추출(배경 제거) 후 새 배경 위에 합성
- B) 피팅 결과 전체를 새 배경 위에 단순 오버레이
- C) Phase 1은 B(단순 오버레이), Phase 2에서 A(인물 추출) 전환
- X) Other (please describe after [Answer]: tag below)

[Answer]:  C

---

### Q3: 배경 변경 적용 대상

배경 변경은 어떤 이미지에 적용됩니까?

- A) 피팅 결과 이미지에만 적용 (피팅 완료 후 사용 가능)
- B) 피팅 결과 + 원본 전신 사진 모두 가능
- C) 어떤 이미지든 가능 (독립 기능)
- X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Q4: 배경 프롬프트 언어 지원

텍스트 프롬프트 입력을 어떤 언어로 지원하시겠습니까?

- A) 한국어만
- B) 한국어 + 영어
- C) 자유 입력 (언어 제한 없음, Phase 2에서 AI가 처리)
- X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

위 질문에 답변해 주시면 unit-background의 상세 기능 설계를 생성하겠습니다.
