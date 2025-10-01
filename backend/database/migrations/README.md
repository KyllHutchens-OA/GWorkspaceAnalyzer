# Database Migrations

## Running Migrations in Supabase

### Option 1: Supabase Dashboard (Recommended for initial setup)

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Click **New Query**
4. Copy and paste the contents of `001_initial_schema.sql`
5. Click **Run** or press `Ctrl+Enter`

### Option 2: Supabase CLI

```bash
# Install Supabase CLI if not already installed
npm install -g supabase

# Initialize Supabase in your project (first time only)
supabase init

# Link to your remote project
supabase link --project-ref your-project-ref

# Run migrations
supabase db push
```

### Option 3: Direct PostgreSQL Connection

```bash
# Get connection string from Supabase Dashboard > Settings > Database
psql "postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-REF].supabase.co:5432/postgres" -f 001_initial_schema.sql
```

## Migration Files

- `001_initial_schema.sql` - Core database schema with all tables, indexes, RLS policies

## Rollback

To rollback the initial migration, run:

```sql
-- Drop all tables in reverse order of dependencies
DROP VIEW IF EXISTS recent_invoices CASCADE;
DROP VIEW IF EXISTS dashboard_summary CASCADE;
DROP TABLE IF EXISTS audit_log CASCADE;
DROP TABLE IF EXISTS vendors CASCADE;
DROP TABLE IF EXISTS finding_invoices CASCADE;
DROP TABLE IF EXISTS findings CASCADE;
DROP TABLE IF EXISTS invoice_content CASCADE;
DROP TABLE IF EXISTS invoices CASCADE;
DROP TABLE IF EXISTS scan_jobs CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS organizations CASCADE;
DROP TYPE IF EXISTS scan_status;
DROP TYPE IF EXISTS finding_status;
DROP TYPE IF EXISTS finding_type;
DROP TYPE IF EXISTS subscription_tier;
```

## Verification

After running migrations, verify the schema:

```sql
-- Check tables
SELECT tablename FROM pg_tables WHERE schemaname = 'public';

-- Check RLS is enabled
SELECT tablename, rowsecurity FROM pg_tables
WHERE schemaname = 'public' AND rowsecurity = true;

-- Check indexes
SELECT indexname, tablename FROM pg_indexes
WHERE schemaname = 'public';
```

## Next Steps

1. Set up Supabase Auth (Google OAuth provider)
2. Configure Storage bucket for invoice attachments
3. Set up Supabase Vault for storing Google refresh tokens
4. Configure environment variables in your backend
