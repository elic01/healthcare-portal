# Configuration Guide

This document describes all configuration options available in the Healthcare Portal.

## Table of Contents

- [Environment Variables](#environment-variables)
- [Flask Configuration](#flask-configuration)
- [Security Configuration](#security-configuration)
- [Database Configuration](#database-configuration)
- [Session Configuration](#session-configuration)
- [Rate Limiting](#rate-limiting)
- [Logging Configuration](#logging-configuration)
- [Production Configuration](#production-configuration)

## Environment Variables

All configuration is managed through the `.env` file in the project root.

### Creating Your .env File

1. Copy the example (if available):
   ```bash
   cp .env.example .env
   ```

2. Or create a new `.env` file with the template below:

```env
# ======================================
# HEALTHCARE PORTAL
# Environment Configuration
# ======================================

# =====================================
# FLASK ENVIRONMENT
# =====================================
FLASK_ENV=development
FLASK_DEBUG=True

# =====================================
# APPLICATION SECURITY
# =====================================
SECRET_KEY=your-secret-key-change-this-in-production

# =====================================
# SUPABASE CONFIGURATION
# =====================================
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here

# =====================================
# DATABASE CONFIGURATION
# =====================================
DEV_DATABASE_URL=https://your-project.supabase.co
DATABASE_URL=https://your-project.supabase.co

# =====================================
# SESSION CONFIGURATION
# =====================================
SESSION_TIMEOUT_HOURS=8
SESSION_COOKIE_SECURE=False

# =====================================
# PASSWORD POLICY
# =====================================
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=True
PASSWORD_REQUIRE_LOWERCASE=True
PASSWORD_REQUIRE_NUMBERS=True
PASSWORD_REQUIRE_SPECIAL=False

# =====================================
# ACCOUNT SECURITY
# =====================================
MAX_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_DURATION=30

# =====================================
# RATE LIMITING
# =====================================
RATELIMIT_DEFAULT=100 per hour
RATELIMIT_STORAGE_URL=memory://
API_RATE_LIMIT=1000 per hour

# =====================================
# LOGGING CONFIGURATION
# =====================================
LOG_LEVEL=INFO
LOG_FILE=logs/pdms.log

# =====================================
# PAGINATION & UI
# =====================================
ITEMS_PER_PAGE=20

# =====================================
# CSRF PROTECTION
# =====================================
WTF_CSRF_ENABLED=True

# =====================================
# COMPANY INFORMATION
# =====================================
COMPANY_NAME=HealthTech Solutions
SUPPORT_EMAIL=support@healthtechsolutions.com

# =====================================
# API CONFIGURATION
# =====================================
API_VERSION=v1
```

## Flask Configuration

### FLASK_ENV

**Description**: Sets the Flask environment mode
**Values**: `development`, `production`, `testing`
**Default**: `development`
**Production**: `production`

```env
FLASK_ENV=development
```

**Development mode**:
- Enables debug toolbar
- Shows detailed error pages
- Auto-reloads on code changes

**Production mode**:
- Disables debug mode
- Shows generic error pages
- Optimized performance

### FLASK_DEBUG

**Description**: Enables/disables Flask debug mode
**Values**: `True`, `False`
**Default**: `True`
**Production**: `False`

```env
FLASK_DEBUG=False
```

**Warning**: Never enable debug mode in production!

## Security Configuration

### SECRET_KEY

**Description**: Secret key for session encryption and CSRF protection
**Type**: String
**Required**: Yes
**Default**: `dev-secret-key-change-in-production`

```env
SECRET_KEY=your-secret-key-change-this-in-production
```

**Generating a secure key**:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Important**:
- Must be kept secret
- Should be different for each environment
- Change immediately in production
- At least 32 characters recommended

### WTF_CSRF_ENABLED

**Description**: Enables CSRF protection on forms
**Values**: `True`, `False`
**Default**: `True`
**Production**: `True`

```env
WTF_CSRF_ENABLED=True
```

## Database Configuration

### SUPABASE_URL

**Description**: Your Supabase project URL
**Type**: URL
**Required**: Yes
**Format**: `https://[project-id].supabase.co`

```env
SUPABASE_URL=https://mmfsjnpxwlbhcfftjlse.supabase.co
```

**Where to find**:
1. Go to your Supabase dashboard
2. Click Settings > API
3. Copy "Project URL"

### SUPABASE_ANON_KEY

**Description**: Supabase anonymous/public API key
**Type**: JWT Token
**Required**: Yes
**Format**: Long JWT string starting with `eyJ...`

```env
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Where to find**:
1. Go to your Supabase dashboard
2. Click Settings > API
3. Copy "anon public" key under "Project API keys"

**Note**: This key is safe to expose in frontend applications.

### DATABASE_URL

**Description**: Database connection URL
**Type**: URL
**Default**: Same as `SUPABASE_URL`

```env
DATABASE_URL=https://your-project.supabase.co
```

### DEV_DATABASE_URL

**Description**: Development database URL
**Type**: URL
**Default**: Same as `SUPABASE_URL`

```env
DEV_DATABASE_URL=https://your-project.supabase.co
```

**Use case**: Separate database for development and testing

## Session Configuration

### SESSION_TIMEOUT_HOURS

**Description**: How long a user session lasts (in hours)
**Type**: Integer
**Default**: `8`
**Range**: `1` - `24`

```env
SESSION_TIMEOUT_HOURS=8
```

Converted to seconds internally:
- 8 hours = 28,800 seconds
- Session expires after inactivity

### SESSION_COOKIE_SECURE

**Description**: Require HTTPS for session cookies
**Values**: `True`, `False`
**Default**: `False`
**Production**: `True` (if using HTTPS)

```env
SESSION_COOKIE_SECURE=True
```

**Production**: Set to `True` when using HTTPS

## Password Policy

### PASSWORD_MIN_LENGTH

**Description**: Minimum password length
**Type**: Integer
**Default**: `8`
**Recommended**: `12-16` for production

```env
PASSWORD_MIN_LENGTH=8
```

### PASSWORD_REQUIRE_UPPERCASE

**Description**: Require at least one uppercase letter
**Values**: `True`, `False`
**Default**: `True`

```env
PASSWORD_REQUIRE_UPPERCASE=True
```

**Note**: Currently enforced at validation level

### PASSWORD_REQUIRE_LOWERCASE

**Description**: Require at least one lowercase letter
**Values**: `True`, `False`
**Default**: `True`

```env
PASSWORD_REQUIRE_LOWERCASE=True
```

### PASSWORD_REQUIRE_NUMBERS

**Description**: Require at least one number
**Values**: `True`, `False`
**Default**: `True`

```env
PASSWORD_REQUIRE_NUMBERS=True
```

### PASSWORD_REQUIRE_SPECIAL

**Description**: Require at least one special character
**Values**: `True`, `False`
**Default**: `False`

```env
PASSWORD_REQUIRE_SPECIAL=True
```

**Special characters**: `!@#$%^&*()_+-=[]{}|;:,.<>?`

## Account Security

### MAX_LOGIN_ATTEMPTS

**Description**: Maximum failed login attempts before lockout
**Type**: Integer
**Default**: `5`
**Recommended**: `3-5`

```env
MAX_LOGIN_ATTEMPTS=5
```

### ACCOUNT_LOCKOUT_DURATION

**Description**: Account lockout duration in minutes
**Type**: Integer
**Default**: `30`

```env
ACCOUNT_LOCKOUT_DURATION=30
```

## Rate Limiting

### RATELIMIT_DEFAULT

**Description**: Default rate limit for all routes
**Format**: `number per period`
**Default**: `100 per hour`

```env
RATELIMIT_DEFAULT=100 per hour
```

**Examples**:
- `100 per hour`
- `10 per minute`
- `1000 per day`

### RATELIMIT_STORAGE_URL

**Description**: Storage backend for rate limiting
**Values**: `memory://`, `redis://host:port`
**Default**: `memory://`

```env
RATELIMIT_STORAGE_URL=memory://
```

**Production**: Use Redis for distributed systems:
```env
RATELIMIT_STORAGE_URL=redis://localhost:6379
```

### API_RATE_LIMIT

**Description**: Rate limit for API endpoints
**Format**: `number per period`
**Default**: `1000 per hour`

```env
API_RATE_LIMIT=1000 per hour
```

## Logging Configuration

### LOG_LEVEL

**Description**: Logging level
**Values**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
**Default**: `INFO`
**Production**: `WARNING` or `ERROR`

```env
LOG_LEVEL=INFO
```

**Log Levels**:
- `DEBUG`: Detailed information for debugging
- `INFO`: General informational messages
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

### LOG_FILE

**Description**: Path to log file
**Type**: File path
**Default**: `logs/pdms.log`

```env
LOG_FILE=logs/pdms.log
```

**Note**: Make sure the directory exists or the app can create it.

## UI Configuration

### ITEMS_PER_PAGE

**Description**: Number of items per page in lists
**Type**: Integer
**Default**: `20`

```env
ITEMS_PER_PAGE=20
```

## Company Information

### COMPANY_NAME

**Description**: Company name displayed in the application
**Type**: String
**Default**: `HealthTech Solutions`

```env
COMPANY_NAME=Your Healthcare Provider
```

### SUPPORT_EMAIL

**Description**: Support email displayed to users
**Type**: Email
**Default**: `support@healthtechsolutions.com`

```env
SUPPORT_EMAIL=support@yourdomain.com
```

## API Configuration

### API_VERSION

**Description**: API version identifier
**Type**: String
**Default**: `v1`

```env
API_VERSION=v1
```

## Production Configuration

### Recommended Production Settings

```env
# Flask
FLASK_ENV=production
FLASK_DEBUG=False

# Security
SECRET_KEY=<generate-strong-random-key>
SESSION_COOKIE_SECURE=True
WTF_CSRF_ENABLED=True

# Password Policy
PASSWORD_MIN_LENGTH=12
PASSWORD_REQUIRE_UPPERCASE=True
PASSWORD_REQUIRE_LOWERCASE=True
PASSWORD_REQUIRE_NUMBERS=True
PASSWORD_REQUIRE_SPECIAL=True

# Account Security
MAX_LOGIN_ATTEMPTS=3
ACCOUNT_LOCKOUT_DURATION=60

# Logging
LOG_LEVEL=WARNING
LOG_FILE=/var/log/pdms/application.log

# Sessions
SESSION_TIMEOUT_HOURS=2
```

### Security Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `FLASK_ENV=production`
- [ ] Set `FLASK_DEBUG=False`
- [ ] Set `SESSION_COOKIE_SECURE=True` (with HTTPS)
- [ ] Change default admin password
- [ ] Enable stricter password policy
- [ ] Reduce `MAX_LOGIN_ATTEMPTS`
- [ ] Set appropriate `LOG_LEVEL`
- [ ] Use Redis for `RATELIMIT_STORAGE_URL` in distributed systems
- [ ] Configure proper backup strategy
- [ ] Enable Row Level Security in Supabase

## Environment-Specific Configuration

### Development

```env
FLASK_ENV=development
FLASK_DEBUG=True
SESSION_COOKIE_SECURE=False
LOG_LEVEL=DEBUG
```

### Staging

```env
FLASK_ENV=production
FLASK_DEBUG=False
SESSION_COOKIE_SECURE=True
LOG_LEVEL=INFO
```

### Production

```env
FLASK_ENV=production
FLASK_DEBUG=False
SESSION_COOKIE_SECURE=True
LOG_LEVEL=WARNING
```

## Verifying Configuration

### Check loaded configuration:

```python
python -c "
from dotenv import load_dotenv
import os

load_dotenv()

print('SUPABASE_URL:', os.getenv('SUPABASE_URL'))
print('FLASK_ENV:', os.getenv('FLASK_ENV'))
print('PASSWORD_MIN_LENGTH:', os.getenv('PASSWORD_MIN_LENGTH'))
"
```

### Test database connection:

```bash
python data_supabase.py
```

## Troubleshooting

### Issue: Configuration not loading

1. Check `.env` file exists in project root
2. Verify no syntax errors in `.env`
3. Ensure `python-dotenv` is installed
4. Try loading manually:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

### Issue: Invalid Supabase credentials

1. Verify `SUPABASE_URL` format
2. Check `SUPABASE_ANON_KEY` is complete
3. Test in Supabase dashboard
4. Ensure project is not paused

### Issue: Session timeout not working

1. Verify `SESSION_TIMEOUT_HOURS` is set
2. Check that sessions are properly initialized
3. Clear browser cookies and test again

## Additional Resources

- [Flask Configuration Documentation](https://flask.palletsprojects.com/en/latest/config/)
- [Supabase Documentation](https://supabase.com/docs)
- [Python dotenv Documentation](https://github.com/theskumar/python-dotenv)
