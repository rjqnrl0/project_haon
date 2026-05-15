# V-Suitcase — Story-to-Unit Mappings

## Unit → Stories

| Unit | Stories | Epic |
|------|---------|------|
| unit-core | (기반 인프라 — 직접 매핑 스토리 없음) | - |
| unit-auth | US-01, US-02, US-03, US-04 | Epic 1: 인증 및 본인 확인 |
| unit-fitting | US-05, US-06, US-07 | Epic 2: AI 가상 피팅 |
| unit-background | US-08, US-09 | Epic 3: 커스텀 배경 생성 |
| unit-recommend | US-10, US-11 | Epic 4: AI 추천 |
| unit-result | US-12, US-13 | Epic 5: 결과 관리 및 공유 |

## Story → Unit (역방향)

| Story | Unit | Priority |
|-------|------|----------|
| US-01 회원가입 | unit-auth | Must Have |
| US-02 로그인/로그아웃 | unit-auth | Must Have |
| US-03 Face ID 등록 | unit-auth | Must Have |
| US-04 본인 인증 검증 | unit-auth | Must Have |
| US-05 전신 사진 업로드 | unit-fitting | Must Have |
| US-06 의류 이미지 업로드 | unit-fitting | Must Have |
| US-07 가상 피팅 실행 | unit-fitting | Must Have |
| US-08 텍스트 배경 변경 | unit-background | Must Have |
| US-09 이미지 배경 변경 | unit-background | Must Have |
| US-10 사이즈 조언 | unit-recommend | Should Have |
| US-11 날씨 코디 추천 | unit-recommend | Should Have |
| US-12 결과 다운로드 | unit-result | Should Have |
| US-13 SNS 공유 | unit-result | Should Have |

## Coverage Verification

- Total Stories: 13
- Mapped Stories: 13
- Unmapped Stories: 0
- Coverage: **100%**
