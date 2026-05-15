# Domain Entities — unit-result

## 1. DownloadRequest

| 속성 | 타입 | 설명 |
|------|------|------|
| downloadId | string (UUID) | PK |
| userId | string (UUID) | FK → User |
| sourceImageId | string (UUID) | 원본 결과 이미지 ID |
| sourceType | SourceType | 이미지 출처 유형 |
| watermarked | boolean | 워터마크 삽입 여부 |
| outputPath | string | 생성된 파일 경로 |
| createdAt | ISO timestamp | 요청 시각 |

## 2. SourceType (Enum)

| 값 | 설명 |
|----|------|
| FITTING_RESULT | 피팅 결과 이미지 |
| BACKGROUND_RESULT | 배경 합성 결과 이미지 |

## 3. ShareLink

| 속성 | 타입 | 설명 |
|------|------|------|
| shareId | string (UUID) | PK |
| shareToken | string (UUID v4) | URL 토큰 (공개) |
| userId | string (UUID) | FK → User (생성자) |
| sourceImageId | string (UUID) | 원본 결과 이미지 ID |
| sourceType | SourceType | 이미지 출처 유형 |
| sharedFilePath | string | 공유용 이미지 저장 경로 |
| shareUrl | string | 전체 공유 URL |
| expiresAt | ISO timestamp | 만료 시각 (생성 + 30일) |
| createdAt | ISO timestamp | 생성 시각 |

## 5. SharePageView (공유 URL 열람 시)

| 속성 | 타입 | 설명 |
|------|------|------|
| shareToken | string | URL 토큰 |
| imageUrl | string | 이미지 URL |
| isExpired | boolean | 만료 여부 |
| title | string | 페이지 제목 ("V-Suitcase 피팅 결과") |

## 6. WatermarkConfig

| 속성 | 타입 | 설명 |
|------|------|------|
| text | string | "V-Suitcase" |
| position | string | "bottom-right" |
| margin | number | 10 (px) |
| fontSizeRatio | number | 0.03 (이미지 너비 대비) |
| opacity | number | 0.4 |
| color | string | "#FFFFFF" |
| shadowColor | string | "#000000" |

## 7. Entity Relationships

```
User (1) ---- (*) DownloadRequest
User (1) ---- (*) ShareLink
FittingResult (1) ---- (*) DownloadRequest
FittingResult (1) ---- (*) ShareLink
BackgroundResult (1) ---- (*) DownloadRequest
BackgroundResult (1) ---- (*) ShareLink
```
