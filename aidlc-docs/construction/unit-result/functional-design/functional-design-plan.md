# Functional Design Plan — unit-result

## Unit Overview
- **Unit**: unit-result
- **Purpose**: 결과 이미지 다운로드 및 SNS 공유
- **Scope**: 로컬 다운로드, 워터마크 삽입, 임시 공유 URL 생성
- **Backend Components**: BC-07 ShareService
- **Frontend Components**: FC-06 ResultModule
- **Stories**: US-12, US-13

---

## Plan Steps

- [x] Step 1: Define ShareService business logic (다운로드 + 공유)
- [x] Step 2: Define watermark and share URL generation
- [x] Step 3: Define frontend ResultModule (다운로드/공유 UI)
- [x] Step 4: Define error scenarios and edge cases
- [x] Step 5: Generate functional design artifacts

---

## Clarifying Questions

아래 질문에 답변해 주세요.

---

### Q1: 워터마크 디자인

결과 이미지에 삽입할 워터마크를 어떻게 구성하시겠습니까?

- A) 텍스트 워터마크 ("V-Suitcase" 반투명 텍스트, 우하단)
- B) 로고 이미지 워터마크 (서비스 로고 PNG, 우하단)
- C) 워터마크 없음 (다운로드/공유 모두 원본 그대로)
- X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Q2: 공유 URL 유효기간

SNS 공유용 임시 URL의 유효기간을 얼마로 하시겠습니까?

- A) 24시간
- B) 7일
- C) 30일
- X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

### Q3: 공유 대상 SNS

어떤 SNS 공유를 지원하시겠습니까?

- A) Web Share API 사용 (OS 기본 공유 시트 — 카카오톡, 인스타 등 자동 지원)
- B) 특정 SNS 직접 연동 (카카오톡, 인스타그램, 트위터 각각 버튼)
- C) URL 복사만 (사용자가 직접 SNS에 붙여넣기)
- X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Q4: 다운로드 이미지 품질

다운로드 시 이미지 품질/형식을 어떻게 제공하시겠습니까?

- A) 원본 해상도 JPEG (단일 옵션)
- B) 원본 + 압축 버전 2가지 선택 가능
- C) PNG(무손실) + JPEG(압축) 형식 선택 가능
- X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

위 질문에 답변해 주시면 unit-result의 상세 기능 설계를 생성하겠습니다.
