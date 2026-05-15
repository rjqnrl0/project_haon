# Business Logic — unit-background

## 1. BackgroundService (BC-04)

### 1.1 텍스트 프롬프트 배경 생성 (US-08)

**플로우**:
1. 사용자가 텍스트 프롬프트 입력 (자유 언어)
2. 프롬프트에서 키워드 추출 (Phase 1: 단순 공백 분리)
3. Unsplash API 호출 (키워드 검색)
4. 검색 결과 중 적합한 이미지 선택
5. 피팅 결과 이미지와 합성
6. 결과 반환

**Phase 1 구현 (Unsplash Mock)**:
1. 프롬프트 텍스트를 Unsplash Search API의 query로 전달
2. 상위 5개 결과 반환 → 사용자 선택 또는 첫 번째 자동 사용
3. 선택된 배경 이미지 다운로드
4. 피팅 결과 이미지를 배경 위에 단순 오버레이 합성

**Phase 2 전환**:
- Unsplash 검색 → Stability AI (Bedrock) 배경 생성
- 단순 오버레이 → SAM 인물 추출 + 배경 합성

**비즈니스 규칙**:
- 프롬프트 최대 길이: 200자
- 언어 제한 없음 (Unsplash는 영문 검색 최적화 — 내부적으로 영문 변환 고려)
- 빈 프롬프트 거부
- 검색 결과 없을 시 기본 배경 제공 (단색 흰색)

### 1.2 이미지 업로드 배경 (US-09)

**플로우**:
1. 사용자가 배경 이미지 업로드
2. 이미지 유효성 검증 (JPG/PNG, 10MB 이내)
3. 피팅 결과 이미지와 합성
4. 결과 반환

**Phase 1 합성 방식 (단순 오버레이)**:
1. 배경 이미지를 피팅 결과와 동일 크기로 리사이즈
2. 피팅 결과 이미지를 배경 중앙에 오버레이
3. 결과 이미지 생성

**Phase 2 전환**:
- 단순 오버레이 → 인물 세그멘테이션 (SAM) + 배경 교체 합성

**비즈니스 규칙**:
- 지원 형식: JPG, PNG
- 최대 크기: 10MB
- 최소 해상도: 640x480
- 배경 이미지는 피팅 결과 해상도에 맞춰 자동 리사이즈

### 1.3 배경 합성 엔진

**Phase 1 — 단순 오버레이 알고리즘**:
```
Input: fittingResultImage, backgroundImage
Output: compositeImage

1. bgResized = resize(backgroundImage, fittingResultImage.dimensions)
2. compositeImage = copy(bgResized)
3. overlay(compositeImage, fittingResultImage, position=center)
4. return compositeImage
```

**Phase 2 — 인물 추출 합성 알고리즘**:
```
Input: fittingResultImage, backgroundImage
Output: compositeImage

1. personMask = SAM.segment(fittingResultImage, target="person")
2. personOnly = applyMask(fittingResultImage, personMask)
3. bgResized = resize(backgroundImage, fittingResultImage.dimensions)
4. compositeImage = composite(bgResized, personOnly, mask=personMask)
5. return compositeImage
```

### 1.4 Unsplash API 연동

**API 사용 방식**:
- Endpoint: `GET /search/photos`
- Parameters: `query={prompt}`, `per_page=5`, `orientation=portrait`
- 응답에서 `regular` 크기 URL 사용
- Rate Limit: 50 requests/hour (Demo), 5000/hour (Production)

**에러 처리**:
| 상황 | 처리 |
|------|------|
| API 응답 없음/타임아웃 | 기본 배경(흰색) 사용 + 에러 메시지 |
| 검색 결과 0건 | "검색 결과가 없습니다. 다른 키워드를 시도해주세요" |
| Rate Limit 초과 | "잠시 후 다시 시도해주세요" 메시지 |

---

## 2. 접근 제어

- 배경 변경은 피팅 결과 이미지에만 적용 가능
- 피팅 미완료 시 배경 변경 기능 비활성화
- FULLY_AUTHENTICATED 상태 필수

---

## 3. 결과 관리

- 배경 변경 결과도 세션 기반 저장 (unit-fitting과 동일 정책)
- 로그아웃 시 자동 삭제
- 이전 피팅 결과는 유지 (배경 변경은 새 결과 이미지 생성)
