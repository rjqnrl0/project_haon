# Business Logic — unit-result

## 1. ShareService (BC-07)

### 1.1 이미지 다운로드 (US-12)

**플로우**:
1. 사용자가 결과 이미지에서 "다운로드" 클릭
2. 워터마크 삽입 처리
3. JPEG 이미지 파일 생성 (원본 해상도)
4. 다운로드 URL 반환 → 브라우저 다운로드 트리거

**이미지 형식**:
| 형식 | 용도 | 품질 |
|------|------|------|
| JPEG | 원본 해상도 (단일 옵션) | 85% quality |

**비즈니스 규칙**:
- 다운로드 가능 대상: 피팅 결과, 배경 합성 결과
- 워터마크는 항상 삽입 (다운로드/공유 모두)
- 형식 선택 없음 — JPEG 고정
- 파일명 규칙: `vsuitcase_fitting_{timestamp}.jpg`

### 1.2 워터마크 삽입

**워터마크 사양**:
| 항목 | 값 |
|------|-----|
| 유형 | 텍스트 |
| 내용 | "V-Suitcase" |
| 위치 | 우하단 (마진 10px) |
| 폰트 크기 | 이미지 너비의 3% |
| 투명도 | 40% (반투명) |
| 색상 | 흰색 + 검은색 그림자 (가독성) |

**처리 알고리즘**:
```
Input: sourceImage, format (PNG/JPEG)
Output: watermarkedImage

1. canvas = copy(sourceImage)
2. fontSize = canvas.width * 0.03
3. textWidth = measureText("V-Suitcase", fontSize)
4. x = canvas.width - textWidth - 10
5. y = canvas.height - fontSize - 10
6. drawText(canvas, "V-Suitcase", x, y, opacity=0.4, color=white, shadow=black)
7. export(canvas, JPEG, quality=85)
8. return watermarkedImage
```

### 1.3 SNS 공유 (US-13)

**플로우**:
1. 사용자가 "공유" 클릭
2. 워터마크 삽입된 이미지 생성
3. 임시 공유 URL 생성 (30일 유효)
4. Web Share API 호출 (OS 기본 공유 시트)
5. 공유 시트에서 사용자가 대상 앱 선택

**임시 공유 URL 생성**:
- 경로: `/share/{shareToken}`
- shareToken: UUID v4 (추측 불가)
- 유효기간: 30일
- 만료 후: 404 반환
- 저장 위치: `temp/share/{shareToken}.{ext}`

**Web Share API 호출**:
```javascript
navigator.share({
  title: 'V-Suitcase 피팅 결과',
  text: 'AI 가상 피팅 결과를 확인해보세요!',
  url: shareUrl
})
```

**Web Share API 미지원 브라우저 대응**:
- 폴백: URL 복사 버튼 표시
- 클립보드 복사 후 "복사되었습니다" 토스트 메시지

### 1.4 공유 URL 관리

**생성 규칙**:
| 항목 | 값 |
|------|-----|
| URL 형식 | `{domain}/share/{shareToken}` |
| Token | UUID v4 |
| 유효기간 | 30일 |
| 접근 제한 | 없음 (URL 아는 누구나 열람 가능) |
| 이미지 포맷 | JPEG 85% (공유 최적화) |

**정리 메커니즘**:
- 백그라운드 정리 작업: 만료된 공유 파일 일괄 삭제
- 정리 주기: 매일 1회 (cron)

---

## 2. 접근 제어

- FULLY_AUTHENTICATED 상태 필수
- 본인 결과만 다운로드/공유 가능 (userId 검증)
- 공유 URL 접근: 인증 불필요 (공개 열람)

---

## 3. 에러 처리

| 상황 | 처리 |
|------|------|
| 원본 이미지 없음 (세션 만료) | "결과 이미지가 만료되었습니다. 다시 피팅해주세요" |
| 워터마크 처리 실패 | 원본 그대로 제공 (워터마크 스킵) |
| Web Share API 미지원 | URL 복사 폴백 |
| 공유 URL 만료 | "공유 링크가 만료되었습니다" 안내 페이지 |
