# Supabase OAuth Setup Guide

## 1. Configure Google OAuth in Supabase Dashboard

1. Go to: https://supabase.com/dashboard/project/hdkbxjxntgqqmducbmjn/auth/providers
2. Find "Google" in the list of providers
3. Enable it and configure:
   - **Client ID**: Use your Google OAuth Client ID from Google Cloud Console
   - **Client Secret**: Use your Google OAuth Client Secret from Google Cloud Console
   - **Authorized Client IDs**: Leave empty (optional)
   - **Skip nonce check**: No (keep unchecked)

4. **Important**: Copy the "Callback URL (for OAuth)" shown on this page. It should be:
   `https://hdkbxjxntgqqmducbmjn.supabase.co/auth/v1/callback`

## 2. Update Google Cloud Console

1. Go to: https://console.cloud.google.com/apis/credentials
2. Find your OAuth 2.0 Client ID
3. Click Edit
4. Under "Authorized redirect URIs", add:
   - `https://hdkbxjxntgqqmducbmjn.supabase.co/auth/v1/callback`
   - Keep the existing: `http://localhost:3000/auth/callback`

5. Add the scopes we need in the OAuth consent screen:
   - Go to OAuth consent screen
   - Click "Edit App"
   - Under "Scopes", add:
     - `https://www.googleapis.com/auth/gmail.readonly`
     - `https://www.googleapis.com/auth/userinfo.email`
     - `https://www.googleapis.com/auth/userinfo.profile`

6. Save all changes

## 3. Test the Flow

1. Start backend: `cd backend && uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Navigate to: http://localhost:3000/login
4. Click "Continue with Google Workspace"
5. You should be redirected to Google OAuth
6. After authorizing, you'll be redirected back to `/auth/callback`
7. The callback should create your user and redirect to dashboard

## Troubleshooting

### Error: "redirect_uri_mismatch"
- Make sure you added the Supabase callback URL to Google Cloud Console
- Wait a few minutes for changes to propagate

### Error: "User not found" or database errors
- The backend will automatically create the user in the database
- Check that SUPABASE_JWT_SECRET is set correctly in backend/.env

### Session not persisting
- Check browser console for Supabase errors
- Verify NEXT_PUBLIC_SUPABASE_ANON_KEY is set in frontend/.env.local

### Dev Login (Bypass OAuth)
- Click "Dev Login (No OAuth)" button on login page
- This uses a mock user without requiring Google OAuth
- Useful for testing without setting up OAuth
