# Vynk Frontend Vercel Deployment Guide

This guide provides step-by-step instructions for deploying the **Vynk** React/Vite frontend to **Vercel** and connecting it to your FastAPI backend API.

---

## 1. Architecture Overview

```text
┌───────────────────────────────────────┐
│           Vynk React App              │
│       Hosted on Vercel (SPA)          │
│   (e.g., https://vynk.vercel.app)     │
└──────────────────┬────────────────────┘
                   │
                   │ HTTPS API Requests
                   │ (Bearer JWT Auth)
                   ▼
┌───────────────────────────────────────┐
│          Vynk FastAPI Backend         │
│   Public Host (Render / Fly / VPS)    │
│   (e.g., https://api.yourdomain.com)  │
└──────────────────┬────────────────────┘
                   │
                   │ SQLAlchemy asyncpg
                   ▼
┌───────────────────────────────────────┐
│          PostgreSQL Database          │
└───────────────────────────────────────┘
```

---

## 2. Prerequisites

1. A [Vercel](https://vercel.com) account.
2. A GitHub repository containing the Vynk project.
3. A deployed or accessible FastAPI backend URL (e.g., `https://api.yourdomain.com/api/v1`).

---

## 3. Step-by-Step Vercel Deployment

### Step 1: Push Project to GitHub
Ensure all code and configurations are committed and pushed to your GitHub repository:
```bash
git add .
git commit -m "Prepare Vynk frontend for Vercel deployment"
git push origin master
```

### Step 2: Import Project in Vercel Dashboard
1. Log in to [Vercel Dashboard](https://vercel.com/dashboard).
2. Click **Add New...** → **Project**.
3. Select and import your GitHub repository (`vynk`).

### Step 3: Configure Project Settings
In the Vercel project configuration screen:
- **Project Name**: `vynk` (or custom name)
- **Framework Preset**: `Vite`
- **Root Directory**: Click `Edit` and select `frontend`
- **Build Command**: `npm run build` (default)
- **Output Directory**: `dist` (default)
- **Install Command**: `npm install` (default)

### Step 4: Configure Environment Variables
In the **Environment Variables** section, add:
- **Key**: `VITE_API_BASE_URL`
- **Value**: `https://YOUR-BACKEND-DOMAIN/api/v1` (e.g. `https://api.vynk.io/api/v1`)

> [!IMPORTANT]
> **Zero Backend Secrets on Vercel:** Only public frontend variables starting with `VITE_` are configured on Vercel. Never add `SECRET_KEY`, `DATABASE_URL`, or `GEMINI_API_KEY` to Vercel environment variables.

### Step 5: Deploy
Click **Deploy**. Vercel will install dependencies, execute `npm run build`, and deploy your SPA to a `.vercel.app` domain.

---

## 4. SPA Fallback Routing

Client-side routing (React Router v7) is managed via `frontend/vercel.json`:

```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

This ensures direct URL navigation and page refreshes on paths like `/login`, `/dashboard`, `/projects`, `/messages`, and `/admin/*` serve the SPA without 404 errors.

---

## 5. Configure Backend CORS

Once your Vercel deployment is live, update your backend's `BACKEND_CORS_ORIGINS` environment variable on your backend hosting provider:

```bash
BACKEND_CORS_ORIGINS=["https://YOUR-VYNK.vercel.app","https://vynk.io"]
```

> [!CAUTION]
> Production FastAPI strictly rejects wildcard `BACKEND_CORS_ORIGINS=["*"]` when credentials (Authorization Bearer headers) are used. Always specify the exact HTTPS Vercel domain.

---

## 6. Post-Deployment Verification Checklist

1. [ ] **Homepage**: Visit `https://YOUR-VYNK.vercel.app` and check console for clean loading.
2. [ ] **Direct Navigation**: Refresh on `https://YOUR-VYNK.vercel.app/login` and `https://YOUR-VYNK.vercel.app/projects` to ensure 200 OK without 404s.
3. [ ] **Authentication**: Register a test user and log in. Verify JWT is stored and `/auth/me` returns 200.
4. [ ] **Showcase Discovery**: Browse projects and sponsors; verify API communication.
5. [ ] **Admin Security**: Access `/admin` with a standard user and verify 403 / redirect protection.
