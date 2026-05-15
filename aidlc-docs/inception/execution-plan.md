# V-Suitcase — Execution Plan

## Project Summary
- **Type**: Greenfield, Complex, Multi-component
- **Stack**: React + FastAPI + AWS (EC2, S3, RDS, Cognito, Bedrock, Rekognition)
- **MVP**: 가상 피팅 + 배경 생성 + 사이즈 조언 + 날씨 코디 + Face ID 인증

---

## Phase Determination

### INCEPTION PHASE — 실행 단계

| Stage | Execute | Reason |
|-------|---------|--------|
| Workspace Detection | DONE | Greenfield 확인 완료 |
| Reverse Engineering | SKIP | Greenfield — 기존 코드 없음 |
| Requirements Analysis | DONE | 요구사항 확정 및 승인 완료 |
| User Stories | **YES** | 다중 사용자 시나리오, 복잡한 UX 플로우 |
| Workflow Planning | **IN PROGRESS** | 현재 단계 |
| Application Design | **YES** | 새 서비스/컴포넌트 다수 |
| Units Generation | **YES** | 4개 이상 유닛 예상 |

### CONSTRUCTION PHASE — 실행 단계

| Stage | Execute | Reason |
|-------|---------|--------|
| Functional Design | **YES** | AI 파이프라인, 얼굴 인증 등 복잡한 비즈니스 로직 |
| NFR Requirements | SKIP | 보안 확장 opt-out, MVP 단계 |
| NFR Design | SKIP | 위와 동일 |
| Infrastructure Design | SKIP | 기술 스택 결정 완료 |
| Code Generation | **YES** | 핵심 — 실제 코드 생성 |
| Build and Test | **YES** | 필수 — 빌드 및 테스트 |

---

## Proposed Units of Work (예비)

실제 Units Generation에서 세분화되지만, 예상 유닛 구성:

| Unit | 설명 | 주요 기능 |
|------|------|-----------|
| **unit-auth** | 인증 및 본인 확인 | Cognito 연동, Face ID 등록/검증 |
| **unit-fitting** | AI 가상 피팅 | 이미지 업로드, 마스킹, 피팅 생성 (Mock) |
| **unit-background** | 배경 생성 | 텍스트/이미지 기반 배경 변경 (Mock) |
| **unit-recommend** | AI 추천 | 사이즈 조언, 날씨 코디 (Mock) |
| **unit-frontend** | 프론트엔드 UI | React 페이지, 컴포넌트, 라우팅 |

---

## Execution Order

```
INCEPTION:
  1. User Stories
  2. Application Design
  3. Units Generation

CONSTRUCTION (per-unit):
  4. Functional Design (per unit)
  5. Code Generation (per unit)
  6. Build and Test (all units)
```

---

## Risk Assessment

| Risk | Level | Mitigation |
|------|-------|------------|
| AI Mock → 실제 연동 전환 복잡도 | Medium | 추상화 레이어로 인터페이스 분리 |
| 이미지 임시 파일 관리 누수 | Low | TTL 기반 자동 삭제 + cron job |
| Rekognition 얼굴 인식 정확도 | Low | Phase 2에서 실제 테스트 |
| 동시 접속 100명 성능 목표 | Medium | Phase 2에서 부하 테스트 |

---

## Estimated Effort

| Phase | Estimated Time |
|-------|---------------|
| Inception (Stories + Design + Units) | ~1 session |
| Construction (Design + Code + Test) | ~2-3 sessions |
| **Total** | ~3-4 sessions |

---

## Approval Request

위 실행 계획을 검토해 주세요.

**실행 요약:**
- INCEPTION: User Stories → Application Design → Units Generation
- CONSTRUCTION: Functional Design → Code Generation → Build and Test
- **건너뛰는 단계**: Reverse Engineering, NFR Requirements, NFR Design, Infrastructure Design

승인 후 User Stories 단계로 진행합니다.
