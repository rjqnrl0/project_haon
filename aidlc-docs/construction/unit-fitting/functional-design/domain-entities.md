# Domain Entities — unit-fitting

## 1. BodyImage

| 속성 | 타입 | 설명 |
|------|------|------|
| imageId | string (UUID) | PK |
| sessionId | string | 세션 식별자 |
| userId | string (UUID) | FK → User |
| filePath | string | 임시 저장 경로 |
| fileHash | string (MD5) | 중복 감지용 |
| width | number | 이미지 너비 (px) |
| height | number | 이미지 높이 (px) |
| verified | boolean | 본인 인증 완료 여부 |
| uploadedAt | ISO timestamp | 업로드 시각 |

## 2. ClothingImage

| 속성 | 타입 | 설명 |
|------|------|------|
| clothingId | string (UUID) | PK |
| sessionId | string | 세션 식별자 |
| userId | string (UUID) | FK → User |
| category | ClothingCategory | 의류 카테고리 |
| filePath | string | 임시 저장 경로 |
| zIndex | number | 레이어 순서 |
| uploadedAt | ISO timestamp | 업로드 시각 |

## 3. ClothingCategory (Enum)

| 값 | 설명 |
|----|------|
| TOP | 상의 |
| BOTTOM | 하의 |
| DRESS | 원피스 |
| OUTER | 아우터 |
| ACCESSORY | 액세서리 |

## 4. FittingRequest

| 속성 | 타입 | 설명 |
|------|------|------|
| requestId | string (UUID) | PK |
| sessionId | string | 세션 식별자 |
| userId | string (UUID) | FK → User |
| bodyImageId | string (UUID) | FK → BodyImage |
| clothingIds | string[] | FK → ClothingImage[] |
| status | FittingStatus | 처리 상태 |
| createdAt | ISO timestamp | 요청 시각 |

## 5. FittingResult

| 속성 | 타입 | 설명 |
|------|------|------|
| resultId | string (UUID) | PK |
| requestId | string (UUID) | FK → FittingRequest |
| sessionId | string | 세션 식별자 |
| userId | string (UUID) | FK → User |
| resultFilePath | string | 결과 이미지 저장 경로 |
| resultUrl | string | 접근 URL |
| createdAt | ISO timestamp | 생성 시각 |

## 6. FittingStatus (Enum)

| 값 | 설명 |
|----|------|
| PENDING | 대기 중 |
| PROCESSING | 처리 중 |
| COMPLETED | 완료 |
| FAILED | 실패 |

## 7. ImageValidation

| 속성 | 타입 | 설명 |
|------|------|------|
| isValidFormat | boolean | JPG/PNG 여부 |
| isValidSize | boolean | 10MB 이하 여부 |
| isValidResolution | boolean | 640x480 이상 여부 |
| hasFullBody | boolean | 전신 포함 여부 (Phase 1: always true) |

## 8. Entity Relationships

```
User (1) ---- (*) BodyImage
User (1) ---- (*) ClothingImage
User (1) ---- (*) FittingRequest
FittingRequest (1) ---- (1) BodyImage
FittingRequest (1) ---- (*) ClothingImage
FittingRequest (1) ---- (0..1) FittingResult
```
