# Vynk Production Deployment Guide

This step-by-step deployment guide describes how to deploy **Vynk** ("Ideas Meet Opportunities") across various production hosting topologies: Docker Compose, Container Platforms (Cloud Run / AWS ECS / Render), or Traditional Linux VPS.

---

## 1. Prerequisites

- Python 3.13+ runtime environment
- Node.js 20+ (for building frontend static bundle)
- PostgreSQL 15+ database instance
- Valid domain name with SSL/TLS certificate (HTTPS)

---

## 2. Standard Deployment Sequence

```mermaid
flowchart LR
    A["1. Provision PostgreSQL"] --> B["2. Configure Environment"]
    B --> C["3. Run Alembic Migrations"]
    C --> D["4. Start FastAPI Backend"]
    D --> E["5. Build React Frontend"]
    E --> F["6. Verify Health & Smoke Test"]
```

### Step 1: Provision Managed PostgreSQL
Provision a PostgreSQL database instance and retrieve the connection credentials. Ensure `pg_isready` reports available.

### Step 2: Configure Production Environment Variables
On your server or deployment platform, export the production environment variables:

```bash
export ENV=production
export PROJECT_NAME="Vynk API"
export SECRET_KEY="$(openssl rand -hex 32)"
export DATABASE_URL="postgresql+asyncpg://vynk_user:DB_PASSWORD@db.example.com:5432/vynk_db"
export BACKEND_CORS_ORIGINS='["https://vynk.example.com"]'
export GEMINI_API_KEY="optional_api_key"
```

### Step 3: Run Database Migrations
Execute Alembic migrations to construct the complete baseline schema:

```bash
cd backend
python -m pip install -r requirements.txt
alembic -c alembic.ini upgrade head
```

### Step 4: Start the Backend Production Server
Launch `uvicorn` using a production supervisor (systemd, gunicorn with uvicorn workers, or Docker):

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Step 5: Build and Deploy Frontend Static Assets
Configure the public API base URL and build the optimized production bundle:

```bash
cd frontend
export VITE_API_BASE_URL="https://api.vynk.example.com/api/v1"
npm ci
npm run build
```

Serve the generated `frontend/dist/` directory through a high-performance web server such as Nginx or Caddy with SPA fallback routing enabled.

---

## 3. Docker Container Deployment

If deploying with Docker and Docker Compose:

```bash
# 1. Clone repository and navigate to root
cd vynk

# 2. Configure production .env file
cp .env.example .env
# Edit .env with your real secret keys, domains, and database passwords

# 3. Build and launch containers
docker compose up -d --build

# 4. Apply database migrations inside the backend container
docker compose exec backend alembic -c alembic.ini upgrade head

# 5. Verify service health
curl -f http://localhost:8000/api/v1/health
```

---

## 4. Reverse Proxy & HTTPS Configuration (Nginx Example)

```nginx
# API Backend Proxy
server {
    listen 443 ssl http2;
    server_name api.vynk.example.com;

    ssl_certificate /etc/letsencrypt/live/vynk.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/vynk.example.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}

# Frontend Static SPA
server {
    listen 443 ssl http2;
    server_name vynk.example.com;

    ssl_certificate /etc/letsencrypt/live/vynk.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/vynk.example.com/privkey.pem;

    root /var/www/vynk/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

---

## 5. Post-Deployment Verification Checklist

1. [ ] `GET /api/v1/health` returns `200 OK` with database status `healthy`.
2. [ ] User registration, login, and JWT issuance succeed.
3. [ ] Role dashboards load properly for Entrepreneur, Sponsor, and Admin.
4. [ ] In-app notification polling and secure messaging function without errors.
5. [ ] Project showcase discovery feed renders published startups.
6. [ ] Deterministic Trust Score calculations remain accurate.
