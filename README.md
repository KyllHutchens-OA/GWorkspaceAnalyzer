# GWorkspace Analyzer

A full-stack application with Next.js 14 frontend and FastAPI backend.

## Project Structure

```
GWorkspaceAnalyzer/
├── frontend/                 # Next.js 14 with App Router
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   │   ├── layout.tsx   # Root layout
│   │   │   ├── page.tsx     # Home page
│   │   │   └── globals.css  # Global styles with Tailwind
│   │   ├── components/      # React components
│   │   │   └── ui/          # shadcn/ui components
│   │   └── lib/             # Utility functions
│   │       └── utils.ts     # cn() helper for Tailwind
│   ├── public/              # Static assets
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── components.json      # shadcn/ui config
│
└── backend/                  # FastAPI Python backend
    ├── app/
    │   ├── api/
    │   │   └── v1/
    │   │       ├── endpoints/   # API endpoints
    │   │       └── __init__.py  # API router
    │   ├── core/
    │   │   └── config.py        # App configuration
    │   ├── models/              # Database models
    │   ├── schemas/             # Pydantic schemas
    │   ├── services/            # Business logic
    │   └── main.py              # FastAPI app entry point
    ├── requirements.txt
    └── .env.example
```

## Getting Started

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

The frontend will run on http://localhost:3000

### Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend will run on http://localhost:8000
API docs available at http://localhost:8000/docs

## Tech Stack

### Frontend
- **Next.js 14** with App Router
- **TypeScript**
- **Tailwind CSS** for styling
- **shadcn/ui** for UI components

### Backend
- **FastAPI** for Python web framework
- **Pydantic** for data validation
- **Uvicorn** as ASGI server

## Adding shadcn/ui Components

```bash
cd frontend
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
# Add more components as needed
```
