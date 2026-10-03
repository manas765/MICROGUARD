![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![Vercel](https://img.shields.io/badge/Frontend-Vercel-black?logo=vercel)
![Render](https://img.shields.io/badge/Backend-Render-46E3B7?logo=render&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikit-learn&logoColor=white)
![Groq](https://img.shields.io/badge/AI-Groq%20Llama%203.3-orange)

# MICROGUARD


An AI-powered end-to-end microfinance platform covering credit scoring, business cash-flow simulation, fraud detection, continuous loan monitoring, an AI financial assistant, and a tamper-evident audit trail.

Built as a full-stack portfolio project — React frontend, FastAPI backend, PostgreSQL database, deployed on Vercel + Render.

**Live app:** https://frontend-vibr.vercel.app/
**API docs:** https://microguard.onrender.com/docs

---

## Overview

MICROGUARD simulates a real microfinance lending platform for small business owners. Borrowers apply for loans and get an instant, explainable credit risk score; loan officers review and approve/reject applications with AI-assisted terms; approved loans are tracked through repayment with continuous risk monitoring; and the whole system includes fraud detection, privacy-conscious data handling, and a cryptographically verifiable audit log.

Every scoring/analysis component is built honestly for what the data supports — a real trained ML model where historical data exists (credit risk), and transparent rule-based logic where it doesn't (financial stress, loan health monitoring, cash-flow forecasting) rather than fabricating models with no real labels to train on.

---

## Tech stack

- **Frontend:** React (Vite), Tailwind CSS, Recharts, React Router — deployed on Vercel
- **Backend:** FastAPI, SQLAlchemy, Pydantic — deployed on Render
- **Database:** PostgreSQL
- **ML/Data:** scikit-learn (GradientBoostingClassifier), SHAP (explainability), Isolation Forest (anomaly detection), NetworkX (fraud graph clustering)
- **AI Assistant:** Groq API (Llama 3.3 70B)
- **Auth:** JWT + bcrypt

---

## Features by phase

### Phase 1 — Foundation
JWT authentication with role-based access (borrower / loan_officer / admin), business profile management, loan application and repayment schedule data model.

### Phase 2 — Credit scoring & financial stress
- **Credit risk scoring:** GradientBoostingClassifier trained on a public microfinance loan dataset (501 historical loans), with SHAP-based plain-language explanations for every prediction (e.g. "having a guarantor decreases risk").
- **Financial stress score:** rule-based (not ML — no historical label exists to validate a model against), comparing estimated repayment burden against declared income and business maturity.

### Phase 3 — Digital twin & cash-flow simulation
Deterministic month-by-month cash-flow forecasting (`/simulation/forecast`) using a business's real repayment schedule, income estimate, and configurable growth/shock/expense assumptions. Supports side-by-side scenario comparison (`/simulation/compare`).

### Phase 4 — Fraud detection
Three complementary layers, combined into advisory (not auto-reject) flags:
- **Rule-based checks:** rapid repeat applications, requested amount wildly inconsistent with income, guarantor already linked to a defaulted loan
- **Graph-based clustering (NetworkX):** flags applications sharing a signup IP or guarantor phone number — a classic signature of a fraud ring
- **Isolation Forest:** unsupervised anomaly detection against the live application pool (no fraud-labeled dataset exists, so no fraud *classifier* is claimed)

### Phase 5 — Continuous monitoring
Rule-based loan health tracking comparing predicted risk at origination against real repayment behavior — on_track / due_soon / overdue / paid_on_time / paid_late — with a dynamic risk score that adjusts based on actual payment history, and early-warning alerts for loan officers when a loan's real trajectory diverges from its original prediction.

### Phase 6 — AI financial assistant
A Groq-powered (Llama 3.3 70B) assistant that answers borrower and officer questions using their real data — risk score, stress score, fraud flags, loan health, and forecasts — formatted into plain-text context. No fabricated numbers; it only reasons over what's actually in the database.

### Phase 7 — Advanced features
- **Tamper-evident audit trail:** a hash-chained append-only log (`audit_log` table) recording key events — loan approvals/rejections, repayments, fraud flags. Each entry's hash incorporates the previous entry's hash, so any retroactive edit breaks the chain and is detectable via `/audit/verify`.
- **Privacy-preserving data handling:** sensitive identifiers (like guarantor phone numbers) are salted-hashed before being written into the audit log, and a borrower-facing `/privacy` page explains what's collected, what's stored raw vs. hashed, and who can see what.
- **Graph fraud detection refinement:** the shared-attribute fraud graph is exposed via `/fraud/graph` and visualized as an interactive force-directed graph on the officer dashboard, making fraud rings visually obvious rather than buried in a text flag.

---

## Project structure


---

## Running locally

**Backend:**
```bash
cd microguard
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
# set up a local PostgreSQL database and configure DATABASE_URL
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd microguard/frontend
npm install
npm run dev
```

Environment variables needed:
- Backend: `DATABASE_URL`, `GROQ_API_KEY`, `PYTHON_VERSION=3.11.9` (for deployment)
- Frontend: `VITE_API_URL` (points to the backend)

---

## API documentation

Full interactive API docs (Swagger UI) are available at `/docs` on the running backend — see the live link above.

---

## Notes on design philosophy

Every "AI" or "scoring" component in this project is built to match what the data actually supports:
- Credit risk scoring is a real trained classifier, because labeled historical outcome data exists.
- Financial stress, cash-flow forecasting, and loan health monitoring are deterministic rule-based logic — not fabricated ML models — because no historical label exists to validate a model against.
- Fraud detection combines transparent rules, graph clustering, and unsupervised anomaly detection — deliberately not a trained fraud *classifier*, since no fraud-labeled dataset exists.

This was a conscious choice to keep every claim in the system honest rather than impressive-sounding but unfounded.