# Supabase Cloud Setup & Configuration Guide for TWIB

This guide walks you through connecting your **Supabase** project to TWIB for hosted PostgreSQL, Cloud Authentication, and Object Storage.

---

## 1. Obtain Your Supabase Credentials

From your [Supabase Dashboard](https://supabase.com/dashboard/projects):

1. **Project URL & API Keys**:
   - Go to **Project Settings** → **API**.
   - Copy **Project URL** (e.g. `https://xyzproject.supabase.co`).
   - Copy **Project API keys** → `anon` `public` key.
   - Copy **Project API keys** → `service_role` `secret` key.
2. **JWT Secret**:
   - In **Project Settings** → **API**, scroll to **JWT Settings**.
   - Copy the **JWT Secret**.
3. **Database Connection Pooler String**:
   - Go to **Project Settings** → **Database** → **Connection Pooling**.
   - Select **Mode: Transaction** and **Port: 6543**.
   - Copy the URI:
     ```text
     postgresql://postgres.[YOUR-PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
     ```

---

## 2. Configure Storage Bucket

1. Go to **Storage** in your Supabase Dashboard sidebar.
2. Click **New Bucket**.
3. Set **Bucket Name**: `workflow-artifacts`.
4. Set **Public Bucket**: Enabled (or configure signed URL policies).
5. Click **Save**.

---

## 3. Configure Backend Environment (`backend/.env`)

Add or update the following values in your `backend/.env` file:

```env
# Supabase PostgreSQL Connection Pooler
DATABASE_URL=postgresql+asyncpg://postgres.your-project-ref:your-db-password@aws-0-region.pooler.supabase.com:6543/postgres

# Supabase API & Security Credentials
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
SUPABASE_JWT_SECRET=your-supabase-jwt-secret
SUPABASE_STORAGE_BUCKET=workflow-artifacts
```

---

## 4. Configure Frontend Environment (`frontend/.env.local`)

Add the following values in your `frontend/.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_SUPABASE_URL=https://your-project-ref.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
```

---

## 5. Verify Full-Stack Connectivity

1. **Start Backend**:
   ```powershell
   cd backend
   .\.venv\Scripts\uvicorn app.main:app --reload --port 8000
   ```
   FastAPI will automatically initialize the database schema on Supabase PostgreSQL.

2. **Start Frontend**:
   ```powershell
   cd frontend
   npm run dev
   ```

3. **Verify Dual-Mode Fallback**:
   If any Supabase environment variable is omitted or empty, TWIB will automatically and safely fall back to local SQLite (`twib.db`) and local disk storage without failing.
