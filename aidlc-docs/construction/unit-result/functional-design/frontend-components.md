# Frontend Components — unit-result

## 1. ResultModule (FC-06)

### 1.1 DownloadSharePanel

**역할**: 다운로드/공유 액션 패널 (피팅 결과 또는 배경 결과 화면에 임베드)

**UI 요소**:
- "다운로드" 버튼
- "공유" 버튼

**동작**:
- 다운로드 클릭 → 즉시 JPEG 다운로드 실행
- 공유 클릭 → 워터마크 이미지 생성 → Web Share API 호출

### 1.2 DownloadAction

**역할**: 원본 해상도 JPEG 즉시 다운로드

**동작**:
1. "다운로드" 클릭
2. 서버에서 워터마크 삽입 + JPEG 생성
3. 브라우저 다운로드 트리거
4. 완료 토스트: "다운로드 완료!"

### 1.3 ShareAction

**역할**: Web Share API를 통한 공유 실행

**동작**:
1. 공유용 이미지 생성 요청 (JPEG, 워터마크 포함)
2. 임시 공유 URL 수신
3. `navigator.share()` 호출
4. 성공 → 토스트 "공유 완료!"
5. 실패 (API 미지원) → 폴백 UI

**폴백 UI** (Web Share API 미지원 시):
- 공유 URL 텍스트 표시
- "URL 복사" 버튼
- 클릭 시 클립보드 복사 + 토스트 "링크가 복사되었습니다"

### 1.4 ShareViewPage

**역할**: 공유 URL 접근 시 공개 열람 페이지

**UI 요소**:
- V-Suitcase 로고 헤더
- 결과 이미지 (확대 가능)
- "V-Suitcase에서 나도 해보기" CTA 버튼 (서비스 홈으로 링크)
- 만료 시: "이 공유 링크는 만료되었습니다" 안내

**특징**:
- 인증 불필요 (공개 페이지)
- OG 메타태그 포함 (SNS 미리보기 지원):
  - `og:title`: "V-Suitcase 피팅 결과"
  - `og:image`: 공유 이미지 URL
  - `og:description`: "AI 가상 피팅 결과를 확인해보세요!"

### 1.5 useResult Hook

**제공 기능**:
- `downloadImage(sourceImageId)` — 이미지 다운로드 (JPEG)
- `shareImage(sourceImageId)` — 공유 URL 생성 + Share API 호출
- `copyShareUrl(url)` — 클립보드 복사
- `isDownloading` — 다운로드 처리 중
- `isSharing` — 공유 처리 중
- `shareUrl` — 생성된 공유 URL

---

## 2. 라우트 구조

| 경로 | 컴포넌트 | 접근 조건 |
|------|----------|-----------|
| /share/:shareToken | ShareViewPage | 없음 (공개) |

**참고**: DownloadSharePanel은 독립 페이지가 아닌 피팅/배경 결과 페이지에 임베드되는 컴포넌트.

---

## 3. 다른 유닛과의 연동

| 연동 대상 | 트리거 | 전달 데이터 |
|-----------|--------|-------------|
| unit-fitting (FC-03) | FittingResultPage "다운로드/공유" | resultImageId, sourceType=FITTING |
| unit-background (FC-04) | BackgroundResultPage "다운로드/공유" | bgResultImageId, sourceType=BACKGROUND |
