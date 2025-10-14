# System Architecture Documentation

This document provides a comprehensive overview of the Healthcare Portal architecture.

## Table of Contents

- [System Overview](#system-overview)
- [Architecture Diagram](#architecture-diagram)
- [Technology Stack](#technology-stack)
- [Application Structure](#application-structure)
- [Security Architecture](#security-architecture)
- [Database Design](#database-design)
- [Authentication & Authorization](#authentication--authorization)
- [API Endpoints](#api-endpoints)
- [Frontend Architecture](#frontend-architecture)
- [Deployment Architecture](#deployment-architecture)

## System Overview

The Healthcare Portal is a comprehensive healthcare management web application designed to facilitate interactions between patients, medical staff, and administrators.

### Key Features

**Patient Management**
- Patient registration and profile management
- Medical history tracking
- Appointment scheduling
- View medical records and prescriptions

**Medical Staff Features**
- Doctor and nurse management
- Patient care documentation
- Appointment management
- Medical record creation and updates

**Administrative Functions**
- User management (CRUD operations)
- System statistics and reporting
- Audit log monitoring
- Medical staff oversight

**Security & Compliance**
- Role-based access control (RBAC)
- Audit logging for compliance
- Session management
- Password policies
- CSRF protection

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                         │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │   Browser   │  │   Mobile     │  │   Desktop App    │   │
│  │  (HTML/CSS) │  │  (Future)    │  │   (Future)       │   │
│  └──────┬──────┘  └──────┬───────┘  └────────┬─────────┘   │
└─────────┼────────────────┼───────────────────┼──────────────┘
          │                │                   │
          └────────────────┴───────────────────┘
                           │ HTTP/HTTPS
          ┌────────────────▼────────────────┐
          │      REVERSE PROXY (Nginx)       │
          │  - SSL/TLS Termination          │
          │  - Load Balancing               │
          │  - Static File Serving          │
          └────────────────┬────────────────┘
                           │
          ┌────────────────▼────────────────┐
          │     APPLICATION LAYER (Flask)    │
          │  ┌──────────────────────────┐   │
          │  │   Flask Application      │   │
          │  │  ┌────────────────────┐  │   │
          │  │  │  Route Handlers    │  │   │
          │  │  │  - Login/Auth      │  │   │
          │  │  │  - Appointments    │  │   │
          │  │  │  - Medical Records │  │   │
          │  │  │  - User Management │  │   │
          │  │  └────────────────────┘  │   │
          │  │  ┌────────────────────┐  │   │
          │  │  │  Authentication    │  │   │
          │  │  │  - Flask-Login     │  │   │
          │  │  │  - Session Mgmt    │  │   │
          │  │  │  - RBAC            │  │   │
          │  │  └────────────────────┘  │   │
          │  │  ┌────────────────────┐  │   │
          │  │  │  Security Layer    │  │   │
          │  │  │  - CSRF Protection │  │   │
          │  │  │  - Rate Limiting   │  │   │
          │  │  │  - Input Validation│  │   │
          │  │  └────────────────────┘  │   │
          │  └──────────────────────────┘   │
          └────────────────┬────────────────┘
                           │
          ┌────────────────▼────────────────┐
          │      DATA ACCESS LAYER          │
          │  ┌──────────────────────────┐   │
          │  │   Supabase Client        │   │
          │  │   - Query Builder        │   │
          │  │   - Connection Pool      │   │
          │  │   - Error Handling       │   │
          │  └──────────────────────────┘   │
          └────────────────┬────────────────┘
                           │
          ┌────────────────▼────────────────┐
          │     DATABASE LAYER (Supabase)    │
          │  ┌──────────────────────────┐   │
          │  │   PostgreSQL Database    │   │
          │  │  ┌────────────────────┐  │   │
          │  │  │  Tables:           │  │   │
          │  │  │  - users           │  │   │
          │  │  │  - patients        │  │   │
          │  │  │  - medical_staff   │  │   │
          │  │  │  - appointments    │  │   │
          │  │  │  - medical_records │  │   │
          │  │  │  - audit_logs      │  │   │
          │  │  └────────────────────┘  │   │
          │  │  ┌────────────────────┐  │   │
          │  │  │  Indexes           │  │   │
          │  │  │  Triggers          │  │   │
          │  │  │  Constraints       │  │   │
          │  │  └────────────────────┘  │   │
          │  └──────────────────────────┘   │
          └─────────────────────────────────┘
```

## Technology Stack

### Backend Framework
- **Flask 2.3.3** - Lightweight Python web framework
- **Python 3.8+** - Programming language
- **Werkzeug 2.3.7** - WSGI utility library

### Database & Backend Services
- **Supabase** - PostgreSQL database as a service
- **PostgreSQL** - Relational database (via Supabase)
- **supabase-py** - Python client library

### Authentication & Security
- **Flask-Login 0.6.3** - User session management
- **Flask-WTF 1.1.1** - Form handling and CSRF protection
- **bcrypt 4.0.1** - Password hashing (SHA-256 also used)
- **Flask-Limiter 3.5.0** - Rate limiting
- **validators 0.22.0** - Input validation

### Frontend
- **HTML5/CSS3** - Markup and styling
- **Bootstrap 5** - CSS framework
- **JavaScript** - Client-side interactivity
- **Jinja2** - Template engine (built into Flask)

### Development Tools
- **python-dotenv 1.1.1** - Environment variable management
- **Flask-CORS 4.0.0** - Cross-Origin Resource Sharing
- **python-dateutil 2.8.2** - Date/time utilities

### Deployment
- **Gunicorn** - WSGI HTTP Server (production)
- **Nginx** - Reverse proxy and static file server
- **Systemd** - Service management

## Application Structure

```
healthcare-portal/
│
├── app.py                          # Main application entry point
│   ├── HealthcareApp class         # Main application class
│   ├── Configuration               # App configuration
│   ├── Database setup              # Supabase connection
│   ├── Route definitions           # URL routing
│   └── Error handlers              # Custom error pages
│
├── data_supabase.py                # CLI data management tool
│   ├── HealthcareSystem class      # Database operations
│   ├── User management             # CRUD operations
│   ├── Patient records             # Medical record management
│   └── Interactive CLI             # Command-line interface
│
├── templates/                      # HTML templates (Jinja2)
│   ├── base.html                   # Base template (all pages extend this)
│   ├── index.html                  # Homepage
│   ├── login.html                  # Login page
│   ├── register.html               # User registration
│   ├── profile.html                # User profile
│   │
│   ├── admin/                      # Administrator pages
│   │   └── dashboard.html          # Admin dashboard
│   │
│   ├── doctor/                     # Doctor pages
│   │   └── dashboard.html          # Doctor dashboard
│   │
│   ├── nurse/                      # Nurse pages
│   │   └── dashboard.html          # Nurse dashboard
│   │
│   ├── patient/                    # Patient pages
│   │   └── dashboard.html          # Patient dashboard
│   │
│   ├── appointments/               # Appointment management
│   │   ├── book.html               # Book appointment
│   │   ├── list.html               # Appointment list
│   │   └── details.html            # Appointment details
│   │
│   ├── medical_records/            # Medical records
│   │   ├── add.html                # Add record
│   │   └── list.html               # Record list
│   │
│   ├── patients/                   # Patient management
│   │   ├── list.html               # Patient list
│   │   └── details.html            # Patient details
│   │
│   └── errors/                     # Error pages
│       ├── 403.html                # Forbidden
│       ├── 404.html                # Not Found
│       └── 500.html                # Server Error
│
├── static/                         # Static assets
│   ├── css/                        # Stylesheets
│   │   └── main.css                # Custom styles
│   ├── js/                         # JavaScript files
│   │   └── main.js                 # Custom scripts
│   └── images/                     # Images (if any)
│
├── logs/                           # Application logs
│   └── pdms.log                    # Main log file
│
├── .env                            # Environment variables (not in git)
├── .env.example                    # Environment template
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Project configuration
│
└── Documentation files
    ├── README.md                   # Main documentation
    ├── SUPABASE_SETUP.md           # Database setup guide
    ├── CONFIGURATION.md            # Config reference
    ├── DATABASE_SCHEMA.md          # Schema documentation
    ├── MIGRATION_GUIDE.md          # Migration instructions
    └── ARCHITECTURE.md             # This file
```

## Security Architecture

### 1. Authentication Flow

```
┌──────────────┐
│   User       │
│   Visits     │
│   Login Page │
└──────┬───────┘
       │
       │ 1. Submit credentials
       ▼
┌──────────────────┐
│  Flask Route     │
│  /login          │
└──────┬───────────┘
       │
       │ 2. Validate CSRF token
       ▼
┌──────────────────┐
│  Validate Input  │
│  - Username      │
│  - Password      │
└──────┬───────────┘
       │
       │ 3. Hash password (SHA-256)
       ▼
┌──────────────────┐
│  Query Database  │
│  (Supabase)      │
└──────┬───────────┘
       │
       │ 4. Compare credentials
       ▼
┌──────────────────┐
│  Authentication  │
│  Success?        │
└──────┬───────────┘
       │
       ├─── YES ───┐
       │           ▼
       │     ┌──────────────┐
       │     │ Create       │
       │     │ Session      │
       │     │ (Flask-Login)│
       │     └──────┬───────┘
       │            │
       │            │ 5. Set session cookie
       │            ▼
       │     ┌──────────────┐
       │     │ Log Action   │
       │     │ (Audit Log)  │
       │     └──────┬───────┘
       │            │
       │            │ 6. Redirect to dashboard
       │            ▼
       │     ┌──────────────┐
       │     │ User         │
       │     │ Dashboard    │
       │     └──────────────┘
       │
       └─── NO ────┐
                   ▼
            ┌──────────────┐
            │ Show Error   │
            │ Log Attempt  │
            │ Increment    │
            │ Failed Count │
            └──────────────┘
```

### 2. Authorization (RBAC)

```
User Role Hierarchy:

Administrator (Full Access)
    │
    ├── Manage all users
    ├── View all data
    ├── System configuration
    ├── Audit logs
    └── Medical staff management

Doctor (Advanced Access)
    │
    ├── View assigned patients
    ├── Create/update medical records
    ├── Manage appointments
    ├── Prescribe medications
    └── View patient history

Nurse (Intermediate Access)
    │
    ├── View patient lists
    ├── Update patient information
    ├── Manage appointments
    ├── View medical records (limited)
    └── Update basic records

Patient (Basic Access)
    │
    ├── View own medical records
    ├── Book appointments
    ├── View appointment history
    ├── Update profile
    └── View assigned doctors
```

### 3. Security Layers

**Layer 1: Input Validation**
- CSRF token validation on all forms
- Input sanitization
- Email format validation
- Password strength requirements
- SQL injection prevention (parameterized queries)

**Layer 2: Authentication**
- SHA-256 password hashing
- Session-based authentication
- Session timeout (configurable)
- Secure session cookies (HTTPS in production)

**Layer 3: Authorization**
- Role-based access control (RBAC)
- Route-level permission checks
- Data-level permission checks
- Cross-user data access prevention

**Layer 4: Rate Limiting**
- Login attempt limiting (default: 5 attempts)
- API rate limiting (1000/hour)
- General route rate limiting (100/hour)
- Account lockout on excessive failures

**Layer 5: Audit Logging**
- All user actions logged
- IP address tracking
- User agent logging
- Timestamp recording
- JSONB storage for old/new values

## Database Design

### Entity Relationships

```
┌────────────┐
│   users    │ (Parent table)
│            │
│ - id (PK)  │
│ - username │
│ - password │
│ - role     │
│ - email    │
│ - ...      │
└─────┬──────┘
      │
      │ 1:1 relationships
      ├──────────────┬──────────────┐
      │              │              │
┌─────▼──────┐ ┌────▼──────┐ ┌────▼──────────┐
│  patients  │ │  medical  │ │  audit_logs   │
│            │ │  _staff   │ │               │
│ - patient_ │ │ - staff_  │ │ - user_id     │
│   id (FK)  │ │   id (FK) │ │ - action      │
│ - blood_   │ │ - special │ │ - created_at  │
│   type     │ │   ization │ │ - ...         │
└────────────┘ │ - license │ └───────────────┘
               │   _number │
               └───────────┘
      │
      │ 1:Many relationships
      ├──────────────────────────┐
      │                          │
┌─────▼────────────┐   ┌─────────▼──────────┐
│  appointments    │   │  medical_records   │
│                  │   │                    │
│ - id (PK)        │   │ - id (PK)          │
│ - patient_id (FK)│   │ - patient_id (FK)  │
│ - doctor_id (FK) │   │ - doctor_id (FK)   │
│ - date           │   │ - visit_date       │
│ - status         │   │ - diagnosis        │
│ - reason         │   │ - treatment        │
└──────────────────┘   │ - prescription     │
                       └────────────────────┘
```

### Key Design Patterns

**1. Inheritance Pattern**
- Base `users` table for all user types
- Specialized tables (`patients`, `medical_staff`) linked via foreign key
- Reduces data duplication
- Simplifies authentication

**2. Audit Trail Pattern**
- `audit_logs` table captures all changes
- JSONB fields store old/new values
- Timestamp and user tracking
- IP address logging

**3. Soft Delete Pattern**
- `status` fields instead of DELETE operations
- Preserves data integrity
- Maintains audit trail
- Can be restored if needed

**4. Timestamp Pattern**
- `created_at` and `updated_at` on all tables
- Automatic updates via triggers
- Tracks record lifecycle

## Authentication & Authorization

### Session Management

```python
# Session Configuration
app.config['SESSION_TIMEOUT'] = 28800  # 8 hours in seconds
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only (production)
app.config['SESSION_COOKIE_HTTPONLY'] = True  # No JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
```

### Login Flow

1. User submits credentials
2. CSRF token validated
3. Username looked up in database
4. Password hashed with SHA-256
5. Hash compared with stored hash
6. On success:
   - Session created
   - User ID stored in session
   - Role stored in session
   - Action logged
7. On failure:
   - Failed attempt counter incremented
   - Account locked after max attempts
   - Error message displayed

### Route Protection

```python
@login_required
def protected_route():
    # Only accessible to authenticated users
    pass

@role_required('doctor')
def doctor_only_route():
    # Only accessible to doctors
    pass

@role_required(['doctor', 'nurse'])
def medical_staff_route():
    # Accessible to doctors and nurses
    pass
```

## API Endpoints

### Public Routes
- `GET /` - Homepage
- `GET /login` - Login page
- `POST /login` - Process login
- `GET /register` - Registration page
- `POST /register` - Process registration

### Authentication Required
- `GET /dashboard` - User dashboard (role-based redirect)
- `GET /profile` - User profile
- `POST /profile` - Update profile
- `GET /logout` - Logout

### Patient Routes
- `GET /patient/dashboard` - Patient dashboard
- `GET /patient/appointments` - View appointments
- `GET /patient/medical-records` - View medical records

### Doctor Routes
- `GET /doctor/dashboard` - Doctor dashboard
- `GET /doctor/patients` - View patients
- `GET /doctor/appointments` - Manage appointments
- `POST /doctor/medical-record` - Create medical record

### Nurse Routes
- `GET /nurse/dashboard` - Nurse dashboard
- `GET /nurse/patients` - View patients
- `GET /nurse/appointments` - Manage appointments

### Administrator Routes
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/users` - Manage users
- `POST /admin/users` - Create user
- `PUT /admin/users/<id>` - Update user
- `DELETE /admin/users/<id>` - Delete user
- `GET /admin/audit-logs` - View audit logs
- `GET /admin/statistics` - System statistics

### Appointment Routes
- `GET /appointments` - List appointments
- `GET /appointments/<id>` - Appointment details
- `POST /appointments` - Book appointment
- `PUT /appointments/<id>` - Update appointment
- `DELETE /appointments/<id>` - Cancel appointment

### Medical Record Routes
- `GET /medical-records` - List records
- `GET /medical-records/<id>` - Record details
- `POST /medical-records` - Create record
- `PUT /medical-records/<id>` - Update record

## Frontend Architecture

### Template Hierarchy

```
base.html (Master Template)
    │
    ├── Navigation Bar
    │   ├── Logo
    │   ├── Role-based menu items
    │   └── User dropdown
    │
    ├── Flash Messages
    │   ├── Success messages
    │   ├── Error messages
    │   └── Warning messages
    │
    ├── Content Block ({% block content %})
    │   └── Child templates extend this
    │
    └── Footer
        ├── Copyright
        └── Links

Child Templates
    │
    ├── index.html (Homepage)
    ├── login.html (Login page)
    ├── register.html (Registration)
    │
    ├── Dashboards (role-specific)
    │   ├── patient/dashboard.html
    │   ├── doctor/dashboard.html
    │   ├── nurse/dashboard.html
    │   └── admin/dashboard.html
    │
    ├── Feature pages
    │   ├── appointments/
    │   ├── medical_records/
    │   └── patients/
    │
    └── Error pages
        ├── 403.html (Forbidden)
        ├── 404.html (Not Found)
        └── 500.html (Server Error)
```

### CSS Architecture

- **Bootstrap 5** - Base framework
- **Custom CSS** - Overrides and extensions
- **Responsive Design** - Mobile-first approach
- **Component-based** - Reusable UI components

### JavaScript Organization

- **Vanilla JavaScript** - No framework dependency
- **Event Handlers** - Form validation, AJAX calls
- **Dynamic Content** - Real-time updates
- **Modular Design** - Separated by feature

## Deployment Architecture

### Development Environment

```
Developer Machine
    │
    ├── Flask Development Server (port 5000)
    ├── SQLite or Supabase (development)
    ├── Debug mode enabled
    └── Auto-reload enabled
```

### Production Environment

```
┌─────────────────────────────────────┐
│         Internet                     │
└───────────────┬─────────────────────┘
                │
                │ HTTPS (Port 443)
                ▼
        ┌───────────────┐
        │   Nginx       │
        │  (Reverse     │
        │   Proxy)      │
        └───────┬───────┘
                │
                │ HTTP (Port 8000)
                ▼
        ┌───────────────┐
        │   Gunicorn    │
        │   (4 workers) │
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │  Flask App    │
        │  (Python)     │
        └───────┬───────┘
                │
                │ API Calls
                ▼
        ┌───────────────┐
        │   Supabase    │
        │  (PostgreSQL) │
        └───────────────┘
```

### Load Balanced Production (Future)

```
                Internet
                   │
                   ▼
            Load Balancer
            (AWS ELB/ALB)
                   │
      ┌────────────┼────────────┐
      │            │            │
      ▼            ▼            ▼
   Nginx 1      Nginx 2      Nginx 3
      │            │            │
      ▼            ▼            ▼
  Gunicorn     Gunicorn     Gunicorn
      │            │            │
      └────────────┼────────────┘
                   │
                   ▼
              Supabase
            (PostgreSQL)
                   │
                   ▼
            Redis (Cache)
         (Rate Limit Store)
```

## Scalability Considerations

### Current Limitations
- Single server deployment
- In-memory rate limiting
- Session storage in Flask

### Future Improvements
1. **Horizontal Scaling**
   - Multiple application servers
   - Load balancer
   - Redis for shared state

2. **Caching Layer**
   - Redis cache
   - Static content CDN
   - Database query caching

3. **Database Optimization**
   - Connection pooling
   - Read replicas
   - Query optimization

4. **Monitoring**
   - Application performance monitoring
   - Error tracking (e.g., Sentry)
   - Log aggregation (e.g., ELK stack)

## Performance Optimization

### Database
- Indexed columns for common queries
- Connection pooling via Supabase
- Query optimization
- Proper foreign key relationships

### Application
- Route caching where appropriate
- Static file compression
- Minified CSS/JS (production)
- Lazy loading of data

### Frontend
- CDN for Bootstrap
- Image optimization
- Responsive images
- Browser caching headers

## Security Best Practices

### Implemented
- [x] CSRF protection on all forms
- [x] Password hashing (SHA-256)
- [x] Session management
- [x] Role-based access control
- [x] Rate limiting
- [x] Input validation
- [x] Audit logging
- [x] SQL injection prevention
- [x] XSS prevention (Jinja2 auto-escaping)

### Recommended for Production
- [ ] HTTPS/SSL certificates
- [ ] Row Level Security (RLS) in Supabase
- [ ] Two-factor authentication (2FA)
- [ ] API authentication tokens
- [ ] Regular security audits
- [ ] Penetration testing
- [ ] HIPAA compliance measures
- [ ] Data encryption at rest

## Monitoring & Logging

### Application Logs
- **Location**: `logs/pdms.log`
- **Format**: Standard Python logging
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Rotation**: Needs to be configured

### Audit Logs
- **Storage**: Database (audit_logs table)
- **Captures**: User actions, IP, timestamp
- **Retention**: Permanent (consider archiving strategy)

### System Metrics (Future)
- Request count
- Response times
- Error rates
- Database query performance
- Memory usage
- CPU usage

## Compliance & Regulations

### HIPAA Considerations
- Audit logging implemented
- Access controls implemented
- Encryption in transit (with HTTPS)
- User authentication and authorization
- Session timeout enforcement

### Recommended Additions
- Data encryption at rest
- Business Associate Agreements (BAA)
- Regular compliance audits
- Breach notification procedures
- Data retention policies

## Future Enhancements

### Short-term
- [ ] Password reset functionality
- [ ] Email notifications
- [ ] Advanced search and filtering
- [ ] Export data to PDF
- [ ] Appointment reminders

### Medium-term
- [ ] Two-factor authentication
- [ ] API for mobile apps
- [ ] Real-time notifications (WebSocket)
- [ ] File upload for medical documents
- [ ] Prescription management system

### Long-term
- [ ] Telemedicine integration
- [ ] Lab results integration
- [ ] Billing and insurance management
- [ ] Analytics and reporting dashboard
- [ ] Multi-language support
- [ ] Mobile applications (iOS/Android)

## Conclusion

The Healthcare Portal architecture is designed for:
- **Security**: Multiple layers of protection
- **Scalability**: Can be extended to handle growth
- **Maintainability**: Clean code structure and documentation
- **Compliance**: Audit logging and access controls
- **User Experience**: Role-based interfaces

For detailed information on specific components, refer to:
- [README.md](README.md) - Getting started
- [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) - Database design
- [CONFIGURATION.md](CONFIGURATION.md) - Configuration options
- [SUPABASE_SETUP.md](SUPABASE_SETUP.md) - Database setup
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Deployment guide
