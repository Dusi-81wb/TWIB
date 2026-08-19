# Supabase Cloud Integration Specification (Database, Auth, Storage)

- **Date**: 2026-08-15
- **Status**: Approved
- **Topic**: Cloud Supabase Integration (PostgreSQL, Supabase Auth, Object Storage) with Dual-Mode Local Fallback

---

## 1. Overview & Objectives

This specification defines the integration of Supabase into the TWIB (Total Workflow Intelligence Builder) platform across three core pillars:
1. **Managed PostgreSQL**: High-performance database layer using async SQLAlchemy and `asyncpg` with PgBouncer connection pooling.
2. **Supabase Cloud Authentication**: Seamless user authentication supporting Email/Password and OAuth (Google, GitHub) on Next.js 15, with FastAPI JWT claim verification and user auto-provisioning.
3. **Supabase Object Storage**: Cloud artifact storage bucket (`workflow-artifacts`) for archiving generated reports, JSON workflow plans, and deliverable files with secure presigned URLs.
4. **Dual-Mode Fallback**: Automated fallback to local SQLite and local mock storage when running offline, in test suites, or when Supabase keys are not set.

---

## 2. Architecture & Configuration

### 2.1 Backend Environment Configuration (`backend/app/core/settings.py`)

New settings attributes:
```python
# Supabase Configuration
supabase_url: str = ""
supabase_anon_key: str = ""
supabase_service_role_key: str = ""
supabase_jwt_secret: str = ""
supabase_storage_bucket: str = "workflow-artifacts"
```

### 2.2 Database Engine Enhancement (`backend/app/infrastructure/database/engine.py`)

- Converts PostgreSQL connection strings (`postgres://` / `postgresql://`) to `postgresql+asyncpg://`.
- Configures connection pooling parameters:
  - `pool_size = 10`
  - `max_overflow = 20`
  - `pool_pre_ping = True` (detects and replaces dropped or stale cloud connections).
- Falls back to `sqlite+aiosqlite` with `StaticPool` if `database_url` is empty or begins with `sqlite`.

---

## 3. Authentication Architecture

### 3.1 Frontend (`frontend/lib/supabase.ts`)
- Client singleton: `@supabase/supabase-js` configured with `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`.
- Auth Provider / Hook: `useSupabaseAuth()` exposing:
  - `user`, `session`, `isLoading`
  - `signUp(email, password)`
  - `signInWithPassword(email, password)`
  - `signInWithOAuth(provider: 'google' | 'github')`
  - `signOut()`
- Axios Interceptor: Injects active `Authorization: Bearer <supabase_access_token>` on all outbound API requests to FastAPI.

### 3.2 Backend Token Verification (`backend/app/security/supabase_auth.py`)
- Middleware / Dependency: `get_current_supabase_user(token: str) -> AuthenticatedUser`
- Verifies JWT signature against `SUPABASE_JWT_SECRET` (or Supabase public keys).
- Decodes standard claims (`sub` as Supabase user ID, `email`, `role`, `app_metadata`).
- Syncs user record into the local/PostgreSQL `users` table upon first login.
- Falls back to local JWT verification when in local development mode.

---

## 4. Cloud Object Storage (`backend/app/services/storage/`)

### 4.1 Storage Service Interface
```python
class SupabaseStorageService:
    async def upload_artifact(self, workflow_id: str, filename: str, content: bytes, content_type: str) -> str:
        ...
    async def get_download_url(self, file_path: str, expires_in: int = 3600) -> str:
        ...
    async def delete_artifact(self, file_path: str) -> bool:
        ...
```

- Target Bucket: `workflow-artifacts` (automatically created if not present).
- Presigned URLs: Generates time-bounded signed URLs for secure download from the frontend result viewer.
- Fallback: Saves files locally to `backend/storage/artifacts/` if Supabase storage is unconfigured.

---

## 5. Verification & Testing Strategy

1. **Unit & Integration Tests**:
   - `test_supabase_auth.py`: Tests valid Supabase JWT decoding, expired token rejection, and fallback to local JWT.
   - `test_supabase_storage.py`: Tests upload, presigned URL generation, and fallback behavior.
   - `test_database_engine.py`: Tests `asyncpg` URL parsing and pooling configuration.
2. **Frontend Type & Build Verification**:
   - `npx tsc --noEmit` on `frontend/`.
   - `npm run build` production compilation.
3. **Backend Test Suite**:
   - Pytest execution ensuring all tests continue passing with dual-mode fallback.
