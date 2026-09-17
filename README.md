# Vynk — Ideas Meet Opportunities

Vynk is a modern, enterprise-grade professional networking and sponsorship platform connecting **Entrepreneurs** (idea owners, startup creators) and **Sponsors** (angels, corporate partners, funds, grantors) through a structured, auditable lifecycle:

```
Discover → AI Match → Connect → Commit → Track → Complete → Build Trust
```

---

## Core Pillars & Differentiators

1. **AI Compatibility Matching**: Explainable, deterministic compatibility scoring with optional Google Gemini GenAI enrichment linking founders and sponsors based on industry, stage, budget, and strategic goals.
2. **Sponsorship Commitment Tracking**: Verifiable 7-stage commitment pipeline (`Interested → Discussion → Promised → Confirmed → Agreement → Funded → Completed`) with milestone proof references and audit events.
3. **Deterministic Trust Score & Reputation**: Deterministic, game-resistant 0–100 credibility rating computed algorithmically across 4 verifiable pillars: Platform Verification, Commitment Track Record, Milestone Delivery, and Responsiveness.
4. **Relationship-Gated Secure Messaging**: Strict relationship validation ensuring communications occur only between connected counter-parties or active request participants.
5. **Governance & Moderation**: Comprehensive platform administration, project showcase review queues, dispute arbitration, and immutable audit logs.

---

## Technical Architecture

- **Frontend**: React 19, Vite, React Router v7, Vanilla CSS Design System with dark mode tokens & responsive glassmorphic cards.
- **Backend**: Python 3.13, FastAPI, Pydantic v2, Async SQLAlchemy 2.0.
- **Database Support**: Dual-dialect architecture:
  - **Production**: PostgreSQL 15+ using `asyncpg` with connection pooling.
  - **Development/Testing**: SQLite using `aiosqlite` with zero-config setup.
- **Database Migrations**: Alembic async migrations for PostgreSQL production environments.
- **Security & Auth**: Signed JWT tokens (HS256), bcrypt password hashing, role-based access control (`entrepreneur`, `sponsor`, `admin`), security headers middleware.

---

## Local Development Quickstart

### 1. Backend Setup

```bash
cd backend
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env

# Start FastAPI development server
uvicorn app.main:app --reload --port 8000
```

- API Docs: `http://localhost:8000/api/v1/docs`
- Health Check: `http://localhost:8000/api/v1/health`

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

- Frontend Application: `http://localhost:5173`

---

## Running Automated Tests

Run the complete backend test suite:

```bash
cd backend
pytest -v
```

Execute the live end-to-end verification suites (Phases 1 through 9):

```bash
python verify_live.py
python verify_phase2.py
python verify_phase3.py
python verify_phase4.py
python verify_phase5.py
python verify_phase6.py
python verify_phase7.py
python verify_phase8.py
python verify_phase9.py
```

Build the production frontend bundle:

```bash
cd frontend
npm run build
```

---

## Production Deployment & Operations

For complete production guides, see:
- [Production Operations & Security Guide](docs/PRODUCTION.md)
- [Step-by-Step Deployment Guide](docs/DEPLOYMENT.md)
