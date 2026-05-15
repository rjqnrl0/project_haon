# Functional Design Plan — unit-recommend

## Unit Overview
- **Unit**: unit-recommend
- **Purpose**: AI 추천 (사이즈 조언 + 날씨 코디)
- **Scope**: 체형 분석, 날씨 API 연동, Claude 기반 추천 텍스트 (Phase 1: Mock)
- **Backend Components**: BC-05 RecommendService
- **Frontend Components**: FC-05 RecommendModule
- **Stories**: US-10, US-11

---

## Plan Steps

- [x] Step 1: Define RecommendService business logic (사이즈 추천 + 날씨 코디)
- [x] Step 2: Define weather API integration and data flow
- [x] Step 3: Define frontend RecommendModule (추천 결과 표시 UI)
- [x] Step 4: Define error scenarios and edge cases
- [x] Step 5: Generate functional design artifacts

---

## Clarifying Questions

아래 질문에 답변해 주세요.

---

### Q1: 사이즈 추천 — Phase 1 Mock 방식

사이즈 조언을 Phase 1에서 어떻게 Mock 하시겠습니까?

- A) 의류 카테고리별 고정 사이즈 표 반환 (예: "상의 → M 추천")
- B) 사용자 신체 정보 입력(키/몸무게) 기반 간단한 룰 계산
- C) 하드코딩된 추천 텍스트 반환 (AI 응답 형식 미리보기용)
- X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

### Q2: 날씨 코디 추천 — 날씨 API 선택

날씨 정보를 어떤 API에서 가져오시겠습니까?

- A) OpenWeatherMap (무료 tier, 글로벌 커버리지)
- B) 기상청 공공데이터 API (한국 특화, 정확도 높음)
- C) Phase 1에서는 Mock (하드코딩된 날씨 데이터), Phase 2에서 실제 API 연동
- X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Q3: 여행지 입력 방식

날씨 코디 추천을 위한 여행지를 어떻게 입력받으시겠습니까?

- A) 텍스트 자유 입력 (도시명)
- B) 미리 정의된 인기 도시 목록에서 선택
- C) 텍스트 입력 + 자동완성 (인기 도시 추천)
- X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

### Q4: 추천 결과 표시 형식

추천 결과를 어떤 형식으로 사용자에게 보여주시겠습니까?

- A) 간단한 텍스트 카드 (사이즈 + 코디 팁 1~2줄)
- B) 상세 카드 (사이즈 표 + 코디 설명 + 관련 의류 이미지 추천)
- C) 대화형 (챗봇 형태로 추가 질문 가능)
- X) Other (please describe after [Answer]: tag below)

[Answer]: B

---

위 질문에 답변해 주시면 unit-recommend의 상세 기능 설계를 생성하겠습니다.
