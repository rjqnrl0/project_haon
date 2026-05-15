# Frontend Components — unit-background

## 1. BackgroundModule (FC-04)

### 1.1 BackgroundPage

**역할**: 배경 변경 메인 화면 — 텍스트 프롬프트 또는 이미지 업로드 선택

**레이아웃**:
```
+-------------------------------------------+
|  [현재 피팅 결과 미리보기]                |
+-------------------------------------------+
|  배경 변경 방법 선택:                     |
|  [텍스트로 생성]  |  [이미지 업로드]      |
+-------------------------------------------+
|  [입력/업로드 영역]                       |
+-------------------------------------------+
|  [배경 적용] 버튼                         |
+-------------------------------------------+
```

**진입 조건**: 피팅 결과 존재 (FittingResult 필수)

### 1.2 TextPromptSection

**역할**: 텍스트 프롬프트 입력 및 배경 검색

**UI 요소**:
- 프롬프트 입력 필드 (placeholder: "원하는 배경을 설명해주세요")
- 글자 수 카운터 (최대 200자)
- "배경 검색" 버튼
- 검색 결과 그리드 (Unsplash 이미지 5개 썸네일)
- 각 결과의 선택 버튼
- 촬영자 attribution 텍스트

**동작**:
1. 프롬프트 입력 (자유 언어)
2. "배경 검색" 클릭 → Unsplash 검색 API 호출
3. 결과 5개 그리드로 표시
4. 사용자가 원하는 배경 선택
5. "배경 적용" 클릭 → 합성 실행

### 1.3 ImageUploadSection

**역할**: 배경 이미지 직접 업로드

**UI 요소**:
- 드래그앤드롭 영역 또는 파일 선택 버튼
- 업로드 프로그레스 바
- 업로드된 이미지 미리보기
- 교체/삭제 버튼

**동작**:
1. 파일 선택 또는 드래그앤드롭
2. 클라이언트 검증 (형식, 크기)
3. 미리보기 표시
4. "배경 적용" 클릭 → 합성 실행

### 1.4 BackgroundResultPage

**역할**: 배경 합성 결과 표시

**UI 요소**:
- Before/After 비교 (슬라이더 또는 토글)
- 합성 결과 이미지 (확대/축소)
- "다른 배경 시도" 버튼
- "다운로드" 버튼 → unit-result
- "공유" 버튼 → unit-result
- "돌아가기" 버튼 → 피팅 결과 화면

### 1.5 BackgroundLoadingOverlay

**역할**: 배경 합성 처리 중 로딩 UI

**UI 요소**:
- 스피너 애니메이션
- "배경을 합성하고 있어요..." 안내 텍스트

### 1.6 useBackground Hook

**제공 기능**:
- `searchBackground(prompt)` — 텍스트 프롬프트로 배경 검색
- `uploadBackground(file)` — 배경 이미지 업로드
- `applyBackground(sourceImageId, backgroundOption)` — 배경 합성 실행
- `searchResults` — Unsplash 검색 결과 목록
- `result` — 합성 결과
- `status` — BackgroundStatus
- `isProcessing` — 처리 중 여부

---

## 2. 라우트 구조

| 경로 | 컴포넌트 | 접근 조건 |
|------|----------|-----------|
| /background/:resultId | BackgroundPage | FULLY_AUTHENTICATED + 피팅 결과 존재 |
| /background/result/:bgResultId | BackgroundResultPage | FULLY_AUTHENTICATED |

---

## 3. 다른 유닛과의 연동

| 연동 대상 | 트리거 | 전달 데이터 |
|-----------|--------|-------------|
| unit-fitting (FC-03) | 진입 시 | fittingResultId (소스 이미지) |
| unit-result (FC-06) | "다운로드/공유" 클릭 | bgResultImageId |
