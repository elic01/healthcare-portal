# Migration Guide

This guide helps you migrate the Healthcare Portal to a new PC, server, or Supabase account.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Scenario 1: Moving to a New PC (Same Database)](#scenario-1-moving-to-a-new-pc-same-database)
- [Scenario 2: New Supabase Account (Fresh Start)](#scenario-2-new-supabase-account-fresh-start)
- [Scenario 3: New Supabase Account (With Data)](#scenario-3-new-supabase-account-with-data)
- [Scenario 4: Server Deployment](#scenario-4-server-deployment)
- [Verification Steps](#verification-steps)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before starting migration:

- [ ] Python 3.8+ installed
- [ ] Git installed
- [ ] Access to the original `.env` file or Supabase credentials
- [ ] Backup of any important data
- [ ] New Supabase account (if creating new database)

## Scenario 1: Moving to a New PC (Same Database)

Use this when you want to set up the application on a new computer but keep using the same Supabase database.

### Step 1: Clone or Copy the Project

**Option A: Using Git**
```bash
# Clone the repository
git clone <your-repository-url>
cd healthcare-portal
```

**Option B: Copy Files**
```bash
# Copy the entire project folder to the new PC
# Ensure all files are transferred
```

### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Copy Environment Configuration

1. Copy your `.env` file from the old PC to the new PC
2. Place it in the project root directory
3. Verify the contents:

```bash
cat .env  # Linux/macOS
type .env  # Windows
```

### Step 5: Test the Application

```bash
# Test database connection
python data_supabase.py

# Run the application
python app.py
```

### Step 6: Access the Application

Open browser to `http://localhost:5000`

**Done!** Your application should work exactly as before.

---

## Scenario 2: New Supabase Account (Fresh Start)

Use this when you want to create a completely new database with no existing data.

### Step 1: Set Up New Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Log in or create account
3. Click **"New Project"**
4. Fill in details:
   - Name: `healthcare-portal-new`
   - Database Password: (save this!)
   - Region: Choose closest to your users
5. Click **"Create new project"**
6. Wait for provisioning (2-3 minutes)

### Step 2: Run Database Scripts

1. In Supabase dashboard, go to **SQL Editor**
2. Click **"New Query"**
3. Copy and paste `supabase_schema.sql` content
4. Click **"Run"** or press `Ctrl+Enter`
5. Wait for completion (should see "Success")

6. Create a new query and run `create_admin.sql`
7. Click **"Run"**

### Step 3: Get New Credentials

1. Go to **Settings** > **API**
2. Copy:
   - **Project URL** (under "Config")
   - **anon public key** (under "Project API keys")

### Step 4: Update .env File

Update your `.env` file with new credentials:

```env
SUPABASE_URL=https://[new-project-id].supabase.co
SUPABASE_ANON_KEY=[your-new-anon-key]
```

### Step 5: Set Up Application (if not already done)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 6: Generate New Secret Key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Update in `.env`:
```env
SECRET_KEY=[generated-key]
```

### Step 7: Test and Run

```bash
# Test connection
python data_supabase.py

# Run application
python app.py
```

**Done!** You have a fresh installation with a new database.

---

## Scenario 3: New Supabase Account (With Data)

Use this when you want to migrate your existing data to a new Supabase account.

### Step 1: Export Data from Old Database

#### Option A: Using Supabase Dashboard

1. Go to your old Supabase project
2. Navigate to **Table Editor**
3. For each table, click **"•••"** > **"Download as CSV"**
4. Save CSV files for:
   - users
   - patients
   - medical_staff
   - appointments
   - medical_records

#### Option B: Using SQL Export

Run this in your old Supabase SQL Editor:

```sql
-- Export users
COPY (SELECT * FROM users) TO STDOUT WITH CSV HEADER;

-- Export patients
COPY (SELECT * FROM patients) TO STDOUT WITH CSV HEADER;

-- Export medical_staff
COPY (SELECT * FROM medical_staff) TO STDOUT WITH CSV HEADER;

-- Export appointments
COPY (SELECT * FROM appointments) TO STDOUT WITH CSV HEADER;

-- Export medical_records
COPY (SELECT * FROM medical_records) TO STDOUT WITH CSV HEADER;
```

Save each output to a separate CSV file.

### Step 2: Create New Supabase Project

Follow **Scenario 2, Steps 1-2** to create a new project and run schema scripts.

### Step 3: Import Data to New Database

#### Option A: Using Supabase Dashboard

1. Go to **Table Editor** in new project
2. Select table (e.g., users)
3. Click **"Insert"** > **"Import data from CSV"**
4. Upload the CSV file
5. Map columns if needed
6. Click **"Import"**

Repeat for all tables in this order:
1. users (must be first - it's the parent table)
2. patients
3. medical_staff
4. appointments
5. medical_records

#### Option B: Using SQL Import

In the new Supabase SQL Editor:

```sql
-- Import users (adjust file path as needed)
COPY users FROM '/path/to/users.csv' WITH CSV HEADER;

-- Import patients
COPY patients FROM '/path/to/patients.csv' WITH CSV HEADER;

-- Import medical_staff
COPY medical_staff FROM '/path/to/medical_staff.csv' WITH CSV HEADER;

-- Import appointments
COPY appointments FROM '/path/to/appointments.csv' WITH CSV HEADER;

-- Import medical_records
COPY medical_records FROM '/path/to/medical_records.csv' WITH CSV HEADER;
```

### Step 4: Verify Data Import

```sql
-- Check row counts
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'patients', COUNT(*) FROM patients
UNION ALL
SELECT 'medical_staff', COUNT(*) FROM medical_staff
UNION ALL
SELECT 'appointments', COUNT(*) FROM appointments
UNION ALL
SELECT 'medical_records', COUNT(*) FROM medical_records;
```

Compare counts with your old database.

### Step 5: Update Application Configuration

Follow **Scenario 2, Steps 3-7** to update `.env` and test.

**Done!** Your data has been migrated to the new database.

---

## Scenario 4: Server Deployment

Use this when deploying to a production server (VPS, AWS, DigitalOcean, etc.).

### Step 1: Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y  # Ubuntu/Debian

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv git -y
```

### Step 2: Clone Project

```bash
# Create directory
mkdir -p /var/www
cd /var/www

# Clone repository
git clone <your-repository-url> healthcare-portal
cd healthcare-portal
```

### Step 3: Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Configure for Production

Create production `.env`:

```bash
nano .env
```

Add production configuration:

```env
# Flask
FLASK_ENV=production
FLASK_DEBUG=False

# Security (generate new secret key!)
SECRET_KEY=<generate-new-strong-key>
SESSION_COOKIE_SECURE=True

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

# Sessions
SESSION_TIMEOUT_HOURS=2

# Password Policy (stricter for production)
PASSWORD_MIN_LENGTH=12
PASSWORD_REQUIRE_SPECIAL=True
```

### Step 5: Set Up Gunicorn

Install Gunicorn:
```bash
pip install gunicorn
```

Create systemd service:
```bash
sudo nano /etc/systemd/system/healthcare-portal.service
```

Add content:
```ini
[Unit]
Description=Healthcare Portal Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/healthcare-portal
Environment="PATH=/var/www/healthcare-portal/venv/bin"
ExecStart=/var/www/healthcare-portal/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app

[Install]
WantedBy=multi-user.target
```

### Step 6: Set Up Nginx (Reverse Proxy)

Install Nginx:
```bash
sudo apt install nginx -y
```

Create Nginx configuration:
```bash
sudo nano /etc/nginx/sites-available/healthcare-portal
```

Add content:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/healthcare-portal/static;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/healthcare-portal /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 7: Set Up SSL (Optional but Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### Step 8: Start Application

```bash
# Start service
sudo systemctl start healthcare-portal

# Enable on boot
sudo systemctl enable healthcare-portal

# Check status
sudo systemctl status healthcare-portal
```

### Step 9: Set Up Firewall

```bash
# Allow Nginx
sudo ufw allow 'Nginx Full'

# Enable firewall
sudo ufw enable
```

**Done!** Your application is now running on the server.

---

## Verification Steps

### 1. Test Database Connection

```bash
python data_supabase.py
```

Expected: "Successfully connected to Supabase database!"

### 2. Test Admin Login

1. Open application in browser
2. Login with username: `admin`, password: `admin123`
3. Verify you can access admin dashboard

### 3. Test User Creation

1. As admin, create a test user
2. Logout
3. Login with new user credentials
4. Verify correct dashboard appears

### 4. Test Data Access

1. Create test appointment
2. Create test medical record
3. Verify data appears correctly
4. Check audit logs (admin only)

### 5. Check Error Pages

Visit:
- `/nonexistent-page` (should show 404)
- Login with wrong password 6 times (should show lockout)

---

## Troubleshooting

### Issue: "Module not found" errors

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Supabase connection failed"

**Solution**:
1. Verify `SUPABASE_URL` and `SUPABASE_ANON_KEY` in `.env`
2. Check project is not paused in Supabase dashboard
3. Test credentials in Supabase dashboard
4. Ensure internet connection is working

### Issue: "Admin user not found"

**Solution**:
```bash
# Run create_admin.sql in Supabase SQL Editor
# Or create manually via application registration
```

### Issue: "Permission denied" on server

**Solution**:
```bash
# Fix file permissions
sudo chown -R www-data:www-data /var/www/healthcare-portal
sudo chmod -R 755 /var/www/healthcare-portal
```

### Issue: Application not starting on server

**Solution**:
```bash
# Check service logs
sudo journalctl -u healthcare-portal -f

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Check application is bound correctly
sudo netstat -tulpn | grep 8000
```

### Issue: Data import failed

**Solution**:
1. Check CSV format matches table structure
2. Ensure foreign key references exist (import users first)
3. Check for duplicate keys
4. Import tables in correct order

### Issue: Sessions not persisting

**Solution**:
1. Check `SECRET_KEY` is set in `.env`
2. Verify `SESSION_COOKIE_SECURE` matches HTTPS status
3. Clear browser cookies and try again

---

## Rollback Plan

If migration fails and you need to rollback:

### Rollback to Old System

1. Keep old `.env` file as backup
2. Don't delete old Supabase project until verified
3. Can switch back by updating `.env` with old credentials

### Database Rollback

Supabase provides automatic backups:
1. Go to **Database** > **Backups**
2. Select restore point
3. Click **"Restore"**

### Application Rollback

```bash
# If using Git
git log  # Find last working commit
git checkout <commit-hash>

# Reinstall dependencies
pip install -r requirements.txt
```

---

## Best Practices

### Before Migration

- [ ] Backup all data
- [ ] Document current configuration
- [ ] Test migration in development first
- [ ] Create checklist of all steps
- [ ] Schedule maintenance window

### During Migration

- [ ] Keep old system running until verified
- [ ] Test each step before proceeding
- [ ] Document any issues encountered
- [ ] Keep backup of `.env` files

### After Migration

- [ ] Verify all functionality works
- [ ] Test with real users
- [ ] Monitor logs for errors
- [ ] Update documentation
- [ ] Decommission old system only after verification

---

## Additional Resources

- [SUPABASE_SETUP.md](SUPABASE_SETUP.md) - Detailed Supabase setup
- [CONFIGURATION.md](CONFIGURATION.md) - Configuration options
- [README.md](README.md) - General documentation
- [Supabase CLI Guide](https://supabase.com/docs/guides/cli)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/latest/deploying/)

---

## Support

If you need help with migration:

1. Check this guide thoroughly
2. Review error messages in logs
3. Test in development environment first
4. Check Supabase dashboard for database issues
5. Verify all environment variables are correct
