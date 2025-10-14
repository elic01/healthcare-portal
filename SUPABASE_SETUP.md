# Supabase Database Setup Guide

This guide walks you through setting up a new Supabase database for the Healthcare Portal.

## Table of Contents

- [Creating a Supabase Account](#creating-a-supabase-account)
- [Creating a New Project](#creating-a-new-project)
- [Database Setup](#database-setup)
- [Getting Your Credentials](#getting-your-credentials)
- [Configuring Your Application](#configuring-your-application)
- [Verifying Setup](#verifying-setup)
- [Migrating to a New Supabase Account](#migrating-to-a-new-supabase-account)

## Creating a Supabase Account

1. Go to [https://supabase.com](https://supabase.com)
2. Click **"Start your project"** or **"Sign Up"**
3. Sign up with:
   - GitHub account (recommended)
   - Google account
   - Email and password

## Creating a New Project

1. After logging in, click **"New Project"**
2. Fill in the project details:
   - **Name**: `healthcare-portal` (or your preferred name)
   - **Database Password**: Choose a strong password (save this!)
   - **Region**: Choose the closest region to your users
   - **Pricing Plan**: Free tier is sufficient for development

3. Click **"Create new project"**
4. Wait 2-3 minutes for the project to be provisioned

## Database Setup

### Step 1: Access the SQL Editor

1. In your Supabase project dashboard, click **"SQL Editor"** in the left sidebar
2. Click **"New Query"** to create a blank query

### Step 2: Run the Main Schema Script

1. Open the `supabase_schema.sql` file from your project folder
2. Copy the entire contents
3. Paste into the SQL Editor in Supabase
4. Click **"Run"** or press `Ctrl+Enter` (Windows/Linux) or `Cmd+Enter` (Mac)

You should see:
```
Success. No rows returned
```

This script creates:
- **users** table - All system users
- **patients** table - Patient-specific information
- **medical_staff** table - Doctor/nurse information
- **appointments** table - Appointment scheduling
- **medical_records** table - Patient medical records
- **audit_logs** table - Security and compliance logging
- **Indexes** for performance optimization
- **Triggers** for automatic timestamp updates

### Step 3: Create the Admin User

1. Create a new query in the SQL Editor
2. Open the `create_admin.sql` file
3. Copy and paste the contents
4. Click **"Run"**

This creates a default administrator account:
- **Username**: `admin`
- **Password**: `admin123`

**IMPORTANT**: Change this password after first login!

### Step 4: Verify Table Creation

Run this query to verify all tables were created:

```sql
SELECT
    schemaname,
    tablename,
    tableowner
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
```

You should see these tables:
- appointments
- audit_logs
- medical_records
- medical_staff
- patients
- users

### Step 5: Check Row-Level Security (Optional for Development)

For development, you may want to disable Row Level Security (RLS):

```sql
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE patients DISABLE ROW LEVEL SECURITY;
ALTER TABLE medical_staff DISABLE ROW LEVEL SECURITY;
ALTER TABLE appointments DISABLE ROW LEVEL SECURITY;
ALTER TABLE medical_records DISABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs DISABLE ROW LEVEL SECURITY;
```

**NOTE**: For production, implement proper RLS policies instead of disabling.

## Getting Your Credentials

### Supabase URL

1. In your project dashboard, click **"Settings"** (gear icon)
2. Click **"API"** in the left menu
3. Under **"Project URL"**, copy the URL
   - Format: `https://[project-id].supabase.co`
   - Example: `https://mmfsjnpxwlbhcfftjlse.supabase.co`

### Supabase Anon Key

1. In the same **API** settings page
2. Under **"Project API keys"**, find **"anon public"**
3. Click the copy icon to copy the key
   - This is a long JWT token
   - Example: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

### Database Password (Optional)

If you need direct database access:
1. Go to **Settings** > **Database**
2. Find your connection string under **"Connection string"**
3. Choose **"URI"** or **"Pooler"** depending on your needs

## Configuring Your Application

### Step 1: Update .env File

1. Open the `.env` file in your project root
2. Update these values with your Supabase credentials:

```env
# =====================================
# SUPABASE CONFIGURATION
# =====================================
SUPABASE_URL=https://[your-project-id].supabase.co
SUPABASE_ANON_KEY=your-anon-key-here

# =====================================
# DATABASE CONFIGURATION
# =====================================
DEV_DATABASE_URL=https://[your-project-id].supabase.co
DATABASE_URL=https://[your-project-id].supabase.co
```

### Step 2: Update Flask Secret Key

Generate a secure secret key for production:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Update in `.env`:
```env
SECRET_KEY=<generated-secret-key>
```

### Step 3: Save and Restart

1. Save the `.env` file
2. Restart your Flask application

## Verifying Setup

### Test 1: Check Database Connection

Run the Python CLI tool:

```bash
python data_supabase.py
```

If connected successfully, you'll see:
```
Successfully connected to Supabase database!
```

### Test 2: Test Admin Login

1. Start the Flask application:
   ```bash
   python app.py
   ```

2. Open browser to `http://localhost:5000`

3. Login with:
   - Username: `admin`
   - Password: `admin123`

4. If successful, you should see the Administrator Dashboard

### Test 3: Create a Test User

1. Login as admin
2. Navigate to "Manage Users"
3. Create a new test user
4. Logout and login with the new user

## Migrating to a New Supabase Account

If you need to move to a new Supabase account or project:

### Option 1: Fresh Setup

1. Create new Supabase project (follow steps above)
2. Run all SQL scripts in order:
   - `supabase_schema.sql`
   - `create_admin.sql`
3. Update `.env` with new credentials
4. Restart application

### Option 2: Export and Import Data

1. **Export from old database**:
   ```bash
   # In Supabase SQL Editor (old project)
   COPY users TO STDOUT WITH CSV HEADER;
   COPY patients TO STDOUT WITH CSV HEADER;
   COPY medical_staff TO STDOUT WITH CSV HEADER;
   COPY appointments TO STDOUT WITH CSV HEADER;
   COPY medical_records TO STDOUT WITH CSV HEADER;
   ```

2. **Create new database** (follow steps above)

3. **Import to new database**:
   - Use Supabase dashboard's Table Editor
   - Or use SQL COPY commands
   - Or use the Supabase CLI

### Option 3: Using Supabase CLI

1. Install Supabase CLI:
   ```bash
   npm install -g supabase
   ```

2. Login to Supabase:
   ```bash
   supabase login
   ```

3. Link to your project:
   ```bash
   supabase link --project-ref [your-project-id]
   ```

4. Pull database schema:
   ```bash
   supabase db pull
   ```

5. Push to new project:
   ```bash
   supabase link --project-ref [new-project-id]
   supabase db push
   ```

## Troubleshooting

### Issue: "relation already exists"

If you see errors about tables already existing:

1. Either drop the existing tables:
   ```sql
   DROP TABLE IF EXISTS audit_logs CASCADE;
   DROP TABLE IF EXISTS medical_records CASCADE;
   DROP TABLE IF EXISTS appointments CASCADE;
   DROP TABLE IF EXISTS medical_staff CASCADE;
   DROP TABLE IF EXISTS patients CASCADE;
   DROP TABLE IF EXISTS users CASCADE;
   ```

2. Or modify the SQL script to skip existing tables (the `IF NOT EXISTS` clauses should handle this)

### Issue: "permission denied"

If you get permission errors:
1. Make sure you're using the correct API key
2. Check that you're running queries in the SQL Editor, not via API
3. Verify your Supabase project is active and not paused

### Issue: Missing columns

If the application reports missing columns:
1. Run the `add_missing_columns.sql` script
2. This adds any columns that may have been missed

### Issue: Cannot connect to database

1. Verify your Supabase URL and key in `.env`
2. Check that your project is not paused (free tier)
3. Ensure you have internet connection
4. Check Supabase status at [status.supabase.com](https://status.supabase.com)

### Issue: Admin user already exists

If you see "duplicate key value violates unique constraint":
- The admin user already exists
- You can skip this step or change the username in the script

## Security Best Practices

### For Development
- Use the anon key (it's meant to be public)
- Disable RLS for easier testing
- Keep database password secure

### For Production
1. **Enable Row Level Security**:
   ```sql
   ALTER TABLE users ENABLE ROW LEVEL SECURITY;
   -- Create appropriate policies
   ```

2. **Change default admin password** immediately

3. **Use environment variables** for all secrets

4. **Enable SSL/TLS** for database connections

5. **Regularly backup** your database:
   - Supabase provides automatic backups
   - Set up additional backup schedule

6. **Monitor audit logs** regularly

7. **Rotate API keys** periodically

## Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Supabase CLI Documentation](https://supabase.com/docs/guides/cli)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Supabase logs in the dashboard
3. Check the application logs for detailed error messages
4. Verify all SQL scripts ran successfully
