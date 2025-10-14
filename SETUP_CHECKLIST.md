# Setup Checklist

Use this checklist to ensure you've completed all steps for setting up the Patient Data Management System.

## Pre-Installation Checklist

### Requirements Verification

- [ ] Python 3.8 or higher installed
  ```bash
  python3 --version
  # Should show: Python 3.8.x or higher
  ```

- [ ] pip package manager available
  ```bash
  pip --version
  # Should show pip version
  ```

- [ ] Internet connection active
  ```bash
  ping -c 1 google.com  # Linux/Mac
  ping google.com       # Windows
  ```

- [ ] Text editor available (VS Code, Sublime, nano, etc.)

- [ ] Web browser installed

---

## Supabase Setup Checklist

### Account Creation

- [ ] Visited [https://supabase.com](https://supabase.com)
- [ ] Created account (GitHub/Google/Email)
- [ ] Verified email (if required)
- [ ] Successfully logged in

### Project Creation

- [ ] Clicked "New Project"
- [ ] Entered project name: `healthcare-portal`
- [ ] Created and saved database password
- [ ] Selected closest region
- [ ] Clicked "Create new project"
- [ ] Waited for provisioning to complete (2-3 minutes)
- [ ] Project dashboard is visible

### Database Setup

- [ ] Opened SQL Editor in Supabase
- [ ] Created new query
- [ ] Copied contents of `sql/supabase_schema.sql`
- [ ] Pasted into SQL Editor
- [ ] Executed query successfully (saw "Success" message)
- [ ] Created another new query
- [ ] Copied contents of `sql/create_admin.sql`
- [ ] Pasted and executed successfully
- [ ] Verified admin user created

### Credentials Collection

- [ ] Navigated to Settings > API
- [ ] Copied Project URL (format: `https://xxxxx.supabase.co`)
- [ ] Saved Project URL securely
- [ ] Copied anon public key (starts with `eyJ...`)
- [ ] Saved anon key securely

### Database Verification

- [ ] Opened Table Editor in Supabase
- [ ] Verified these tables exist:
  - [ ] users
  - [ ] patients
  - [ ] medical_staff
  - [ ] appointments
  - [ ] medical_records
  - [ ] audit_logs
- [ ] Checked users table has admin user
- [ ] No errors in Supabase dashboard

---

## Application Installation Checklist

### Project Setup

- [ ] Opened terminal/command prompt
- [ ] Navigated to project directory
  ```bash
  cd /path/to/healthcare-portal
  ```
- [ ] Verified project files exist
  ```bash
  ls -la  # Linux/Mac
  dir     # Windows
  ```

### Virtual Environment

- [ ] Created virtual environment
  ```bash
  python3 -m venv venv  # Linux/Mac
  python -m venv venv   # Windows
  ```
- [ ] Verified venv folder created
- [ ] Activated virtual environment
  ```bash
  source venv/bin/activate      # Linux/Mac
  venv\Scripts\activate         # Windows
  ```
- [ ] See `(venv)` in terminal prompt

### Dependencies Installation

- [ ] Installed requirements
  ```bash
  pip install -r requirements.txt
  ```
- [ ] Installation completed without errors
- [ ] All packages installed successfully

### Package Verification

- [ ] Verify Flask installed
  ```bash
  python -c "import flask; print(flask.__version__)"
  ```
- [ ] Verify Supabase client installed
  ```bash
  python -c "import supabase; print('OK')"
  ```

---

## Configuration Checklist

### Environment File

- [ ] Located `.env.example` file
- [ ] Copied to `.env`
  ```bash
  cp .env.example .env  # Linux/Mac
  copy .env.example .env  # Windows
  ```
- [ ] Verified `.env` file created
- [ ] Opened `.env` in text editor

### Supabase Configuration

- [ ] Updated `SUPABASE_URL` with your Project URL
- [ ] Updated `SUPABASE_ANON_KEY` with your anon key
- [ ] Updated `DEV_DATABASE_URL` (usually same as SUPABASE_URL)
- [ ] Updated `DATABASE_URL` (usually same as SUPABASE_URL)
- [ ] Saved `.env` file

### Security Configuration

- [ ] Generated new SECRET_KEY
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- [ ] Updated `SECRET_KEY` in `.env`
- [ ] Verified no spaces or quotes around values
- [ ] Saved `.env` file

### Configuration Verification

- [ ] `.env` file has no syntax errors
- [ ] All required fields have values
- [ ] No placeholder text remains
- [ ] File saved successfully

---

## First Run Checklist

### Starting Application

- [ ] Virtual environment is activated (see `(venv)`)
- [ ] In project root directory
- [ ] Started application
  ```bash
  python app.py
  ```
- [ ] Saw "Connected to Supabase database" message
- [ ] Saw "Running on http://127.0.0.1:5000"
- [ ] No errors in terminal

### Accessing Application

- [ ] Opened web browser
- [ ] Navigated to `http://localhost:5000`
- [ ] Homepage loaded successfully
- [ ] No error messages displayed

### First Login

- [ ] Clicked "Login" button/link
- [ ] Login page loaded
- [ ] Entered username: `admin`
- [ ] Entered password: `admin123`
- [ ] Clicked login button
- [ ] Successfully logged in
- [ ] Redirected to Administrator Dashboard
- [ ] Dashboard shows statistics

---

## Post-Installation Checklist

### Security Setup

- [ ] Logged in as admin
- [ ] Clicked profile/username
- [ ] Selected "Profile" or "Change Password"
- [ ] Changed admin password
- [ ] Logged out
- [ ] Logged in with new password
- [ ] Login successful

### User Creation Test

- [ ] Logged in as admin
- [ ] Navigated to "Manage Users" or "Users"
- [ ] Clicked "Add User" or "Create User"
- [ ] Created test patient user:
  - [ ] Entered username
  - [ ] Entered password
  - [ ] Selected role: Patient
  - [ ] Filled in name, email
  - [ ] Submitted form
- [ ] User created successfully
- [ ] User appears in users list

### User Login Test

- [ ] Logged out as admin
- [ ] Logged in as test patient user
- [ ] Patient dashboard displayed
- [ ] Can navigate menu items
- [ ] Logged out successfully

### Feature Testing

#### Appointment Booking

- [ ] Logged in as patient
- [ ] Found "Book Appointment" option
- [ ] Created test doctor user (if needed)
- [ ] Booked appointment with doctor
- [ ] Appointment created successfully
- [ ] Appointment appears in list

#### Medical Records (Doctor)

- [ ] Created doctor user (if not exists)
- [ ] Logged in as doctor
- [ ] Accessed "Medical Records" section
- [ ] Created test medical record
- [ ] Record saved successfully

#### Admin Functions

- [ ] Logged in as admin
- [ ] Viewed user list
- [ ] Viewed statistics
- [ ] Checked audit logs
- [ ] All functions working

---

## Verification Checklist

### Database Verification

In Supabase dashboard:

- [ ] Table Editor shows data
- [ ] Users table has entries
- [ ] Appointments table has test data
- [ ] Audit logs show activity
- [ ] No errors in logs

### Application Verification

- [ ] All pages load without errors
- [ ] Forms submit successfully
- [ ] Data persists after refresh
- [ ] Logout works correctly
- [ ] Login redirects work properly

### Error Testing

- [ ] Tried invalid login - shows error
- [ ] Tried accessing protected page without login - redirected
- [ ] Invalid form data - shows validation errors
- [ ] 404 page works for invalid URLs

---

## Production Deployment Checklist

(Only if deploying to production)

### Production Configuration

- [ ] Set `FLASK_ENV=production` in `.env`
- [ ] Set `FLASK_DEBUG=False` in `.env`
- [ ] Generated new `SECRET_KEY` for production
- [ ] Set `SESSION_COOKIE_SECURE=True` (if using HTTPS)
- [ ] Updated password requirements (stronger)
- [ ] Reduced `MAX_LOGIN_ATTEMPTS`
- [ ] Set appropriate `LOG_LEVEL`

### Server Setup

- [ ] Server OS updated
- [ ] Python 3.8+ installed on server
- [ ] Nginx installed (or other web server)
- [ ] SSL certificate obtained (Let's Encrypt)
- [ ] Firewall configured
- [ ] Project files uploaded to server

### Application Deployment

- [ ] Virtual environment created on server
- [ ] Dependencies installed
- [ ] `.env` file configured for production
- [ ] Gunicorn installed
- [ ] Systemd service created
- [ ] Nginx configured as reverse proxy
- [ ] Application started
- [ ] Application accessible via domain

### Production Verification

- [ ] HTTPS working
- [ ] Application loads
- [ ] Can login
- [ ] All features working
- [ ] Logs being written
- [ ] Automatic restart on failure
- [ ] Backup strategy in place

---

## Troubleshooting Reference

### If Database Connection Fails

1. [ ] Check `.env` has correct SUPABASE_URL
2. [ ] Check `.env` has correct SUPABASE_ANON_KEY
3. [ ] Verify Supabase project is not paused
4. [ ] Check internet connection
5. [ ] Verify no typos in credentials

### If Can't Login

1. [ ] Verify admin user exists in Supabase Table Editor
2. [ ] Check username is exactly `admin`
3. [ ] Check password is exactly `admin123` (initially)
4. [ ] Run `sql/create_admin.sql` again if needed
5. [ ] Check application logs for errors

### If Modules Not Found

1. [ ] Verify virtual environment is activated
2. [ ] Run `pip install -r requirements.txt` again
3. [ ] Check Python version is 3.8+
4. [ ] Try creating new virtual environment

### If Port Already in Use

```bash
# Linux/Mac
lsof -ti:5000 | xargs kill -9

# Windows
netstat -ano | findstr :5000
taskkill /PID <pid> /F
```

---

## Documentation Checklist

### Documentation Read

- [ ] Read [QUICKSTART.md](QUICKSTART.md)
- [ ] Skimmed [README.md](README.md)
- [ ] Bookmarked [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
- [ ] Know where to find [CONFIGURATION.md](CONFIGURATION.md)
- [ ] Know where to find [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)

### Documentation Accessibility

- [ ] All `.md` files accessible
- [ ] SQL files in `sql/` folder
- [ ] `.env.example` available as template

---

## Completion Status

### Essential Tasks

- [ ] Supabase account created ✅
- [ ] Database schema created ✅
- [ ] Application installed ✅
- [ ] Configuration completed ✅
- [ ] First login successful ✅
- [ ] Admin password changed ✅

### Recommended Tasks

- [ ] Test user created
- [ ] Features tested
- [ ] Documentation reviewed
- [ ] Backup strategy planned

### Optional Tasks

- [ ] Production deployment completed
- [ ] SSL certificate installed
- [ ] Monitoring set up
- [ ] Custom configuration applied

---

## Sign-Off

**Setup Completed By**: ___________________

**Date**: ___________________

**Application Version**: 2.0.0

**Environment**: ☐ Development  ☐ Production  ☐ Testing

**Notes**:
```
[Add any notes about your specific setup here]
```

---

## Next Steps

After completing this checklist:

1. **Development**: Start building features or customizing
2. **Production**: Deploy to production server
3. **Training**: Train users on the system
4. **Documentation**: Review specific docs as needed

---

## Quick Reference

**Start Application**:
```bash
cd /path/to/healthcare-portal
source venv/bin/activate  # or venv\Scripts\activate
python app.py
```

**Access Application**:
```
http://localhost:5000
```

**Default Credentials**:
- Username: `admin`
- Password: `admin123` (change immediately!)

**Stop Application**:
Press `Ctrl+C` in terminal

---

**Checklist Complete!** 🎉

If all items are checked, your Patient Data Management System is fully set up and ready to use!
