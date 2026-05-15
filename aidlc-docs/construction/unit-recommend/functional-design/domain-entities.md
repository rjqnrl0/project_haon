# Domain Entities — unit-recommend

## 1. SizeRecommendation

| 속성 | 타입 | 설명 |
|------|------|------|
| recommendationId | string (UUID) | PK |
| userId | string (UUID) | FK → User |
| fittingResultId | string (UUID) | FK → FittingResult |
| clothingCategory | ClothingCategory | 의류 카테고리 |
| recommendedSize | string | 추천 사이즈 (S/M/L/XL 등) |
| sizeChart | SizeChart | 사이즈 표 |
| fitAdvice | string | 핏 조언 텍스트 |
| stylingTip | string | 스타일링 팁 텍스트 |
| createdAt | ISO timestamp | 생성 시각 |

## 2. SizeChart

| 속성 | 타입 | 설명 |
|------|------|------|
| sizes | Map<string, SizeDetail> | 사이즈별 상세 정보 |

## 3. SizeDetail

| 속성 | 타입 | 설명 |
|------|------|------|
| label | string | 사이즈 라벨 (S, M, L, XL) |
| chest | string | 가슴둘레 범위 |
| waist | string | 허리둘레 범위 |
| length | string | 총장 범위 |

## 4. WeatherCodiRecommendation

| 속성 | 타입 | 설명 |
|------|------|------|
| recommendationId | string (UUID) | PK |
| userId | string (UUID) | FK → User |
| city | string | 여행지 도시명 |
| weatherData | WeatherForecast[] | 날씨 예보 데이터 |
| codiAdvice | string | 코디 추천 텍스트 |
| essentialItems | string[] | 필수 아이템 목록 |
| additionalTips | string | 추가 팁 |
| createdAt | ISO timestamp | 생성 시각 |

## 5. WeatherForecast

| 속성 | 타입 | 설명 |
|------|------|------|
| date | string (YYYY-MM-DD) | 예보 날짜 |
| tempMin | number | 최저 기온 (°C) |
| tempMax | number | 최고 기온 (°C) |
| feelsLike | number | 체감 온도 (°C) |
| condition | WeatherCondition | 날씨 상태 |
| precipitation | number | 강수 확률 (%) |
| humidity | number | 습도 (%) |

## 6. WeatherCondition (Enum)

| 값 | 설명 |
|----|------|
| CLEAR | 맑음 |
| CLOUDS | 흐림 |
| RAIN | 비 |
| SNOW | 눈 |
| DRIZZLE | 이슬비 |
| THUNDERSTORM | 뇌우 |

## 7. CityOption (자동완성용)

| 속성 | 타입 | 설명 |
|------|------|------|
| nameKo | string | 한국어 도시명 |
| nameEn | string | 영어 도시명 |
| country | string | 국가 코드 |
| isPopular | boolean | 인기 도시 여부 |

## 8. Entity Relationships

```
User (1) ---- (*) SizeRecommendation
User (1) ---- (*) WeatherCodiRecommendation
FittingResult (1) ---- (0..*) SizeRecommendation
WeatherCodiRecommendation (1) ---- (*) WeatherForecast
```
