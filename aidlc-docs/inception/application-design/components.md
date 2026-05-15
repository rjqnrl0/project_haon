# V-Suitcase — Component Definitions

## Frontend Components (React)

### FC-01: AuthModule
| 항목 | 내용 |
|------|------|
| **책임** | 회원가입, 로그인, 로그아웃, 토큰 관리 |
| **Stories** | US-01, US-02 |
| **외부 의존** | AWS Cognito SDK |

### FC-02: FaceIDModule
| 항목 | 내용 |
|------|------|
| **책임** | 셀피 촬영 UI, 웹캠 접근, Face ID 등록 플로우 |
| **Stories** | US-03, US-04 |
| **외부 의존** | WebRTC (카메라 접근), Backend API |

### FC-03: FittingModule
| 항목 | 내용 |
|------|------|
| **책임** | 전신 사진 업로드, 의류 이미지 업로드, 피팅 결과 표시 |
| **Stories** | US-05, US-06, US-07 |
| **외부 의존** | Backend API |

### FC-04: BackgroundModule
| 항목 | 내용 |
|------|------|
| **책임** | 텍스트 프롬프트 입력, 배경 이미지 업로드, 배경 합성 결과 표시 |
| **Stories** | US-08, US-09 |
| **외부 의존** | Backend API |

### FC-05: RecommendModule
| 항목 | 내용 |
|------|------|
| **책임** | 사이즈 추천 표시, 날씨 코디 추천 표시, 여행지 입력 |
| **Stories** | US-10, US-11 |
| **외부 의존** | Backend API |

### FC-06: ResultModule
| 항목 | 내용 |
|------|------|
| **책임** | 결과 이미지 다운로드, SNS 공유 (워터마크 삽입) |
| **Stories** | US-12, US-13 |
| **외부 의존** | Backend API, Web Share API |

### FC-07: LayoutModule
| 항목 | 내용 |
|------|------|
| **책임** | 공통 레이아웃, 네비게이션, 라우팅, 반응형 디자인 |
| **Stories** | 전체 |
| **외부 의존** | React Router |

---

## Backend Components (FastAPI)

### BC-01: AuthService
| 항목 | 내용 |
|------|------|
| **책임** | Cognito 토큰 검증, 사용자 세션 관리 |
| **Stories** | US-01, US-02 |
| **외부 의존** | AWS Cognito |

### BC-02: FaceVerificationService
| 항목 | 내용 |
|------|------|
| **책임** | 기준 얼굴 등록, 얼굴 비교 검증 |
| **Stories** | US-03, US-04 |
| **외부 의존** | AWS Rekognition (Phase 2), Mock (Phase 1) |

### BC-03: FittingService
| 항목 | 내용 |
|------|------|
| **책임** | 이미지 수신, 마스킹 처리, 피팅 이미지 생성 |
| **Stories** | US-05, US-06, US-07 |
| **외부 의존** | SAM + Stability AI via Bedrock (Phase 2), Mock (Phase 1) |

### BC-04: BackgroundService
| 항목 | 내용 |
|------|------|
| **책임** | 프롬프트/이미지 기반 배경 생성 및 합성 |
| **Stories** | US-08, US-09 |
| **외부 의존** | Stability AI via Bedrock (Phase 2), Mock (Phase 1) |

### BC-05: RecommendService
| 항목 | 내용 |
|------|------|
| **책임** | 체형 분석 사이즈 추천, 날씨 API 연동 코디 추천 |
| **Stories** | US-10, US-11 |
| **외부 의존** | Claude Opus 4.6 via Bedrock (Phase 2), Weather API, Mock (Phase 1) |

### BC-06: FileManagerService
| 항목 | 내용 |
|------|------|
| **책임** | 임시 파일 저장/삭제, TTL 관리, 다운로드 URL 생성 |
| **Stories** | US-05, US-06, US-12 |
| **외부 의존** | 로컬 파일 시스템 (임시 디렉토리) |

### BC-07: ShareService
| 항목 | 내용 |
|------|------|
| **책임** | 워터마크 삽입, 임시 공유 URL 생성 |
| **Stories** | US-13 |
| **외부 의존** | Pillow (이미지 처리) |
