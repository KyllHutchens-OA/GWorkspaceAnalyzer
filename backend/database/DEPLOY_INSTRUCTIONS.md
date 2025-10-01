# Database Deployment Instructions

## Issue
Direct PostgreSQL connections to Supabase are being blocked by your network/firewall.

## Solution: Deploy via Supabase Dashboard (2 minutes)

### Step-by-Step:

1. **Open Supabase SQL Editor**
   - Click this link: https://supabase.com/dashboard/project/hdkbxjxntgqqmducbmjn/sql/new
   - Or manually navigate to:
     - Go to: https://supabase.com/dashboard
     - Select project: `hdkbxjxntgqqmducbmjn`
     - Click: **SQL Editor** (left sidebar)
     - Click: **New Query**

2. **Copy the SQL Migration**
   - Open file: `backend/database/migrations/001_initial_schema.sql`
   - Select all (Ctrl+A)
   - Copy (Ctrl+C)

3. **Paste and Run**
   - Paste into Supabase SQL Editor (Ctrl+V)
   - Click: **Run** button (or press Ctrl+Enter)
   - Wait ~5-10 seconds for completion

4. **Verify Success**
   You should see output similar to:
   ```
   Success. No rows returned
   ```

   Run this verification query in a new SQL tab:
   ```sql
   SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;
   ```

   You should see tables:
   - audit_log
   - finding_invoices
   - findings
   - invoice_content
   - invoices
   - organizations
   - scan_jobs
   - users
   - vendors

## Alternative: Use File Directly

If copy/paste is difficult (file is 500+ lines), you can:

1. In Supabase SQL Editor, click the **Upload** button (if available)
2. Select: `backend/database/migrations/001_initial_schema.sql`
3. Click **Run**

## Troubleshooting

### Error: "relation already exists"
- The table already exists in your database
- Either:
  - A) Drop all tables first (see rollback section in `migrations/README.md`)
  - B) Skip this migration (tables already created)

### Error: "permission denied"
- Make sure you're logged into Supabase with the correct account
- Verify project ID: `hdkbxjxntgqqmducbmjn`

### Error: "syntax error"
- Make sure you copied the ENTIRE file (including the top comments)
- Don't copy line numbers if viewing in an editor

## Next Steps After Deployment

Once migration is successful:

1. **Enable Google OAuth**
   - Dashboard > Authentication > Providers > Google
   - Add your OAuth credentials

2. **Create Storage Bucket**
   - Dashboard > Storage > New Bucket
   - Name: `invoice-attachments`
   - Public: No (private)

3. **Set up Supabase Vault** (for secure token storage)
   - Dashboard > Database > Vault
   - Create new secret for Google refresh tokens

4. **Update Environment Variables**
   ```bash
   # In backend/.env, add:
   GOOGLE_CLIENT_ID="your-client-id"
   GOOGLE_CLIENT_SECRET="your-client-secret"
   ```

## Verification Query

After deployment, run this to verify everything:

```sql
-- Check tables (should be 9+)
SELECT COUNT(*) as table_count FROM pg_tables WHERE schemaname = 'public';

-- Check RLS is enabled (should be 8+)
SELECT COUNT(*) as rls_enabled FROM pg_tables WHERE schemaname = 'public' AND rowsecurity = true;

-- Check ENUMs (should be 4)
SELECT COUNT(DISTINCT typname) FROM pg_type t JOIN pg_enum e ON t.oid = e.enumtypid;

-- Check views (should be 2)
SELECT COUNT(*) FROM pg_views WHERE schemaname = 'public';

-- Check indexes (should be 15+)
SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public';
```

Expected results:
- Tables: 9
- RLS enabled: 8
- ENUMs: 4
- Views: 2
- Indexes: 15+

---

**Your Supabase Project:**
- URL: https://hdkbxjxntgqqmducbmjn.supabase.co
- Project ID: hdkbxjxntgqqmducbmjn
- SQL Editor: https://supabase.com/dashboard/project/hdkbxjxntgqqmducbmjn/sql
