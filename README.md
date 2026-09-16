# Vynk — Ideas Meet Opportunities

Vynk is a modern professional networking and sponsorship platform connecting **Entrepreneurs** (idea owners, startup creators) and **Sponsors** (angels, corporate partners, funds, grantors) through a structured, verifiable lifecycle:

```
Discover → AI Match → Connect → Commit → Track → Complete → Build Trust
```

## Core Differentiators

1. **AI Matching**: Explainable compatibility recommendations linking founders and sponsors based on industry, stage, budget, and sponsorship preferences.
2. **Sponsorship Commitment Tracking**: Structured 7-stage commitment pipeline (`Interested → Discussion → Promised → Confirmed → Agreement → Funded → Completed`).
3. **Verifiable Trust Score**: Transparent 0-100 credibility metric derived from verified credentials, completed commitments, and responsiveness.

---

## Tech Stack

- **Frontend**: React, Vite, Modern Responsive Vanilla CSS Design System
- **Backend**: Python 3.13, FastAPI, Pydantic v2
- **Database**: SQLAlchemy 2.0 (PostgreSQL-ready with asyncpg; SQLite fallback with aiosqlite for local development)
- **Auth**: JWT tokens, bcrypt password hashing, role-based access control (Entrepreneur, Sponsor, Admin)
- **AI Service**: Pluggable AI service architecture ready for Google Gemini API integration

---

## Quickstart

### 1. Backend Setup

```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Unix:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Backend API documentation will be available at `http://localhost:8000/docs`.

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend application will be available at `http://localhost:5173`.
