# GWorkspace Analyzer - Setup Guide

## Environment Configuration

### Backend (.env)

Create `backend/.env` with the following variables:

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/gworkspace
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_JWT_SECRET=your_jwt_secret

# Google OAuth & Gmail API
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/callback

# JWT Settings
SECRET_KEY=your_secret_key_here_minimum_32_chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Frontend (.env.local)

Already configured in `frontend/.env.local`:

```env
# API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://hdkbxjxntgqqmducbmjn.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
```

## API Integration Summary

### Completed Features

1. **API Client (`frontend/src/lib/api.ts`)**
   - Type-safe methods for all backend endpoints
   - Automatic authentication header injection
   - Error handling with typed responses
   - Endpoints: auth, scans, invoices, findings

2. **Authentication Flow**
   - Supabase Auth integration via `AuthContext`
   - Google OAuth sign-in
   - Token management in localStorage
   - Protected routes ready

3. **Dashboard Integration (`frontend/src/app/dashboard/page.tsx`)**
   - Real-time data from API instead of mock data
   - Findings summary from `/api/v1/findings/summary`
   - Invoice statistics from `/api/v1/invoices/stats/summary`
   - Scan job status from `/api/v1/scan/jobs`
   - Dynamic calculations for waste totals

4. **Scan Job Triggers (`QuickActionsBar.tsx`)**
   - "Scan Emails" button triggers POST `/api/v1/scan/start`
   - Background job processing
   - Real-time feedback to user

### API Endpoints Used

#### Authentication
- `GET /api/v1/auth/google/login` - Get OAuth URL
- `POST /api/v1/auth/google/callback` - Exchange code for token
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/refresh` - Refresh access token

#### Scan Jobs
- `POST /api/v1/scan/start` - Start new Gmail scan
- `GET /api/v1/scan/jobs?limit=10` - List scan jobs
- `GET /api/v1/scan/jobs/{id}` - Get scan job details
- `DELETE /api/v1/scan/jobs/{id}` - Cancel scan job

#### Invoices
- `GET /api/v1/invoices?page=1&page_size=20` - List invoices (paginated)
- `GET /api/v1/invoices/{id}` - Get invoice details
- `GET /api/v1/invoices/stats/summary` - Get invoice statistics
- `GET /api/v1/invoices/vendors/list` - List vendors

#### Findings
- `GET /api/v1/findings?status=pending&page=1` - List findings (paginated)
- `GET /api/v1/findings/{id}` - Get finding details
- `GET /api/v1/findings/{id}/invoices` - Get related invoices
- `PATCH /api/v1/findings/{id}` - Update finding status
- `GET /api/v1/findings/summary` - Get findings summary

### Dashboard Data Flow

```
Dashboard Loads
    ↓
loadDashboardData()
    ├── api.findings.list({ status: 'pending' })
    ├── api.findings.getSummary()
    ├── api.invoices.getStats()
    └── api.scans.list(1)
    ↓
Map Backend Data → Frontend Types
    ├── FindingResponse[] → Finding[]
    ├── Summary → IssueSummary[]
    ├── Stats → DashboardStats
    └── Scan Jobs → Activity Log
    ↓
Render Components with Real Data
```

### Real Numbers Now Displayed

All hardcoded mock values have been replaced with real API data:

- **Total Waste**: Sum of `total_guaranteed_waste + total_potential_waste`
- **Invoices Analyzed**: From `total_invoices` in invoice stats
- **Issues Found**: From `pending_count` in findings summary
- **Scans Used**: Count of completed scan jobs
- **Duplicate Charges**: From `by_type.duplicate.total_amount`
- **Unused Subscriptions**: From `by_type.unused_subscription.total_amount`
- **Price Increases**: From `by_type.price_increase.total_amount`

### Next Steps

To fully test the integration:

1. **Start Backend**:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test Flow**:
   - Visit http://localhost:3000/login
   - Sign in with Google (Supabase Auth)
   - Click "Scan Emails" to trigger a scan
   - View real findings on dashboard

### Known Limitations

1. **Missing Backend Algorithms**:
   - Subscription tracking (recurring charge detection)
   - Price monitoring (month-over-month comparison)
   - Need to be implemented in backend

2. **Savings Calculation**:
   - Currently calculated from resolved findings
   - Needs refinement based on actual user actions

3. **Real-time Updates**:
   - Dashboard requires manual refresh to see scan progress
   - Consider adding WebSocket or polling for live updates

### Files Modified

1. `frontend/src/lib/api.ts` - Fixed endpoint paths and response types
2. `frontend/src/app/dashboard/page.tsx` - Integrated real API data
3. `frontend/src/components/QuickActionsBar.tsx` - Added scan trigger
4. `frontend/.env.local` - API URL configuration
