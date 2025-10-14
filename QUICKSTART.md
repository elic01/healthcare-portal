# Quick Start Guide

Get the Healthcare Portal up and running in 10 minutes!

## Prerequisites

- Python 3.8 or higher installed
- Internet connection
- A text editor

## Step-by-Step Setup

### 1. Get a Supabase Account (3 minutes)

1. Go to [https://supabase.com](https://supabase.com)
2. Click **"Start your project"** and sign up (free!)
3. Click **"New Project"**
4. Fill in:
   - **Name**: `healthcare-portal`
   - **Database Password**: Create a strong password (SAVE THIS!)
   - **Region**: Choose closest to you
5. Click **"Create new project"**
6. Wait 2-3 minutes for setup to complete

### 2. Set Up Database (2 minutes)

1. In your Supabase dashboard, click **"SQL Editor"** in the left sidebar
2. Click **"New Query"**

3. **Run Schema Script**:
   - Open the file `sql/supabase_schema.sql` from this project
   - Copy ALL the contents
   - Paste into the SQL Editor
   - Click **"Run"** (or press Ctrl+Enter)
   - Wait for "Success" message

4. **Create Admin User**:
   - Click **"New Query"** again
   - Open the file `sql/create_admin.sql`
   - Copy and paste contents
   - Click **"Run"**
   - You should see the admin user created

### 3. Get Your Credentials (1 minute)

1. In Supabase, click **"Settings"** (gear icon at bottom left)
2. Click **"API"** in the settings menu
3. Copy these two values:
   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **anon public key** (long string starting with `eyJ...`)

### 4. Install Application (2 minutes)

Open your terminal/command prompt:

```bash
# Navigate to the project folder
cd healthcare-portal

# Create virtual environment
python3 -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Configure Application (1 minute)

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` in a text editor

3. Update these lines with your Supabase credentials:
   ```env
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

4. Save the file

### 6. Run the Application (30 seconds)

```bash
python app.py
```

You should see:
```
✅ Connected to Supabase database
 * Running on http://127.0.0.1:5000
```

### 7. Access the Application (30 seconds)

1. Open your web browser
2. Go to: `http://localhost:5000`
3. Click **"Login"**
4. Use these credentials:
   - **Username**: `admin`
   - **Password**: `admin123`

**SUCCESS!** You should now see the Administrator Dashboard.

## What's Next?

### Change Admin Password (Recommended)

1. Click your name in the top right
2. Select **"Profile"**
3. Change your password
4. Save

### Create Users

1. Go to **"Manage Users"** (admin only)
2. Click **"Add New User"**
3. Fill in details:
   - Username
   - Password
   - Role (Patient, Nurse, Doctor, or Administrator)
   - Other information
4. Click **"Create User"**

### Explore Features

**As Administrator**:
- View system statistics on dashboard
- Manage all users
- View audit logs
- Manage medical staff

**As Doctor** (create a doctor user to test):
- View assigned patients
- Create medical records
- Manage appointments
- Add prescriptions

**As Patient** (create a patient user to test):
- View your medical records
- Book appointments
- View appointment history
- Update your profile

## Testing the System

### Create a Complete Workflow

1. **As Admin**: Create a doctor user and a patient user

2. **Logout and login as the patient**:
   - Go to "Book Appointment"
   - Select the doctor
   - Choose date and time
   - Add reason for visit
   - Submit

3. **Logout and login as the doctor**:
   - View the appointment on dashboard
   - Go to "Medical Records"
   - Create a new record for the patient
   - Add diagnosis, treatment, prescription
   - Save

4. **Logout and login as the patient**:
   - View your new medical record
   - See the prescription
   - Check your appointment status

## Troubleshooting

### "Database connection error"
- Check your `.env` file has correct SUPABASE_URL and SUPABASE_ANON_KEY
- Verify your Supabase project is active (not paused)
- Check your internet connection

### "Invalid username or password"
- Make sure you ran the `create_admin.sql` script
- Default credentials are: username=`admin`, password=`admin123`
- Try resetting by running `create_admin.sql` again

### "Module not found" errors
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

### Port 5000 already in use
```bash
# On Linux/Mac:
lsof -ti:5000 | xargs kill -9

# On Windows:
netstat -ano | findstr :5000
# Then kill the process: taskkill /PID <pid> /F
```

### Application not starting
- Check Python version: `python --version` (should be 3.8+)
- Check if virtual environment is activated (should see `(venv)` in prompt)
- Check for errors in terminal output

## Common Tasks

### Stop the Application
Press `Ctrl+C` in the terminal

### Restart the Application
```bash
python app.py
```

### Deactivate Virtual Environment
```bash
deactivate
```

### View Database in Supabase
1. Go to your Supabase dashboard
2. Click **"Table Editor"**
3. Select a table (users, appointments, etc.)
4. View/edit data directly

### Run SQL Queries
1. Go to **"SQL Editor"** in Supabase
2. Write your query
3. Click **"Run"**

Example queries:
```sql
-- View all users
SELECT username, role, email FROM users;

-- View all appointments
SELECT * FROM appointments;

-- Count users by role
SELECT role, COUNT(*) FROM users GROUP BY role;
```

## Need More Help?

- **Full documentation**: See [README.md](README.md)
- **Database setup**: See [SUPABASE_SETUP.md](SUPABASE_SETUP.md)
- **Configuration options**: See [CONFIGURATION.md](CONFIGURATION.md)
- **Moving to another PC**: See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
- **Architecture details**: See [ARCHITECTURE.md](ARCHITECTURE.md)

## Default Credentials

**Admin Account**:
- Username: `admin`
- Password: `admin123`

**IMPORTANT**: Change this password immediately after first login!

## Project Structure Overview

```
healthcare-portal/
├── app.py                 # Main application
├── data_supabase.py       # CLI tool
├── requirements.txt       # Dependencies
├── .env                   # Your configuration (create from .env.example)
├── sql/                   # Database scripts
│   ├── supabase_schema.sql
│   └── create_admin.sql
├── templates/             # HTML pages
└── static/               # CSS, JS, images
```

## Quick Commands Reference

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Run application
python app.py

# Run CLI tool
python data_supabase.py

# Install dependencies
pip install -r requirements.txt

# Deactivate virtual environment
deactivate
```

## Success Checklist

- [ ] Supabase account created
- [ ] Database schema created (ran supabase_schema.sql)
- [ ] Admin user created (ran create_admin.sql)
- [ ] Got Supabase URL and anon key
- [ ] Created .env file with credentials
- [ ] Installed Python dependencies
- [ ] Application starts without errors
- [ ] Can login with admin credentials
- [ ] Can access administrator dashboard

## You're All Set!

Congratulations! Your Patient Data Management System is now running.

For production deployment or advanced configuration, check out the other documentation files.

Happy healthcare managing! 🏥
