# Google OAuth Setup Guide

## Overview
You need to create a Google Cloud Project and configure OAuth 2.0 credentials to enable:
- Google Sign-In (authentication)
- Gmail API access (to scan for invoices)

## Step-by-Step Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a project** > **New Project**
3. Enter project details:
   - **Project name**: `GWorkspace Analyzer` (or your preferred name)
   - **Organization**: (optional)
   - Click **Create**
4. Wait for project creation (takes ~30 seconds)
5. Select your new project from the dropdown

### 2. Enable Required APIs

1. In Google Cloud Console, go to **APIs & Services** > **Library**
2. Search and enable these APIs (click each, then click "Enable"):
   - **Gmail API** (for reading emails/invoices)
   - **Google+ API** or **Google People API** (for user profile info)

### 3. Configure OAuth Consent Screen

1. Go to **APIs & Services** > **OAuth consent screen**
2. Choose **User Type**:
   - **External** (if you want anyone to use it)
   - **Internal** (if only for your Google Workspace domain)
3. Click **Create**

4. Fill in **App Information**:
   - **App name**: `GWorkspace Analyzer`
   - **User support email**: Your email
   - **App logo**: (optional, upload later)
   - **Application home page**: `http://localhost:3000` (for now)
   - **Application privacy policy**: (can skip for development)
   - **Application terms of service**: (can skip for development)
   - **Authorized domains**: Add your production domain later
   - **Developer contact email**: Your email
   - Click **Save and Continue**

5. **Scopes** (click "Add or Remove Scopes"):
   - Add these scopes:
     - `https://www.googleapis.com/auth/gmail.readonly` (read Gmail)
     - `https://www.googleapis.com/auth/userinfo.email` (user email)
     - `https://www.googleapis.com/auth/userinfo.profile` (user profile)
   - Click **Update** > **Save and Continue**

6. **Test Users** (if External app in testing mode):
   - Add your email address
   - Add any other emails you want to test with
   - Click **Save and Continue**

7. **Summary**:
   - Review and click **Back to Dashboard**

### 4. Create OAuth 2.0 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. Choose **Application type**:
   - Select: **Web application**
4. Fill in details:
   - **Name**: `GWorkspace Analyzer Web Client`

   - **Authorized JavaScript origins**:
     - `http://localhost:3000` (for local frontend)
     - `http://localhost:8000` (for local backend)
     - Add production URLs later: `https://yourdomain.com`

   - **Authorized redirect URIs**:
     - For Supabase Auth: `https://hdkbxjxntgqqmducbmjn.supabase.co/auth/v1/callback`
     - For local development: `http://localhost:3000/auth/callback`
     - For backend testing: `http://localhost:8000/auth/callback`

5. Click **Create**

6. **IMPORTANT**: Copy credentials shown:
   - **Client ID** (looks like: `123456789-abc.apps.googleusercontent.com`)
   - **Client Secret** (looks like: `GOCSPX-xxxxxxxxxxxxx`)
   - Save these securely! You'll need them next.

### 5. Configure Supabase

1. Go to [Supabase Dashboard](https://supabase.com/dashboard/project/hdkbxjxntgqqmducbmjn/auth/providers)
2. Find **Google** provider
3. Toggle it **ON**
4. Enter:
   - **Client ID**: (paste from step 4)
   - **Client Secret**: (paste from step 4)
5. Copy the **Callback URL** shown (should be):
   ```
   https://hdkbxjxntgqqmducbmjn.supabase.co/auth/v1/callback
   ```
6. Click **Save**

7. Go back to Google Cloud Console > Credentials > Edit your OAuth client
8. Add the Supabase callback URL to **Authorized redirect URIs** if not already there
9. Click **Save**

### 6. Update Environment Variables

Add to `backend/.env`:

```env
GOOGLE_CLIENT_ID="your-client-id-here.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="GOCSPX-your-secret-here"
GOOGLE_REDIRECT_URI="https://hdkbxjxntgqqmducbmjn.supabase.co/auth/v1/callback"
```

Add to `frontend/.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL="https://hdkbxjxntgqqmducbmjn.supabase.co"
NEXT_PUBLIC_SUPABASE_ANON_KEY="your-anon-key"
NEXT_PUBLIC_GOOGLE_CLIENT_ID="your-client-id-here.apps.googleusercontent.com"
```

### 7. Testing OAuth Flow

Once configured, you can test:

1. Go to your frontend: `http://localhost:3000`
2. Click "Sign in with Google"
3. You should see Google's consent screen
4. Grant permissions
5. You'll be redirected back to your app

## Important Scopes for This Project

For invoice scanning, you need:

```
https://www.googleapis.com/auth/gmail.readonly
```

This allows:
- Reading email metadata
- Reading email content
- Downloading attachments
- But NOT sending emails or modifying anything

## Security Notes

1. **Keep Client Secret private**: Never commit to Git
2. **Use .env files**: Already in `.gitignore`
3. **Restrict API keys**: Add domain restrictions in production
4. **OAuth Consent Screen**: Verify it before going public
5. **Scopes**: Request only what you need (principle of least privilege)

## Quotas & Limits

- **Gmail API**: 1 billion quota units/day (default)
- **Read request**: 5 quota units
- **Typical usage**: ~50,000 email reads/day max

If you need more, request quota increase in Google Cloud Console.

## Publishing Your App (Later)

Currently in "Testing" mode (max 100 users). To go public:

1. Complete OAuth consent screen
2. Add privacy policy & terms of service
3. Submit for verification (takes 1-2 weeks)
4. Once approved, anyone can use it

For now, stay in testing mode and add users manually.

## Troubleshooting

### "Access blocked: This app's request is invalid"
- Check redirect URI exactly matches what's in Google Cloud Console
- Make sure OAuth consent screen is configured

### "Error 400: redirect_uri_mismatch"
- Redirect URI in your code doesn't match Google Cloud Console
- Add the exact URI to authorized redirect URIs

### "This app isn't verified"
- Normal for testing mode
- Click "Advanced" > "Go to [app name] (unsafe)"
- Or submit app for verification

### Can't enable Gmail API
- Make sure billing is enabled (free tier is fine)
- Check you're in the correct project

## Next Steps After Setup

1. Test authentication flow
2. Implement Gmail API queries
3. Build invoice parsing logic
4. Test with your own Gmail account

---

**Quick Reference:**
- Google Cloud Console: https://console.cloud.google.com/
- Supabase Auth Settings: https://supabase.com/dashboard/project/hdkbxjxntgqqmducbmjn/auth/providers
- Gmail API Docs: https://developers.google.com/gmail/api
