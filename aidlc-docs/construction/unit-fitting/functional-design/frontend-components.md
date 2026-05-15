# Frontend Components — unit-fitting

## 1. FittingModule (FC-03)

### 1.1 FittingPage (메인 피팅 화면)

**역할**: 전신 사진 + 의류 업로드 + 피팅 실행을 하나의 플로우로 제공

**레이아웃**:
```
+-------------------------------------------+
|  [전신 사진 영역]  |  [의류 목록 영역]     |
|                    |  - 상의 슬롯          |
|  업로드/교체 버튼  |  - 하의 슬롯          |
|                    |  - 원피스 슬롯        |
|                    |  - 아우터 슬롯        |
|                    |  - 액세서리 슬롯      |
|                    |  [+ 의류 추가] 버튼   |
+-------------------------------------------+
|        [ 피팅 실행 ] 버튼                  |
+-------------------------------------------+
```

**동작**:
1. 전신 사진 업로드 → 미리보기 표시
2. 의류 이미지 업로드 → 카테고리 선택 → 목록에 추가
3. "피팅 실행" 클릭 → 로딩 표시 → 결과 화면 이동

### 1.2 BodyUploadSection

**역할**: 전신 사진 업로드 및 관리

**UI 요소**:
- 드래그앤드롭 영역 또는 파일 선택 버튼
- 업로드 프로그레스 바
- 미리보기 이미지
- 교체/삭제 버튼
- 본인 인증 상태 배지 (인증됨/미인증)

**동작**:
1. 파일 선택 또는 드래그앤드롭
2. 클라이언트 사이드 검증 (형식, 크기, 해상도)
3. 업로드 API 호출 + 프로그레스 표시
4. 새 사진일 경우 본인 인증 모달 트리거
5. 인증 성공 → "인증됨" 배지 표시
6. 인증 실패 → VerificationFailureModal (unit-auth)

### 1.3 ClothingUploadSection

**역할**: 의류 이미지 업로드 및 자유 조합 관리

**UI 요소**:
- "+ 의류 추가" 버튼
- 카테고리 선택 드롭다운 (상의/하의/원피스/아우터/액세서리)
- 업로드된 의류 목록 (썸네일 + 카테고리 태그)
- 각 의류 항목의 삭제 버튼
- 드래그로 순서(z-index) 변경

**동작**:
1. "+ 의류 추가" 클릭 → 카테고리 선택 모달
2. 카테고리 선택 후 파일 업로드
3. 업로드 완료 → 목록에 추가
4. 드래그로 레이어 순서 조정 가능
5. 여러 카테고리 자유 조합 가능

### 1.4 FittingResultPage

**역할**: 피팅 결과 이미지 표시 및 후속 액션

**UI 요소**:
- 결과 이미지 (확대/축소 가능)
- "배경 변경" 버튼 → unit-background로 이동
- "사이즈 추천" 버튼 → unit-recommend로 이동
- "다운로드" 버튼 → unit-result 호출
- "공유" 버튼 → unit-result 호출
- "다시 피팅" 버튼 → FittingPage로 돌아감

**동작**:
1. 피팅 완료 시 결과 이미지 표시
2. 후속 액션 선택 (배경 변경 / 추천 / 저장 / 공유)
3. "다시 피팅" → 의류 변경 후 재실행

### 1.5 FittingLoadingOverlay

**역할**: 피팅 처리 중 로딩 UI

**UI 요소**:
- 스피너/프로그레스 애니메이션
- 처리 중 안내 텍스트 ("AI가 옷을 입혀보고 있어요...")
- 예상 소요 시간 표시

### 1.6 useFitting Hook

**제공 기능**:
- `uploadBody(file)` — 전신 사진 업로드
- `uploadClothing(file, category)` — 의류 업로드
- `removeClothing(clothingId)` — 의류 제거
- `reorderClothing(clothingIds)` — 순서 변경
- `executeFitting()` — 피팅 실행
- `bodyImage` — 현재 전신 사진 정보
- `clothingList` — 업로드된 의류 목록
- `result` — 피팅 결과
- `status` — FittingStatus
- `isProcessing` — 처리 중 여부

---

## 2. 라우트 구조

| 경로 | 컴포넌트 | 접근 조건 |
|------|----------|-----------|
| /fitting | FittingPage | FULLY_AUTHENTICATED |
| /fitting/result/:resultId | FittingResultPage | FULLY_AUTHENTICATED |

---

## 3. 다른 유닛과의 연동

| 연동 대상 | 트리거 | 전달 데이터 |
|-----------|--------|-------------|
| unit-auth (FC-02) | 전신 사진 변경 시 | bodyImageId → 본인 인증 요청 |
| unit-background (FC-04) | "배경 변경" 클릭 | resultImageId |
| unit-recommend (FC-05) | "사이즈 추천" 클릭 | bodyImageId, clothingIds |
| unit-result (FC-06) | "다운로드/공유" 클릭 | resultImageId |
