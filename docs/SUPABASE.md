# Vynk — $0 Supabase PostgreSQL Setup Guide

This guide describes how to create and connect a **100% Free Supabase PostgreSQL Database** for the Vynk platform.

---

## 1. Create a Free Supabase Project

1. Go to [database.new](https://database.new) or sign in at [supabase.com](https://supabase.com).
2. Click **New Project**.
3. Fill in the project details:
   - **Name**: `vynk-production`
   - **Database Password**: Choose a strong, secure password (save this securely).
   - **Region**: Choose the closest AWS region (e.g. `us-east-1`, `eu-central-1`, `ap-south-1`).
   - **Pricing Plan**: **Free Tier ($0/month)**.
4. Click **Create new project** and wait ~1-2 minutes for provisioning.

---

## 2. Obtain the Database Connection URI

1. In your Supabase project dashboard, navigate to **Project Settings** (gear icon) → **Database**.
2. Scroll to the **Connection string** section and select **URI**.
3. Choose the appropriate mode:
   - **Transaction Pooler (Port 6543)** *(Recommended for Vercel / Serverless deployments)*:
     ```text
     postgresql+asyncpg://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
     ```
   - **Direct Connection (Port 5432)** *(Recommended for initial Alembic migrations)*:
     ```text
     postgresql+asyncpg://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres
     ```

> [!NOTE]
> Ensure the driver prefix is `postgresql+asyncpg://` so SQLAlchemy uses the asyncpg driver.

---

## 3. Initialize the Database Schema

You have **two simple options** to apply the schema to your fresh Supabase PostgreSQL database:

### Option A: Via Supabase SQL Editor (Fastest, 1-Click)
1. In the Supabase dashboard, click **SQL Editor** in the left sidebar.
2. Click **New query**.
3. Copy the entire contents of [`backend/alembic/supabase_schema.sql`](file:///c:/Projects/vynk/backend/alembic/supabase_schema.sql) and paste them into the SQL editor.
4. Click **Run**.
5. All 19 tables, indexes, constraints, and the `alembic_version` baseline will be created instantly.

### Option B: Via Alembic CLI
From your local terminal, run:
```bash
cd backend
$env:DATABASE_URL="postgresql+asyncpg://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres"
.venv\Scripts\alembic -c alembic.ini upgrade head
```

---

## 4. Supabase Free Tier Best Practices for Vynk

| Setting | Recommended Value | Reason |
| :--- | :--- | :--- |
| `DB_POOL_SIZE` | `0` or `1` | Serverless functions scale elastically; `0` uses `NullPool` with Supavisor transaction pooler. |
| `DB_POOL_TIMEOUT` | `30` | Prevents hanging connections. |
| `pool_pre_ping` | `True` | Enabled automatically in Vynk to verify connection liveness. |
| `ENVIRONMENT` | `production` | Enables security headers, error masking, and strict secret validation. |
