# Domain Entities — unit-background

## 1. BackgroundRequest

| 속성 | 타입 | 설명 |
|------|------|------|
| requestId | string (UUID) | PK |
| sessionId | string | 세션 식별자 |
| userId | string (UUID) | FK → User |
| sourceImageId | string (UUID) | 피팅 결과 이미지 ID |
| type | BackgroundType | 배경 생성 방식 |
| prompt | string | null | 텍스트 프롬프트 (TEXT_PROMPT 시) |
| uploadedBgPath | string | null | 업로드된 배경 경로 (IMAGE_UPLOAD 시) |
| status | BackgroundStatus | 처리 상태 |
| createdAt | ISO timestamp | 요청 시각 |

## 2. BackgroundType (Enum)

| 값 | 설명 |
|----|------|
| TEXT_PROMPT | 텍스트 프롬프트 기반 배경 |
| IMAGE_UPLOAD | 사용자 업로드 배경 |

## 3. BackgroundStatus (Enum)

| 값 | 설명 |
|----|------|
| PENDING | 대기 중 |
| SEARCHING | 배경 검색 중 (Unsplash) |
| COMPOSITING | 합성 중 |
| COMPLETED | 완료 |
| FAILED | 실패 |

## 4. BackgroundResult

| 속성 | 타입 | 설명 |
|------|------|------|
| resultId | string (UUID) | PK |
| requestId | string (UUID) | FK → BackgroundRequest |
| sessionId | string | 세션 식별자 |
| userId | string (UUID) | FK → User |
| resultFilePath | string | 합성 결과 저장 경로 |
| resultUrl | string | 접근 URL |
| backgroundSource | string | 사용된 배경 출처 (Unsplash URL 또는 upload path) |
| createdAt | ISO timestamp | 생성 시각 |

## 5. UnsplashSearchResult

| 속성 | 타입 | 설명 |
|------|------|------|
| imageId | string | Unsplash 이미지 ID |
| imageUrl | string | 이미지 URL (regular 크기) |
| thumbnailUrl | string | 썸네일 URL |
| description | string | null | 이미지 설명 |
| photographer | string | 촬영자 (attribution) |

## 6. Entity Relationships

```
FittingResult (1) ---- (*) BackgroundRequest
BackgroundRequest (1) ---- (0..1) BackgroundResult
BackgroundRequest (TEXT_PROMPT) ---- (*) UnsplashSearchResult
```
