# V-Suitcase — User Stories

## Epic 1: 인증 및 본인 확인

### US-01: 회원가입
**As a** 새로운 사용자
**I want to** 이메일/비밀번호로 회원가입하고 싶다
**So that** 서비스의 모든 기능을 이용할 수 있다

**Acceptance Criteria:**
- [ ] Cognito 기반 이메일/비밀번호 회원가입
- [ ] 이메일 인증 후 계정 활성화
- [ ] 가입 완료 시 Face ID 등록 화면으로 이동

---

### US-02: 로그인/로그아웃
**As a** 가입된 사용자
**I want to** 로그인/로그아웃 하고 싶다
**So that** 내 계정에 안전하게 접근할 수 있다

**Acceptance Criteria:**
- [ ] 이메일/비밀번호 로그인
- [ ] 토큰 기반 상태 유지
- [ ] 로그아웃 시 토큰 무효화

---

### US-03: Face ID 등록
**As a** 신규 가입 사용자
**I want to** 셀피를 촬영하여 기준 얼굴을 등록하고 싶다
**So that** 이후 본인 확인이 자동으로 이루어진다

**Acceptance Criteria:**
- [ ] 회원가입 직후 셀피 촬영 UI 제공
- [ ] Rekognition에 기준 얼굴 등록
- [ ] 등록 성공/실패 피드백
- [ ] 완료 후 메인 화면으로 이동

---

### US-04: 본인 인증 검증
**As a** 전신 사진을 업로드하는 사용자
**I want to** 자동으로 본인 확인이 되길 원한다
**So that** 타인 사진 도용이 방지된다

**Acceptance Criteria:**
- [ ] 전신 사진 얼굴 자동 감지
- [ ] 기준 얼굴과 비교 (유사도 90% 이상)
- [ ] 성공 시 피팅 진행, 실패 시 안내 메시지

---

## Epic 2: AI 가상 피팅

### US-05: 전신 사진 업로드
**As a** 가상 피팅을 원하는 사용자
**I want to** 전신 사진 1장을 업로드하고 싶다
**So that** 내 모습에 옷을 입혀볼 수 있다

**Acceptance Criteria:**
- [ ] JPG, PNG 지원 (최대 10MB)
- [ ] 업로드 프로그레스 표시
- [ ] 업로드 후 본인 인증 자동 수행

---

### US-06: 의류 이미지 업로드
**As a** 사용자
**I want to** 입어보고 싶은 옷 이미지를 업로드하고 싶다
**So that** 해당 옷을 가상으로 입혀볼 수 있다

**Acceptance Criteria:**
- [ ] 의류 이미지 업로드 (JPG, PNG, 최대 10MB)
- [ ] 카테고리 선택 (상의/하의/원피스/아우터/액세서리)
- [ ] 업로드 이미지 미리보기

---

### US-07: 가상 피팅 실행
**As a** 사진을 업로드한 사용자
**I want to** AI 합성 결과를 보고 싶다
**So that** 실제 착용한 듯한 모습을 확인할 수 있다

**Acceptance Criteria:**
- [ ] 전신 + 의류 조합으로 피팅 결과 생성
- [ ] 자연스러운 핏/질감/그림자 반영
- [ ] 로딩 인디케이터 표시
- [ ] 경계선 왜곡률 5% 미만

---

## Epic 3: 커스텀 배경 생성

### US-08: 텍스트 프롬프트 배경 변경
**As a** 피팅 결과를 확인한 사용자
**I want to** 텍스트로 원하는 배경을 입력하고 싶다
**So that** 여행지에서 찍은 듯한 이미지를 얻을 수 있다

**Acceptance Criteria:**
- [ ] 텍스트 입력 (예: "제주도 해변 노을")
- [ ] AI 배경 생성 및 합성
- [ ] 마음에 안 들면 재생성 가능

---

### US-09: 이미지 업로드 배경 변경
**As a** 특정 배경 이미지가 있는 사용자
**I want to** 배경 이미지를 직접 업로드하고 싶다
**So that** 원하는 정확한 배경에 합성할 수 있다

**Acceptance Criteria:**
- [ ] 배경 이미지 업로드 (JPG, PNG)
- [ ] 인물을 배경에 자연스럽게 합성
- [ ] 광원/그림자 자동 조정

---

## Epic 4: AI 추천

### US-10: 체형별 사이즈 조언
**As a** 피팅 결과를 확인한 사용자
**I want to** 사이즈 추천을 받고 싶다
**So that** 온라인 구매 시 사이즈 실패를 줄일 수 있다

**Acceptance Criteria:**
- [ ] 어깨선/허리선 분석
- [ ] 사이즈업/다운 추천 메시지
- [ ] Claude Opus 4.6 기반 자연어 조언

---

### US-11: 날씨 기반 코디 추천
**As a** 여행을 준비하는 사용자
**I want to** 여행지 날씨에 맞는 코디 추천을 받고 싶다
**So that** 기후에 맞는 옷을 준비할 수 있다

**Acceptance Criteria:**
- [ ] 여행지 도시명 입력
- [ ] 실시간 날씨 API 연동
- [ ] 날씨 맞춤 코디 제안 (Claude Opus 4.6)

---

## Epic 5: 결과 관리 및 공유

### US-12: 결과 이미지 다운로드
**As a** 피팅 결과에 만족한 사용자
**I want to** 이미지를 내 기기에 저장하고 싶다
**So that** 오프라인에서도 참고할 수 있다

**Acceptance Criteria:**
- [ ] 다운로드 버튼 → 로컬 저장
- [ ] 고해상도 PNG 다운로드

---

### US-13: SNS 공유
**As a** 결과를 공유하고 싶은 사용자
**I want to** 피팅 이미지를 SNS에 공유하고 싶다
**So that** 친구들에게 코디를 보여주거나 의견을 물을 수 있다

**Acceptance Criteria:**
- [ ] 워터마크("V-Suitcase") 자동 삽입
- [ ] Instagram, KakaoTalk 공유 버튼
- [ ] 공유 이미지는 임시 URL (영구 저장 안 함)

---

## Story Map Summary

| Epic | Stories | Priority |
|------|---------|----------|
| 인증 및 본인 확인 | US-01 ~ US-04 | Must Have |
| AI 가상 피팅 | US-05 ~ US-07 | Must Have |
| 커스텀 배경 생성 | US-08 ~ US-09 | Must Have |
| AI 추천 | US-10 ~ US-11 | Should Have |
| 결과 관리 및 공유 | US-12 ~ US-13 | Should Have |
