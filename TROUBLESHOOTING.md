# Troubleshooting Guide

## Issue: Stuck on "Loading..." screen

### Quick Fix
1. Wait 3 seconds for debug buttons to appear
2. Click **"Go to Dashboard"** to bypass authentication
3. Or click **"Go to Landing"** to see the landing page

### Root Cause
The app is waiting for Supabase authentication to complete. If Supabase is not properly configured or slow to respond, the loading screen will persist.

### Solutions

#### Option 1: Use Dev Mode (Recommended for Testing)
1. Open browser console (F12)
2. Run: `devMode.enable()`
3. Refresh the page
4. You'll be automatically logged in with a mock user

#### Option 2: Bypass Auth Temporarily
Go directly to pages:
- Dashboard: http://localhost:3001/dashboard
- Landing: http://localhost:3001/landing
- Login: http://localhost:3001/login

#### Option 3: Configure Supabase Properly
Make sure your `.env.local` has valid Supabase credentials:
```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
```

Check your Supabase console for the correct values.

#### Option 4: Disable Supabase Auth (Use Backend JWT Only)
If you want to skip Supabase entirely:

1. Modify `frontend/src/app/page.tsx` to bypass auth:
```typescript
useEffect(() => {
  // Skip auth check, go straight to landing
  router.push('/landing');
}, [router]);
```

## Issue: Console shows "Syntax Error" or "Unexpected token"

### Solution
This was fixed in the latest changes. Make sure you have:
- Changed `limit: 50` to `page_size: 50` in `dashboard/page.tsx` line 47

Run: `npx tsc --noEmit` to check for TypeScript errors

## Issue: API calls fail with 401 Unauthorized

### Solutions

1. **Using Dev Mode**: Run `devMode.enable()` in console
2. **Using Real Auth**: Make sure you're logged in via Supabase
3. **Check API URL**: Verify `NEXT_PUBLIC_API_URL=http://localhost:8000` in `.env.local`
4. **Backend Running**: Make sure backend is running on port 8000

## Issue: favicon.ico 404 error

This is harmless. To fix, add a favicon:
```bash
# Download or create a favicon.ico and place in:
frontend/public/favicon.ico
```

## Dev Tools Available

Open browser console and access:
```javascript
devMode.enable()   // Enable dev mode with mock auth
devMode.disable()  // Disable dev mode
devMode.seed()     // Seed test data to backend
devMode.clear()    // Clear test data from backend
```

## Checking Logs

### Frontend Console
1. Open DevTools (F12)
2. Check Console tab for errors
3. Look for:
   - "Auth status: loading/authenticated/unauthenticated"
   - "Checking auth with Supabase..."
   - Any API error messages

### Backend Logs
```bash
cd backend
uvicorn app.main:app --reload
# Watch for API request logs
```

## Testing the Full Flow

1. **Start Backend**:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```
   Should see: "Starting GWorkspace Analyzer API v1.0.0"

2. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```
   Should see: "Ready in X.Xs"

3. **Enable Dev Mode** (in browser console):
   ```javascript
   devMode.enable()
   ```

4. **Navigate to Dashboard**:
   http://localhost:3001/dashboard

5. **Seed Test Data** (in console):
   ```javascript
   await devMode.seed()
   ```

6. **Refresh Dashboard** to see data

## Common Port Issues

- Frontend default: 3000 (may use 3001 if 3000 is busy)
- Backend default: 8000
- Make sure `NEXT_PUBLIC_API_URL` matches backend port
