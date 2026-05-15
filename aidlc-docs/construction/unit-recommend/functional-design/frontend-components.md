# Frontend Components — unit-recommend

## 1. RecommendModule (FC-05)

### 1.1 RecommendPage (메인 추천 화면)

**역할**: 사이즈 추천 + 날씨 코디 추천 통합 화면

**레이아웃**:
```
+-------------------------------------------+
|  [탭: 사이즈 추천 | 날씨 코디]            |
+-------------------------------------------+
|  [선택된 탭 콘텐츠 영역]                  |
+-------------------------------------------+
```

### 1.2 SizeRecommendSection

**역할**: 사이즈 추천 결과 표시 (상세 카드)

**UI 요소**:
- 추천 사이즈 메인 배지 (큰 글씨 "M" 등)
- 사이즈 표 (S/M/L/XL 가슴/허리/총장)
- 핏 조언 텍스트 블록
- 스타일링 팁 텍스트 블록
- 의류 카테고리별 탭 (상의/하의/원피스/아우터 각각)

**동작**:
1. 피팅 결과 페이지에서 "사이즈 추천" 클릭 시 진입
2. 자동으로 추천 API 호출 (피팅 결과 ID 기반)
3. 로딩 → 상세 카드 표시
4. 카테고리 탭 전환 시 해당 카테고리 추천 표시

**진입 조건**: 피팅 결과 필수

### 1.3 WeatherCodiSection

**역할**: 날씨 기반 코디 추천

**UI 요소**:
- 여행지 입력 필드 (자동완성 드롭다운 포함)
- 인기 도시 퀵 버튼 (상위 5개)
- "코디 추천 받기" 버튼
- 날씨 예보 카드 (5일, 기온/날씨 아이콘/강수확률)
- 코디 추천 카드:
  - 추천 의류 조합 텍스트
  - 필수 아이템 태그 목록
  - 추가 팁 텍스트

**동작**:
1. 여행지 입력 시작 → 자동완성 드롭다운 표시
2. 도시 선택 또는 자유 입력 확정
3. "코디 추천 받기" 클릭
4. OpenWeatherMap 날씨 조회 → 코디 추천 생성
5. 결과 상세 카드 표시

**진입 조건**: FULLY_AUTHENTICATED (피팅 결과 불필요)

### 1.4 CityAutocomplete

**역할**: 여행지 자동완성 입력 컴포넌트

**UI 요소**:
- 텍스트 입력 필드
- 자동완성 드롭다운 목록
- 각 항목: 도시명(한국어) + 국가
- 매칭 문자 하이라이트

**동작**:
1. 사용자 입력 시 클라이언트 필터링 (인기 도시 목록)
2. 한국어/영어 모두 매칭
3. 결과 없을 시 자유 입력 허용 ("Enter로 검색")
4. 선택 시 영문 도시명으로 API 호출

### 1.5 WeatherForecastCard

**역할**: 5일 날씨 예보 시각적 표시

**UI 요소**:
- 날짜별 카드 (가로 스크롤 또는 그리드)
- 각 카드: 날짜, 날씨 아이콘, 최고/최저 기온, 강수확률

### 1.6 useRecommend Hook

**제공 기능**:
- `getSizeRecommendation(fittingResultId)` — 사이즈 추천 요청
- `getWeatherCodi(city)` — 날씨 코디 추천 요청
- `searchCity(query)` — 도시 자동완성 검색
- `sizeResult` — 사이즈 추천 결과
- `weatherResult` — 날씨 코디 결과
- `weatherData` — 날씨 예보 데이터
- `isLoading` — 로딩 상태
- `error` — 에러 상태

---

## 2. 라우트 구조

| 경로 | 컴포넌트 | 접근 조건 |
|------|----------|-----------|
| /recommend | RecommendPage | FULLY_AUTHENTICATED |
| /recommend/size/:fittingResultId | SizeRecommendSection | FULLY_AUTHENTICATED + 피팅 결과 |
| /recommend/weather | WeatherCodiSection | FULLY_AUTHENTICATED |

---

## 3. 다른 유닛과의 연동

| 연동 대상 | 트리거 | 전달 데이터 |
|-----------|--------|-------------|
| unit-fitting (FC-03) | "사이즈 추천" 클릭 | fittingResultId |
| unit-fitting (FC-03) | 피팅 완료 후 자동 추천 제안 | fittingResultId |
