# V-Suitcase — Component Dependency Map

## Frontend Dependencies

```
FC-07 LayoutModule
  |
  +-- FC-01 AuthModule (Cognito SDK)
  |     |
  |     +-- FC-02 FaceIDModule (WebRTC)
  |
  +-- FC-03 FittingModule
  |     |
  |     +-- FC-04 BackgroundModule
  |     |
  |     +-- FC-05 RecommendModule
  |
  +-- FC-06 ResultModule
```

## Backend Dependencies

```
BC-01 AuthService (Cognito)
  |
  +-- BC-02 FaceVerificationService (Rekognition)
  |
  +-- BC-06 FileManagerService (임시 파일)
        |
        +-- BC-03 FittingService (SAM + Stability AI)
        |
        +-- BC-04 BackgroundService (Stability AI)
        |
        +-- BC-05 RecommendService (Claude Opus 4.6 + Weather API)
        |
        +-- BC-07 ShareService (Pillow)
```

## Cross-Layer Dependencies

| Frontend | Backend | External |
|----------|---------|----------|
| FC-01 AuthModule | BC-01 AuthService | AWS Cognito |
| FC-02 FaceIDModule | BC-02 FaceVerificationService | AWS Rekognition |
| FC-03 FittingModule | BC-03 FittingService + BC-06 FileManager | Stability AI (Bedrock) |
| FC-04 BackgroundModule | BC-04 BackgroundService + BC-06 FileManager | Stability AI (Bedrock) |
| FC-05 RecommendModule | BC-05 RecommendService | Claude Opus 4.6, Weather API |
| FC-06 ResultModule | BC-06 FileManager + BC-07 ShareService | - |

## Build Order (의존성 순서)

1. **BC-01 AuthService** — 모든 API의 인증 기반
2. **BC-06 FileManagerService** — 이미지 처리 서비스들의 공통 의존
3. **BC-02 FaceVerificationService** — 피팅 전 필수
4. **BC-03 FittingService** — 핵심 기능
5. **BC-04 BackgroundService** — 피팅 이후 사용
6. **BC-05 RecommendService** — 피팅 결과 기반
7. **BC-07 ShareService** — 결과 이후 사용
8. **FC-07 LayoutModule** — 프론트엔드 기반
9. **FC-01 ~ FC-06** — 각 기능 모듈
