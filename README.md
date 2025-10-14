# Healthcare Portal

A comprehensive healthcare management web application built with Flask and Supabase, featuring role-based access control for patients, nurses, doctors, and administrators.

## Quick Links

- **New to Healthcare Portal?** Start with [QUICKSTART.md](QUICKSTART.md) - Get running in 10 minutes!
- **Setting up database?** See [SUPABASE_SETUP.md](SUPABASE_SETUP.md)
- **Migrating to new PC?** See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
- **Configuration help?** See [CONFIGURATION.md](CONFIGURATION.md)
- **Understanding the system?** See [ARCHITECTURE.md](ARCHITECTURE.md)

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Database Setup](#database-setup)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [User Roles](#user-roles)
- [Project Structure](#project-structure)
- [Security Features](#security-features)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)

## Features

### Patient Features
- View personal medical records
- Book and manage appointments
- View appointment history
- Update personal profile information
- View assigned doctors

### Nurse Features
- View patient lists
- Access patient medical records
- Manage appointments
- Update patient information
- Create medical records

### Doctor Features
- View assigned patients
- Access and update medical records
- Manage appointments
- Add diagnoses and prescriptions
- View patient medical history

### Administrator Features
- Manage all users (patients, doctors, nurses)
- View system-wide statistics
- Access audit logs
- Manage medical staff
- System configuration

## Technology Stack

### Backend
- **Flask 2.3.3** - Python web framework
- **Supabase** - PostgreSQL database and backend services
- **Flask-Login** - User session management
- **Flask-WTF** - Form handling and CSRF protection
- **Werkzeug** - Password hashing utilities

### Frontend
- **HTML5/CSS3** - Structure and styling
- **Bootstrap 5** - Responsive UI framework
- **JavaScript** - Client-side interactivity

### Security
- **SHA-256** - Password hashing
- **CSRF Protection** - Form security
- **Session Management** - Secure user sessions
- **Audit Logging** - Action tracking

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Supabase account (free tier available)
- Git (for cloning the repository)

## Installation

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd healthcare-portal
```

### 2. Create Virtual Environment

```bash
# On Linux/macOS
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Database Setup

See [SUPABASE_SETUP.md](SUPABASE_SETUP.md) for detailed instructions on setting up your Supabase database.

Quick setup:
1. Create a Supabase account at https://supabase.com
2. Create a new project
3. Run the SQL scripts in the SQL Editor:
   - `sql/supabase_schema.sql` - Creates all tables and indexes
   - `sql/create_admin.sql` - Creates the default admin user
4. Copy your project URL and anon key to `.env`

## Configuration

### 1. Environment Variables

Copy the `.env.example` file to `.env` and update the values:

```bash
cp .env.example .env
```

Update the following required variables in `.env`:

```env
# Supabase Configuration (REQUIRED)
SUPABASE_URL=your-project-url-here
SUPABASE_ANON_KEY=your-anon-key-here

# Flask Security (REQUIRED - Change in production)
SECRET_KEY=your-secret-key-change-this-in-production
```

See [CONFIGURATION.md](CONFIGURATION.md) for detailed configuration options.

### 2. Default Admin Account

After running the database setup, you can login with:
- **Username**: `admin`
- **Password**: `admin123`

**IMPORTANT**: Change this password immediately after first login!

## Running the Application

### Development Mode

```bash
# Activate virtual environment
source venv/bin/activate  # On Linux/macOS
# or
venv\Scripts\activate     # On Windows

# Run the application
python app.py
```

The application will be available at `http://localhost:5000`

### Production Mode

For production deployment:

1. Set environment variables:
```env
FLASK_ENV=production
FLASK_DEBUG=False
SESSION_COOKIE_SECURE=True
SECRET_KEY=<generate-strong-random-key>
```

2. Use a production WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## User Roles

| Role | Access Level | Permissions |
|------|-------------|-------------|
| **Patient** | Basic | View own records, book appointments, manage profile |
| **Nurse** | Intermediate | View patients, manage appointments, update records |
| **Doctor** | Advanced | Full medical record access, diagnoses, prescriptions |
| **Administrator** | Full | Complete system access, user management, audit logs |

## Project Structure

```
healthcare-portal/
├── app.py                      # Main Flask application
├── data_supabase.py           # CLI data management tool
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Project configuration
├── .env                      # Environment variables (create from .env.example)
│
├── static/                   # Static assets
│   ├── css/                 # Stylesheets
│   └── js/                  # JavaScript files
│
├── templates/               # HTML templates
│   ├── base.html           # Base template
│   ├── index.html          # Home page
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── profile.html        # User profile
│   ├── admin/              # Admin templates
│   ├── doctor/             # Doctor templates
│   ├── nurse/              # Nurse templates
│   ├── patient/            # Patient templates
│   ├── appointments/       # Appointment templates
│   ├── medical_records/    # Medical record templates
│   ├── patients/           # Patient management templates
│   └── errors/             # Error pages
│
└── sql/                    # SQL scripts
    ├── supabase_schema.sql        # Main schema
    ├── create_admin.sql           # Admin user creation
    └── add_missing_columns.sql    # Schema updates
```

## Security Features

### Password Security
- Minimum length: 8 characters
- Must contain letters and numbers
- SHA-256 hashing
- Password strength validation

### Session Security
- Configurable session timeout (default: 8 hours)
- Secure session cookies in production
- CSRF protection on all forms
- Session invalidation on logout

### Access Control
- Role-based access control (RBAC)
- Route-level authentication checks
- User-specific data filtering
- Audit logging for all actions

### Rate Limiting
- Login attempt limiting (default: 5 attempts)
- Account lockout on failed attempts
- API rate limiting (1000 requests/hour)

## Troubleshooting

### Database Connection Errors

**Error**: "Supabase URL and ANON_KEY must be set"
- Check that `.env` file exists and contains valid `SUPABASE_URL` and `SUPABASE_ANON_KEY`

### Login Issues

**Error**: "Invalid username or password"
- Verify the admin user was created with `create_admin.sql`
- Default credentials: username=`admin`, password=`admin123`

**Error**: "User not found"
- Check the users table in Supabase dashboard
- Run `create_admin.sql` to create the default admin user

### Missing Columns

**Error**: Column not found in database
- Run `add_missing_columns.sql` to update the schema
- This adds any missing columns to existing tables

### Port Already in Use

**Error**: "Address already in use"
```bash
# Find and kill the process using port 5000
# On Linux/macOS
lsof -ti:5000 | xargs kill -9

# On Windows
netstat -ano | findstr :5000
taskkill /PID <process_id> /F
```

## Documentation

### Complete Documentation Index

| Document | Description | When to Use |
|----------|-------------|-------------|
| [QUICKSTART.md](QUICKSTART.md) | Get started in 10 minutes | First time setup |
| [README.md](README.md) | Project overview and basics | General reference |
| [SUPABASE_SETUP.md](SUPABASE_SETUP.md) | Detailed database setup | Setting up Supabase |
| [CONFIGURATION.md](CONFIGURATION.md) | All configuration options | Customizing settings |
| [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) | Database structure | Understanding data model |
| [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) | Moving to new PC/server | Migrating or deploying |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture | Understanding how it works |

### Quick Reference

**Starting Out**:

1. [QUICKSTART.md](QUICKSTART.md) - Set up everything
2. [README.md](README.md) - Understand features
3. [ARCHITECTURE.md](ARCHITECTURE.md) - Learn the system

**Daily Operations**:

- [CONFIGURATION.md](CONFIGURATION.md) - Change settings
- [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) - Work with data

**Advanced Tasks**:

- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Deploy or migrate
- [SUPABASE_SETUP.md](SUPABASE_SETUP.md) - Recreate database

## Support

For issues and questions:
- Email: support@healthtechsolutions.com
- Check the documentation files above
- Review the troubleshooting section

## License

This project is developed for educational and healthcare management purposes.

## Version

Current Version: 2.0.0
