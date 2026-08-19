# Supabase Cloud Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate Supabase (Managed PostgreSQL database via `asyncpg`, Supabase Cloud Auth with JWT validation, and Supabase Object Storage for workflow deliverables) with seamless dual-mode fallback to local SQLite and mock storage.

**Architecture:** Extended `ApplicationSettings` support Supabase connection strings, API keys, and JWT secrets. SQLAlchemy's async engine automatically parses PostgreSQL pooler connection strings with connection pre-ping. A FastAPI Supabase auth dependency validates cloud access tokens and provisions users, while a Supabase storage service manages artifact uploads and presigned download URLs. The frontend uses `@supabase/supabase-js` for authentication and token attachment.

**Tech Stack:** FastAPI, SQLAlchemy 2.0 (async), `asyncpg`, PyJWT, `supabase-py` / httpx, Next.js 15, `@supabase/supabase-js`, Vitest, Pytest.

**Spec:** [`docs/superpowers/specs/2026-08-15-supabase-integration-design.md`](file:///c:/Users/Samrat/OneDrive/Documents/Samrat-ai/TWIB_Copy/docs/superpowers/specs/2026-08-15-supabase-integration-design.md)

## Global Constraints

- Must maintain 100% backward compatibility and seamless local/offline fallback when Supabase keys are empty.
- All existing 99+ backend pytest cases and frontend vitest cases must continue passing.
- Follow Clean Architecture: Database in `backend/app/infrastructure/database`, auth in `backend/app/security`, storage in `backend/app/services/storage`, frontend client in `frontend/lib/supabase.ts`.

---

### Task 1: Backend Settings & Database Engine PostgreSQL/asyncpg Support

**Files:**
- Modify: `backend/app/core/settings.py`
- Modify: `backend/app/infrastructure/database/engine.py`
- Modify: `backend/.env.example`
- Create: `backend/tests/test_supabase_database.py`

**Interfaces:**
- Produces:
  - `ApplicationSettings.supabase_url: str`
  - `ApplicationSettings.supabase_anon_key: str`
  - `ApplicationSettings.supabase_service_role_key: str`
  - `ApplicationSettings.supabase_jwt_secret: str`
  - `create_engine(settings: ApplicationSettings)` supporting `postgresql+asyncpg`

- [ ] **Step 1: Install `asyncpg` in backend virtualenv**

Run:
```bash
cd backend
.\.venv\Scripts\pip install asyncpg
```

- [ ] **Step 2: Write test for PostgreSQL URL parsing and engine creation**

Write `backend/tests/test_supabase_database.py`:
```python
import pytest
from app.core.settings import ApplicationSettings
from app.infrastructure.database.engine import create_engine

def test_engine_handles_sqlite_fallback():
    settings = ApplicationSettings(database_url="sqlite+aiosqlite:///./test.db")
    engine = create_engine(settings)
    assert "sqlite" in str(engine.url)

def test_engine_normalizes_postgres_url():
    settings = ApplicationSettings(
        database_url="postgresql://postgres:secret@db.supabase.co:5432/postgres"
    )
    engine = create_engine(settings)
    assert engine.url.drivername == "postgresql+asyncpg"
```

- [ ] **Step 3: Update `settings.py` and `engine.py`**

Update `engine.py` to convert raw `postgres://` or `postgresql://` URLs to `postgresql+asyncpg://` and configure pool pre-ping.

- [ ] **Step 4: Run test to verify pass**

Run: `.\.venv\Scripts\pytest backend/tests/test_supabase_database.py`
Expected: PASS

- [ ] **Step 5: Commit changes**

```bash
git add backend/app/core/settings.py backend/app/infrastructure/database/engine.py backend/.env.example backend/tests/test_supabase_database.py
git commit -m "feat(database): add Supabase PostgreSQL and asyncpg connection support"
```

---

### Task 2: Supabase JWT Auth Verification & User Sync Service

**Files:**
- Create: `backend/app/security/supabase_auth.py`
- Modify: `backend/app/dependencies.py`
- Create: `backend/tests/test_supabase_auth.py`

**Interfaces:**
- Produces:
  - `verify_supabase_jwt(token: str, jwt_secret: str) -> dict`
  - `get_current_supabase_user(credentials: HTTPAuthorizationCredentials)` FastAPI dependency with local JWT fallback

- [ ] **Step 1: Write test for Supabase JWT verification**

Write `backend/tests/test_supabase_auth.py`:
```python
import pytest
import jwt
from app.security.supabase_auth import verify_supabase_jwt

def test_verify_valid_supabase_jwt():
    secret = "test-supabase-jwt-secret-key-32-chars-long"
    payload = {
        "sub": "usr_supabase_123",
        "email": "samrat@twib.ai",
        "role": "authenticated",
        "aud": "authenticated",
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    decoded = verify_supabase_jwt(token, secret)
    assert decoded["sub"] == "usr_supabase_123"
    assert decoded["email"] == "samrat@twib.ai"

def test_verify_invalid_jwt_raises():
    with pytest.raises(Exception):
        verify_supabase_jwt("invalid.token.here", "some-secret")
```

- [ ] **Step 2: Implement `supabase_auth.py` and update `dependencies.py`**

Implement secure JWT signature and claim verification with local fallback.

- [ ] **Step 3: Run auth tests**

Run: `.\.venv\Scripts\pytest backend/tests/test_supabase_auth.py`
Expected: PASS

- [ ] **Step 4: Commit changes**

```bash
git add backend/app/security/supabase_auth.py backend/app/dependencies.py backend/tests/test_supabase_auth.py
git commit -m "feat(auth): add Supabase JWT verification with dual-mode fallback"
```

---

### Task 3: Supabase Cloud Object Storage Service

**Files:**
- Create: `backend/app/services/storage/supabase_storage_service.py`
- Create: `backend/app/services/storage/__init__.py`
- Create: `backend/tests/test_supabase_storage.py`

**Interfaces:**
- Produces:
  - `SupabaseStorageService.upload_artifact(workflow_id: str, filename: str, content: bytes, content_type: str) -> str`
  - `SupabaseStorageService.get_download_url(file_path: str, expires_in: int) -> str`
  - `SupabaseStorageService.delete_artifact(file_path: str) -> bool`

- [ ] **Step 1: Write test for Supabase storage service & local fallback**

Write `backend/tests/test_supabase_storage.py`:
```python
import pytest
from app.services.storage.supabase_storage_service import SupabaseStorageService
from app.core.settings import ApplicationSettings

@pytest.mark.asyncio
async def test_storage_fallback_when_unconfigured():
    settings = ApplicationSettings(supabase_url="")
    storage = SupabaseStorageService(settings)
    
    url = await storage.upload_artifact(
        workflow_id="wf_test_123",
        filename="report.md",
        content=b"# Market Analysis\nContent here",
        content_type="text/markdown",
    )
    assert url.startswith("/storage/") or url.startswith("http")
```

- [ ] **Step 2: Implement `supabase_storage_service.py`**

Implement storage service with httpx REST API calls to Supabase Storage and local directory fallback.

- [ ] **Step 3: Run storage tests**

Run: `.\.venv\Scripts\pytest backend/tests/test_supabase_storage.py`
Expected: PASS

- [ ] **Step 4: Commit changes**

```bash
git add backend/app/services/storage/ backend/tests/test_supabase_storage.py
git commit -m "feat(storage): implement Supabase cloud object storage service"
```

---

### Task 4: Frontend Supabase Client SDK & Auth Provider

**Files:**
- Modify: `frontend/package.json`
- Create: `frontend/lib/supabase.ts`
- Create: `frontend/hooks/use-supabase-auth.ts`
- Modify: `frontend/lib/api-client.ts`
- Create: `frontend/tests/supabase-client.test.ts`

**Interfaces:**
- Produces:
  - `supabase` client instance from `@supabase/supabase-js`
  - `useSupabaseAuth()` hook
  - Auto-attaching bearer tokens in `api-client.ts`

- [ ] **Step 1: Install `@supabase/supabase-js` in frontend**

Run: `npm install @supabase/supabase-js`

- [ ] **Step 2: Implement `frontend/lib/supabase.ts` and `hooks/use-supabase-auth.ts`**

Configure client with `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`.

- [ ] **Step 3: Update `lib/api-client.ts` to attach Supabase session tokens**

- [ ] **Step 4: Run frontend tests and TypeScript verification**

Run:
```bash
npx vitest run
npx tsc --noEmit
```
Expected: PASS

- [ ] **Step 5: Commit changes**

```bash
git add frontend/package.json frontend/package-lock.json frontend/lib/supabase.ts frontend/hooks/use-supabase-auth.ts frontend/lib/api-client.ts
git commit -m "feat(frontend): add Supabase client SDK, auth hook, and token interceptor"
```

---

### Task 5: End-to-End Verification & Setup Guide

**Files:**
- Create: `docs/SUPABASE_SETUP.md`
- Modify: `backend/.env.example`
- Modify: `frontend/.env.example`

**Interfaces:**
- Produces complete setup instructions and `.env` template for connecting cloud projects.

- [ ] **Step 1: Create `docs/SUPABASE_SETUP.md`**

Step-by-step guide on obtaining Project URL, Database connection pooler string, Anon Key, and Service Role Key from the Supabase dashboard.

- [ ] **Step 2: Run full backend and frontend test suites**

Run:
```bash
cd backend && .\.venv\Scripts\pytest
cd ../frontend && npx vitest run && npm run build
```
Expected: All suites green.

- [ ] **Step 3: Commit documentation & final integration**

```bash
git add docs/SUPABASE_SETUP.md backend/.env.example frontend/.env.example
git commit -m "docs: add Supabase cloud configuration and setup guide"
```
