# 💰 FinVault AI

> AI-powered personal finance and EMI manager: track income, expenses, budgets, and every detail of every loan in one place.

## Key Features
- Expense and income tracking with categories, filters, and 6-month trends
- Full loan records: lender, account number, rate, tenure, fees, prepayment penalty, contacts
- Amortization engine (reducing balance and flat rate) with principal/interest split
- One-click EMI recording, prepayment impact calculator, FOIR (debt-to-income)
- Upcoming-EMI and budget alerts
- AI advisor chat that sees your live financial data (OpenAI or Anthropic)

## Tech Stack
| Layer | Technology |
|---|---|
| Backend | FastAPI, SQLAlchemy 2 (async), Pydantic v2 |
| Database | PostgreSQL (SQLite for local dev), Redis |
| Auth | JWT (python-jose), bcrypt |
| AI | Anthropic Claude / OpenAI GPT |
| Frontend | React 18, TypeScript, Vite, Tailwind, Zustand, Recharts |
| Infra | Docker, Nginx, GitHub Actions |

## Folder Structure
See the project tree in the build guide (src/, api/, database/, ui/, config/, tests/, scripts/, infra/).

## Prerequisites
Python 3.11+, Node.js 20+, (optional) Docker Desktop.

## Installation
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then edit SECRET_KEY and an AI key
cd ui && npm install && cd ..
```

## Environment Variables
| Variable | Purpose | Default |
|---|---|---|
| DATABASE_URL | DB connection string | SQLite file |
| SECRET_KEY | JWT signing key (required in prod) | none |
| AI_PROVIDER | `anthropic` or `openai` | openai |
| ANTHROPIC_API_KEY / OPENAI_API_KEY | AI provider key | none |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token lifetime | 60 |
| DEBUG | Enables /docs | false |

## Run (development)
```bash
make seed       # optional demo data: demo@finvault.com / demo12345
make run        # API  → http://localhost:8000/docs
make run-ui     # UI   → http://localhost:5173
```

## Run (production / Docker)
```bash
make docker     # builds the UI, then Postgres + Redis + API + Nginx
```

## API Reference
| Method | Endpoint | Description |
|---|---|---|
| POST | /api/v1/auth/register, /login | Create account / get token |
| GET | /api/v1/auth/me | Profile |
| GET/POST | /api/v1/expenses | List / create expenses |
| GET/POST | /api/v1/incomes | List / create incomes |
| GET/POST | /api/v1/budgets | Budgets |
| GET/POST | /api/v1/loans | List / create loans |
| GET | /api/v1/loans/{id}/amortization | Full schedule + summary |
| POST | /api/v1/loans/{id}/pay-next | Record next EMI |
| POST | /api/v1/loans/{id}/prepayment-impact | Prepayment what-if |
| POST | /api/v1/loans/calculator/emi | Public EMI calculator |
| GET | /api/v1/dashboard/summary | Dashboard aggregate |
| POST | /api/v1/ai/chat | AI advisor |

## Evaluate / Test
```bash
make test
```

## Known Limitations
- No Alembic migrations yet (tables auto-created on startup)
- Floats used for money; migrate to `Numeric` before real-world use
- Alerts are computed on request; no email/SMS push yet
- No refresh tokens

## Future Improvements
- Alembic migrations, Redis caching for the dashboard
- Bank-statement PDF/CSV import with AI categorization
- Email/WhatsApp EMI reminders (Celery + Redis)
- Floating-rate loans, part-payment tenure vs. EMI options
- Mobile app (React Native) and multi-currency

## License
MIT