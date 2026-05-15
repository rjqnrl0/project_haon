# Functional Design Plan — unit-fitting

## Unit Overview
- **Unit**: unit-fitting
- **Purpose**: AI 가상 피팅 핵심 엔진
- **Scope**: 전신/의류 이미지 업로드, 마스킹, 피팅 이미지 생성 (Phase 1: Mock)
- **Backend Components**: BC-03 FittingService
- **Frontend Components**: FC-03 FittingModule
- **Stories**: US-05, US-06, US-07

---

## Plan Steps

- [x] Step 1: Define FittingService business logic (이미지 처리 파이프라인)
- [x] Step 2: Define image upload and validation rules
- [x] Step 3: Define frontend FittingModule (업로드 UI, 피팅 결과 표시)
- [x] Step 4: Define error scenarios and edge cases
- [x] Step 5: Generate functional design artifacts

---

## Clarifying Questions

아래 질문에 답변해 주세요.

---

### Q1: 피팅 파이프라인 Phase 1 Mock 구현 방식

Phase 1에서 AI 모델 없이 피팅 결과를 어떻게 Mock 하시겠습니까?

- A) 전신 사진 위에 의류 이미지를 단순 오버레이 (위치/크기 고정)
- B) 미리 준비된 샘플 결과 이미지를 반환 (하드코딩)
- C) 전신 사진에 의류를 카테고리 기반 위치에 리사이즈하여 합성 (간단한 이미지 처리)
- X) Other (please describe after [Answer]: tag below)

[Answer]:  C

---

### Q2: 의류 카테고리 처리

의류 카테고리(상의/하의/원피스/아우터/액세서리)별로 동시에 여러 벌 피팅이 가능해야 합니까?

- A) 단일 의류만 (한 번에 1벌씩)
- B) 카테고리별 조합 가능 (상의 1 + 하의 1 동시)
- C) 자유 조합 (여러 벌 겹쳐 입기 가능)
- X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

### Q3: 전신 사진 유효성 검증 수준

전신 사진 업로드 시 검증을 어느 수준까지 하시겠습니까?

- A) 파일 형식/크기만 검증 (JPG/PNG, 10MB 이내)
- B) A + 이미지 해상도 최소 기준 검증 (예: 640x480 이상)
- C) A + B + 전신 포함 여부 기본 검증 (Phase 2에서 AI로, Phase 1에서는 Mock)
- X) Other (please describe after [Answer]: tag below)

[Answer]:  C

---

### Q4: 피팅 결과 이미지 저장 정책

생성된 피팅 결과 이미지를 어떻게 관리하시겠습니까?

- A) 임시 저장 (TTL 24시간 후 자동 삭제)
- B) 영구 저장 (사용자가 명시적으로 삭제할 때까지)
- C) 세션 기반 (로그아웃 시 삭제, 로그인 중에만 유지)
- X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

### Q5: 피팅 실행 시 본인 인증 시점

전신 사진 업로드 시 본인 인증(Face ID)을 어느 시점에 수행하시겠습니까?

- A) 전신 사진 업로드 직후 자동 (매번)
- B) 최초 1회만 인증, 같은 세션에서는 재인증 불필요
- C) 전신 사진이 바뀔 때만 재인증 (같은 사진 재사용 시 스킵)
- X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

위 질문에 답변해 주시면 unit-fitting의 상세 기능 설계를 생성하겠습니다.
