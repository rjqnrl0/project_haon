# Build Instructions — V-Suitcase

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Docker & Docker Compose | 24+ | PostgreSQL, LocalStack |
| Python | 3.11+ | Backend runtime |
| Node.js | 20+ | Frontend build |
| npm | 10+ | Package management |
| AWS CLI v2 | 2.x | LocalStack S3 bucket creation |

## 1. Infrastructure Setup

```bash
# Start PostgreSQL and LocalStack
docker compose up -d

# Verify services are running
docker compose ps
# Expected: db (healthy), localstack (healthy)
```

### Create S3 Bucket in LocalStack

```bash
aws --endpoint-url=http://localhost:4566 s3 mb s3://v-suitcase-temp-local --region ap-northeast-2
```

## 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate
# Activate (Unix)
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env: set OPENWEATHERMAP_API_KEY if weather feature needed
```

### Database Migration

```bash
# Generate initial migration
alembic revision --autogenerate -m "initial"

# Apply migrations
alembic upgrade head
```

### Start Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify**: `GET http://localhost:8000/health` should return `{"status": "ok"}`

## 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Verify**: Open `http://localhost:5173` — should show login page.

### Production Build

```bash
npm run build
# Output: frontend/dist/
```

## 4. Environment Configuration

### Local Development (.env)

```
ENV=local
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vsuitcase
DB_USERNAME=postgres
DB_PASSWORD=postgres
COGNITO_POOL_ID=              # Leave empty for local dev (skips JWT verify)
COGNITO_CLIENT_ID=
COGNITO_CLIENT_SECRET=
COGNITO_REGION=ap-northeast-2
S3_TEMP_BUCKET=v-suitcase-temp-local
S3_REGION=ap-northeast-2
FILE_EXPIRY_HOURS=1
SHARE_EXPIRY_HOURS=720
CORS_ORIGINS=http://localhost:5173
OPENWEATHERMAP_API_KEY=       # Required for weather recommendation
UNSPLASH_ACCESS_KEY=          # Required for background search
```

### Local Dev Auth Bypass

When `ENV=local`, the backend skips Cognito JWT verification and uses a mock user. This enables end-to-end testing without AWS Cognito setup.

## 5. Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `connection refused :5432` | PostgreSQL not running | `docker compose up -d db` |
| `connection refused :4566` | LocalStack not running | `docker compose up -d localstack` |
| `NoSuchBucket` | S3 bucket not created | Run `aws --endpoint-url=... s3 mb ...` command |
| Alembic import error | Models not imported | Verify `migrations/env.py` imports all models |
| CORS error in browser | Origin mismatch | Check `CORS_ORIGINS` in `.env` |
| Frontend proxy 502 | Backend not running | Start uvicorn on port 8000 |
| `ModuleNotFoundError` | venv not activated | Activate virtual environment |
