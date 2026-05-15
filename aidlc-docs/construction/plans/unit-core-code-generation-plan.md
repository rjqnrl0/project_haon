# Code Generation Plan — unit-core

## Unit Context
- **Unit**: unit-core
- **Purpose**: 프로젝트 기반 구조, 설정, DB 마이그레이션, 공통 유틸리티
- **Stack**: FastAPI (Backend) + React/Vite (Frontend) + PostgreSQL + S3
- **Structure**: Greenfield, single monorepo (`backend/` + `frontend/`)

## Stories Implemented
- 인프라 기반 (모든 스토리의 전제조건)

## Dependencies
- 없음 (기반 유닛, 다른 모든 유닛이 이 유닛에 의존)

---

## Code Generation Steps

### Backend (FastAPI)

- [x] Step 1: Project structure setup — `backend/` 디렉토리, pyproject.toml, requirements.txt
- [x] Step 2: FastAPI app entry point — `backend/app/main.py` (앱 초기화, 미들웨어, 라우터 등록)
- [x] Step 3: Configuration module — `backend/app/core/config.py` (Pydantic Settings, .env 로딩)
- [x] Step 4: Database setup — `backend/app/core/database.py` (SQLAlchemy async engine, session dependency)
- [x] Step 5: Alembic migration setup — `backend/migrations/` (env.py, initial migrations)
- [x] Step 6: DB models (shared) — `backend/app/models/` (User, FittingTask, ShareLink, WeatherRequest, SizeRecommendation)
- [x] Step 7: FileManagerService — `backend/app/services/file_manager.py` (S3 upload/download/cleanup)
- [x] Step 8: Error handling — `backend/app/core/errors.py` (AppError hierarchy + exception handlers)
- [x] Step 9: Middleware — `backend/app/core/middleware.py` (CORS, logging, error handler)
- [x] Step 10: Health check endpoint — `backend/app/api/health.py`
- [x] Step 11: Background tasks — `backend/app/core/scheduler.py` (periodic cleanup)
- [x] Step 12: `.env.example` + Docker Compose for local dev

### Frontend (React/Vite)

- [x] Step 13: Project structure setup — `frontend/` (Vite + React + TypeScript + Tailwind)
- [x] Step 14: Routing setup — `frontend/src/router/` (React Router v6, route definitions)
- [x] Step 15: Layout components — `frontend/src/layouts/` (PublicLayout, AuthLayout)
- [x] Step 16: Route Guards — `frontend/src/components/guards/` (AuthGuard, FaceIDGuard)
- [x] Step 17: Global state (Zustand) — `frontend/src/stores/` (authStore, uiStore)
- [x] Step 18: Axios configuration — `frontend/src/lib/api.ts` (interceptors, base URL)
- [x] Step 19: Common UI components — `frontend/src/components/common/` (LoadingSpinner, Toast, FileUpload, etc.)
- [x] Step 20: Types & constants — `frontend/src/types/`, `frontend/src/constants/`

### Documentation

- [x] Step 21: Code generation summary — `aidlc-docs/construction/unit-core/code/code-summary.md`

---

## File Structure Preview

```
backend/
  pyproject.toml
  requirements.txt
  .env.example
  app/
    __init__.py
    main.py
    core/
      __init__.py
      config.py
      database.py
      errors.py
      middleware.py
      scheduler.py
    models/
      __init__.py
      base.py
      user.py
      fitting_task.py
      share_link.py
      weather_request.py
      size_recommendation.py
    services/
      __init__.py
      file_manager.py
    api/
      __init__.py
      health.py
  migrations/
    env.py
    versions/
      001_create_users.py
      002_create_fitting_tasks.py
      003_create_share_links.py
      004_create_weather_requests.py
      005_create_size_recommendations.py

frontend/
  package.json
  vite.config.ts
  tsconfig.json
  tailwind.config.js
  postcss.config.js
  index.html
  src/
    main.tsx
    App.tsx
    router/
      index.tsx
      routes.tsx
    layouts/
      PublicLayout.tsx
      AuthLayout.tsx
    components/
      guards/
        AuthGuard.tsx
        FaceIDGuard.tsx
      common/
        LoadingSpinner.tsx
        Toast.tsx
        FileUpload.tsx
        ImagePreview.tsx
        ConfirmDialog.tsx
        ErrorBoundary.tsx
    stores/
      authStore.ts
      uiStore.ts
    lib/
      api.ts
    types/
      index.ts
    constants/
      index.ts

docker-compose.yml
```
