# Business Logic — unit-fitting

## 1. FittingService (BC-03)

### 1.1 전신 사진 업로드 (Body Image Upload)

**플로우**:
1. 사용자가 전신 사진 선택/업로드
2. 파일 유효성 검증:
   - 형식: JPG, PNG
   - 크기: 최대 10MB
   - 해상도: 최소 640x480
3. 전신 포함 검증 (Phase 1: Mock — 항상 PASS 반환)
4. 본인 인증 트리거 (사진 변경 시에만):
   - 이전에 인증된 사진과 동일 → 스킵
   - 새 사진 → Face ID 검증 호출
5. 검증 통과 시 임시 저장 (`temp/fitting/{sessionId}/body.jpg`)
6. 업로드 완료 응답 반환 (imageId, thumbnailUrl)

**비즈니스 규칙**:
- 세션당 1장의 전신 사진만 활성 (새 업로드 시 이전 교체)
- 본인 인증은 전신 사진이 변경될 때만 재수행
- 동일 사진 재업로드 감지: 파일 해시(MD5) 비교

### 1.2 의류 이미지 업로드 (Clothing Image Upload)

**플로우**:
1. 사용자가 의류 이미지 선택/업로드
2. 파일 유효성 검증 (JPG/PNG, 10MB 이내)
3. 카테고리 선택 확인 (상의/하의/원피스/아우터/액세서리)
4. 임시 저장 (`temp/fitting/{sessionId}/clothing/{category}_{index}.jpg`)
5. 업로드 완료 응답 (clothingId, category, thumbnailUrl)

**비즈니스 규칙**:
- 자유 조합 가능: 여러 카테고리의 의류를 동시에 등록
- 같은 카테고리 내 복수 아이템 가능 (레이어링)
- 의류 순서(z-index) 관리: 업로드 순서대로 기본 적용, 사용자 조정 가능

### 1.3 가상 피팅 실행 (Fitting Execution)

**플로우**:
1. 피팅 요청 수신 (bodyImageId + clothingIds[])
2. 전신 사진 및 의류 이미지 로드
3. 본인 인증 상태 확인 (미인증 시 거부)
4. Phase 1 Mock 피팅 처리:
   - 카테고리별 위치 매핑 (아래 표 참조)
   - 전신 사진 비율에 맞춰 의류 리사이즈
   - 의류를 z-index 순서대로 합성
5. 결과 이미지 생성 및 임시 저장
6. 결과 반환 (resultImageId, resultUrl)

**카테고리별 합성 위치 (Phase 1 Mock)**:

| 카테고리 | 기준 위치 | 크기 비율 |
|----------|-----------|-----------|
| 상의 | 전신 상단 30~55% 영역 | 너비의 60% |
| 하의 | 전신 중단 50~80% 영역 | 너비의 55% |
| 원피스 | 전신 상단 30~80% 영역 | 너비의 60% |
| 아우터 | 상의 위 레이어, 동일 위치 | 너비의 65% |
| 액세서리 | 고정 위치 (목/손목 등) | 너비의 20% |

**Phase 2 전환 시**:
- Mock 합성 → SAM 마스킹 + Stability AI Inpainting
- 인터페이스 동일, 내부 구현만 교체

### 1.4 피팅 결과 관리

**저장 정책 — 세션 기반**:
- 로그인 중: 결과 이미지 유지
- 로그아웃 시: 해당 사용자 세션의 모든 임시 파일 삭제
- 세션 만료(토큰 만료 + 갱신 실패): 자동 정리 트리거

**정리 메커니즘**:
- 로그아웃 이벤트 → 해당 sessionId 디렉토리 전체 삭제
- 백그라운드 정리: 24시간 이상 미접근 세션 자동 삭제 (안전장치)

---

## 2. 본인 인증 연동 (unit-auth 의존)

### 인증 판단 로직

```
if (새 전신 사진 업로드) {
  currentBodyHash = hash(uploadedImage)
  if (currentBodyHash !== lastVerifiedBodyHash) {
    result = FaceVerificationService.verify(uploadedImage)
    if (result.verified) {
      lastVerifiedBodyHash = currentBodyHash
      proceed to fitting
    } else {
      reject with VERIFICATION_FAILED
    }
  } else {
    proceed to fitting (이미 인증된 사진)
  }
}
```

---

## 3. 이미지 처리 파이프라인 (Phase 1)

### Mock 합성 알고리즘

```
Input: bodyImage, clothingImages[]
Output: resultImage

1. resultImage = copy(bodyImage)
2. bodyDimensions = analyze(bodyImage) // 높이, 너비
3. for each clothing in clothingImages (sorted by z-index):
   a. position = getCategoryPosition(clothing.category, bodyDimensions)
   b. resized = resize(clothing.image, position.width, position.height)
   c. resultImage = overlay(resultImage, resized, position.x, position.y)
4. return resultImage
```

### 이미지 품질 설정

| 항목 | 값 |
|------|-----|
| 출력 포맷 | JPEG |
| 출력 품질 | 85% |
| 최대 출력 해상도 | 원본 전신 사진과 동일 |
| 알파 블렌딩 | 의류 이미지 투명 배경 지원 |
