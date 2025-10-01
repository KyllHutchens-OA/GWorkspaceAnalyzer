# GWorkspace Analyzer - Development Guide

## Testing Without Real Gmail Invoices

We've built a **Development Mode** that lets you test the full application without needing a Gmail account with real invoices.

---

## Quick Start Guide

### 1. Start Backend (Terminal 1)

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Backend will run on: **http://localhost:8000**
API Docs: **http://localhost:8000/api/docs**

### 2. Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

Frontend will run on: **http://localhost:3000**

---

## Development Mode - Two Ways to Test

### Option A: Browser Console Dev Mode (Easiest)

1. Open **http://localhost:3000** in your browser
2. Open browser DevTools (F12)
3. In the Console, run:

```javascript
devMode.enable()    // Enable dev mode with mock auth
```

4. Refresh the page - you'll be "logged in" as a dev user
5. Seed test data:

```javascript
devMode.seed()      // Creates 30-50 invoices + findings
```

6. Navigate to `/dashboard` to see all the test data!

#### Other Dev Commands:

```javascript
devMode.clear()     // Clear all test data
devMode.disable()   // Disable dev mode
devMode.user        // View current dev user
```

---

### Option B: Manual API Testing (More Control)

#### Step 1: Get a Dev Token

Since we don't have real Google OAuth set up yet, we need to manually create a user and get a token:

**Option 1 - Using Supabase Dashboard:**
1. Go to your Supabase dashboard
2. Create a test user in the `users` table:
   ```sql
   INSERT INTO users (email, full_name, is_active)
   VALUES ('test@example.com', 'Test User', true)
   RETURNING id;
   ```
3. Note the `id` returned

**Option 2 - Use the backend directly:**
(You'll need to temporarily disable auth on the `/dev/seed` endpoint)

#### Step 2: Seed Test Data

Once you have the devMode enabled, call the seed endpoint:

```bash
POST http://localhost:8000/api/v1/dev/seed
Authorization: Bearer dev-token-12345-abcde

# Response:
{
  "message": "Successfully seeded development data",
  "invoices_created": 42,
  "findings_created": 8,
  "scan_jobs_created": 1
}
```

#### Step 3: View The Data

**Get scan jobs:**
```bash
GET http://localhost:8000/api/v1/scan/jobs
```

**Get invoices:**
```bash
GET http://localhost:8000/api/v1/invoices
```

**Get findings:**
```bash
GET http://localhost:8000/api/v1/findings
```

**Get findings summary:**
```bash
GET http://localhost:8000/api/v1/findings/summary
```

---

## What Data Gets Seeded?

The seed endpoint creates realistic test data:

### Invoices (30-50 total)
- **10 vendors**: AWS, Google Workspace, Stripe, Slack, Zoom, Notion, GitHub, Vercel, MongoDB, SendGrid
- **90-day date range**: Invoices spread across last 3 months
- **Realistic amounts**: Each vendor has typical pricing ranges
- **15% duplicates**: Some invoices are intentionally duplicated within 7 days

### Findings (5-15 total)
- **Duplicate charges**: Detects same amount charged twice within 7 days
- **Subscription sprawl**: Multiple subscriptions from same vendor
- **Price increases**: Vendors that raised prices >20%

### Scan Jobs
- 1 completed scan job with metadata
- Shows processing time, email counts, etc.

---

## Frontend Development

### Testing the Dashboard

With dev mode enabled and data seeded:

1. Go to **http://localhost:3000/dashboard**
2. You should see:
   - Total waste amount calculated from findings
   - Issue cards (duplicates, subscriptions, price increases)
   - Findings table with real data
   - Recent scan job status

### Testing Authentication Flow

**Not yet fully implemented** - OAuth requires Google Cloud Project setup.

For now:
- Login page is styled and ready
- OAuth callback flow is wired up
- Use dev mode for testing

---

## API Client Usage

The frontend now has a type-safe API client at `frontend/src/lib/api.ts`:

```typescript
import api from '@/lib/api';

// Scans
const jobs = await api.scans.list();
const job = await api.scans.get(jobId);
await api.scans.start('2024-01-01', '2024-03-31');

// Invoices
const invoices = await api.invoices.list({ vendor: 'AWS' });
const stats = await api.invoices.getStats();

// Findings
const findings = await api.findings.list({ status: 'new' });
const summary = await api.findings.getSummary();
await api.findings.updateStatus(findingId, 'resolved');

// Dev endpoints
await api.dev.seedData();
await api.dev.clearData();
```

---

## Common Development Tasks

### Clear and Reseed Data

```javascript
// In browser console:
await devMode.clear()
await devMode.seed()
```

### Test Different Scenarios

The seed data generator creates varied scenarios automatically, but you can modify `backend/app/api/v1/endpoints/dev.py` to:
- Change vendor lists
- Adjust duplicate probability
- Modify price increase thresholds
- Add custom invoice patterns

### Check Backend Logs

The backend logs show what's happening:
- Scan processing progress
- Invoice extraction results
- Finding generation

### Inspect Database Directly

If you want to see the raw data:

```sql
-- View all invoices
SELECT vendor_name, amount, invoice_date
FROM invoices
ORDER BY invoice_date DESC;

-- View all findings
SELECT finding_type, title, potential_savings
FROM findings
WHERE status = 'new';
```

---

## Troubleshooting

### "Seed endpoint only available in development mode"

Make sure `DEBUG = True` in `backend/app/config/settings.py`

### "No data showing in dashboard"

1. Check dev mode is enabled: `localStorage.getItem('dev_mode')`
2. Verify auth token: `localStorage.getItem('auth_token')`
3. Check if data was seeded: `devMode.seed()`
4. Look at Network tab in DevTools for API errors

### Backend Connection Refused

- Make sure backend is running on port 8000
- Check `.env.local` has `NEXT_PUBLIC_API_URL=http://localhost:8000`
- Verify CORS is allowing localhost:3000

---

## Next Steps for Production

To move from dev mode to real OAuth:

1. **Create Google Cloud Project**
   - Enable Gmail API
   - Set up OAuth consent screen
   - Create OAuth credentials
   - Add redirect URI: `http://localhost:8000/api/v1/auth/google/callback`

2. **Update Environment Variables**
   ```
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
   ```

3. **Test Real OAuth Flow**
   - Disable dev mode
   - Click "Continue with Google Workspace"
   - Authorize Gmail access
   - Backend exchanges code for token
   - User redirected to dashboard

4. **Test Real Scan**
   - Click "Start Scan" button (when implemented)
   - Backend fetches real Gmail emails
   - Invoices extracted and analyzed
   - Findings generated
   - Results displayed

---

## Development Workflow

```bash
# Clean slate
devMode.clear()

# Test invoice parsing
devMode.seed()

# Make changes to findings logic
# ... edit backend code ...

# Re-seed to see new results
devMode.clear()
devMode.seed()

# Check findings
fetch('http://localhost:8000/api/v1/findings/summary')
  .then(r => r.json())
  .then(console.log)
```

---

## API Documentation

Full interactive API docs available at:
**http://localhost:8000/api/docs**

Try out endpoints directly from the Swagger UI!

---

Happy coding!
