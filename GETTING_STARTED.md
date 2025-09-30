# Getting Started - Spend Analyzer for Google Workspace

## Project Overview
A Google Workspace add-on that scans Gmail for invoices/receipts and identifies duplicate charges, unnecessary subscriptions, and price increases. Users save money by finding waste in their business expenses.

## Current Status
✅ **Completed:**
- Initial project structure created
- Next.js 14 frontend with Tailwind CSS + shadcn/ui
- FastAPI backend with structured API routing
- Environment files configured
- Database connection string added (Supabase PostgreSQL)
- Product specification documented in CLAUDE.md
- Local git repository initialized with first commit

⏳ **Pending:**
- GitHub repository creation (need to authenticate `gh` CLI)
- Database schema implementation
- Google OAuth integration
- Invoice extraction engine
- All other features (see TODO.md)

## Tech Stack
- **Frontend:** Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui
- **Backend:** FastAPI (Python), Pydantic
- **Database:** PostgreSQL (Supabase)
- **Auth:** Google OAuth 2.0
- **Email:** SendGrid or AWS SES (TBD)
- **Payments:** Stripe
- **OCR:** Google Cloud Vision API (Phase 2)

## File Structure
```
GWorkspaceAnalyzer/
├── frontend/          # Next.js app
├── backend/           # FastAPI app
├── CLAUDE.md          # Comprehensive product specification
├── TODO.md            # All development tasks
├── README.md          # Project overview
└── .git/              # Local git repository
```

## Environment Setup

### Backend
Database URL is already configured in `backend/.env`:
```
DATABASE_URL=postgresql://postgres:Wbn56t7pq!@db.hdkbxjxntgqqmducbmjn.supabase.co:5432/postgres
```

**Still needed:**
- Google OAuth credentials
- JWT secret key
- Stripe keys
- Email service API key

### Frontend
Located in `frontend/.env.local`:
- API URL (currently localhost:8000)
- Google Client ID
- Stripe publishable key

## Next Steps

### 1. Create GitHub Repository
First, authenticate with GitHub CLI, then create the repo:
```bash
gh auth login
gh repo create "Spend-Analyzer-for-Google-Workspace" --public --source=. --remote=origin --push --description "A Google Workspace add-on that scans Gmail for invoices/receipts and identifies duplicate charges, unnecessary subscriptions, and price increases"
```

### 2. Start Development Server
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (in separate terminal)
cd frontend
npm install
npm run dev
```

### 3. Begin Task #1 - Database Schema
See TODO.md for full task list. Start with designing the database schema for:
- Users (Google account info, subscription status, trial dates)
- Invoices (extracted invoice data)
- Vendors (normalized vendor names)
- Charges (individual line items)
- Issues (detected duplicates, subscriptions, price increases)
- UserActions (resolved, dismissed, notes)

## Quick Start Prompt for New Claude Session

```
I'm working on "Spend Analyzer for Google Workspace" - a Gmail add-on that finds duplicate charges, unnecessary subscriptions, and price increases.

Current status: Initial structure is done (Next.js 14 + FastAPI). Local git repo initialized.

Please review:
1. CLAUDE.md for full product spec
2. TODO.md for task list
3. backend/.env for current config

Next task: [INSERT TASK FROM TODO.md]

Let's continue development!
```

## Key Resources
- **Product Spec:** See CLAUDE.md
- **Task List:** See TODO.md
- **API Docs (once running):** http://localhost:8000/docs
- **Frontend:** http://localhost:3000

## Important Notes
- `.env` files contain secrets - never commit to git
- Database password is already filled in backend/.env
- Focus on MVP features first (see TODO.md Phase 1)
- Target: Free 90-day scan → $49/month subscription model
