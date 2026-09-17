# Vynk Production Architecture & Operations Guide

This document outlines the production configuration, security practices, database administration, backup procedures, and operational checklists for the **Vynk** platform ("Ideas Meet Opportunities").

---

## 1. Environment Configuration

### Required Production Environment Variables

| Variable | Description | Production Requirement | Example |
| :--- | :--- | :--- | :--- |
| `ENV` / `ENVIRONMENT` | Application running mode | Must be set to `production` | `production` |
| `SECRET_KEY` | Symmetric key for signing JWT tokens | Strong random secret $\ge 32$ chars. **Insecure defaults are rejected on startup.** | Generate via `openssl rand -hex 32` |
| `DATABASE_URL` | Async PostgreSQL database connection URI | Must use `postgresql+asyncpg` driver. **SQLite is strictly blocked in production.** | `postgresql+asyncpg://vynk_user:PASSWORD@host:5432/vynk_db` |
| `BACKEND_CORS_ORIGINS` | Permitted browser origins | JSON array of explicit domains. **Wildcard `*` is blocked in production.** | `["https://vynk.io", "https://app.vynk.io"]` |
| `GEMINI_API_KEY` | Google Gemini API key for AI matching | Optional. If omitted, Vynk automatically uses deterministic compatibility scoring. | `AIzaSy...` |
| `DEBUG` | FastAPI debugging & documentation | Must be `false` in production. | `false` |

---

## 2. PostgreSQL Database Setup & Pooling

### Provisioning
Create a dedicated PostgreSQL user and database with standard UTF-8 encoding:

```sql
CREATE USER vynk_user WITH PASSWORD 'your_strong_random_password';
CREATE DATABASE vynk_db OWNER vynk_user ENCODING 'UTF8';
GRANT ALL PRIVILEGES ON DATABASE vynk_db TO vynk_user;
```

### Connection Pool Configuration
In production mode with PostgreSQL, Vynk configures SQLAlchemy's async connection pool:
- `DB_POOL_SIZE`: Default `10` persistent connections.
- `DB_MAX_OVERFLOW`: Default `20` burst connections.
- `DB_POOL_TIMEOUT`: Default `30` seconds before timeout on exhausted pool.
- `DB_POOL_RECYCLE`: Default `3600` seconds (1 hour) to avoid stale socket connections.
- `pool_pre_ping=True`: Proactively tests connection liveness before executing queries.

---

## 3. Database Migration Strategy (Alembic)

Vynk uses **Alembic** for schema migrations in PostgreSQL production environments.

### Applying Migrations
Run Alembic migrations against the production database:

```bash
cd backend
alembic -c alembic.ini upgrade head
```

### Checking Migration Status
```bash
alembic -c alembic.ini current
alembic -c alembic.ini heads
```

### Rollback Guidance
```bash
alembic -c alembic.ini downgrade -1
```

> [!NOTE]
> Local development and unit tests continue supporting SQLite (`sqlite+aiosqlite:///./vynk.db`) with automatic table synchronization. Production deployments must execute migration-driven schema updates via Alembic.

---

## 4. Administrator Account Provisioning

To prevent unauthorized access, **no default admin account or predictable password exists in production source code**.

### Procedure for Creating the First Production Administrator
1. Ensure `SECRET_KEY` and `DATABASE_URL` are configured in your production environment.
2. Run the secure interactive admin creation CLI script or execute an authorized registration call through the API with a strong, unique password:

```bash
# Example via authenticated API call or administrative script
curl -X POST https://api.vynk.io/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "governance@vynk.io",
    "password": "<STRONG_RANDOM_PASSWORD>",
    "full_name": "Governance Administrator",
    "role": "admin"
  }'
```

3. Store administrative credentials in a secure company password manager.

---

## 5. Security & Privacy Hardening

1. **Security Headers**: Injected automatically on all HTTP responses:
   - `X-Content-Type-Options: nosniff`
   - `X-Frame-Options: DENY`
   - `Referrer-Policy: strict-origin-when-cross-origin`
   - `X-XSS-Protection: 1; mode=block`
   - `Strict-Transport-Security: max-age=31536000; includeSubDomains` (enabled when served over HTTPS in production).
2. **Safe Error Handling**: The global exception handler masks raw database errors, internal filepaths, and stack traces when `ENV=production`.
3. **No Secret Leakage**: `SECRET_KEY`, database credentials, and `GEMINI_API_KEY` are strictly server-side environment variables and are never bundled into frontend static JavaScript assets.
4. **Immutable Audit Trail**: All administrative moderation actions (user verification, suspension, project approval/rejection, report resolution, dispute arbitration) record the authenticated `admin_id`, action type, entity ID, and UTC timestamp in `admin_audit_logs`.

---

## 6. Backup & Disaster Recovery

### Automated Database Backup (Daily Recommended)
```bash
# Backup PostgreSQL database to a timestamped compressed archive
pg_dump -U vynk_user -h <db-host> -d vynk_db -F c -b -v -f "/backups/vynk_db_$(date +%Y%m%d_%H%M%S).dump"
```

### Database Restore Procedure
```bash
# In the event of disaster recovery:
pg_restore -U vynk_user -h <db-host> -d vynk_db -v "/backups/vynk_db_YYYYMMDD_HHMMSS.dump"
```

---

## 7. Health Monitoring

Vynk provides an authenticated-safe health endpoint:

```http
GET /api/v1/health
```

**Expected Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "Vynk API",
  "version": "1.0.0",
  "environment": "production",
  "database": {
    "status": "healthy",
    "dialect": "postgresql",
    "latency_ms": 1.45,
    "error": null
  }
}
```
*Note: In production mode, database connection errors are sanitized to prevent credential exposure.*
