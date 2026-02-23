# GEMINI.md - Healthcare Portal Project Context

## Project Overview

**Healthcare Portal** is a comprehensive healthcare management system built with **Flask** and **Supabase (PostgreSQL)**. It provides a secure, role-based platform for patients, medical staff (doctors and nurses), and administrators to manage medical records, appointments, and user profiles.

### Core Technologies
- **Backend:** Python 3.8+, Flask 3.0.3, Supabase (PostgreSQL)
- **Frontend:** HTML5/CSS3, Bootstrap 5, Jinja2 Templates
- **Authentication & Security:** Flask-Login, Flask-WTF (CSRF), SHA-256 Hashing, Audit Logging
- **Database:** Supabase Client (`supabase-py`) for PostgreSQL interaction

### Key Architecture
The project follows a monolithic web application structure with a separate data access layer:
- **`app.py`**: The primary entry point, containing the `HealthcareApp` class which initializes Flask, configures security, manages routing, and handles user sessions.
- **`data_supabase.py`**: A parallel CLI-based management tool for administrative tasks and direct database interaction.
- **Role-Based Access Control (RBAC):** Four distinct roles:
    - **Patient:** Book appointments, view own medical records/profile.
    - **Nurse:** Manage patient lists, update vital signs/notes, view appointments.
    - **Doctor:** Full access to assigned patient records, add diagnoses/prescriptions, manage schedule.
    - **Administrator:** System-wide management, user CRUD, audit logs, and statistics.

---

## Building and Running

### Prerequisites
- Python 3.8+
- Supabase account with a project created.

### Environment Setup
1. **Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # venv\Scripts\activate   # Windows
   ```
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configuration:**
   Create a `.env` file from `.env.example`:
   ```env
   SUPABASE_URL=your-project-url
   SUPABASE_ANON_KEY=your-anon-key
   SECRET_KEY=your-flask-secret-key
   ```

### Database Initialization
Apply the SQL scripts located in the `sql/` directory via the Supabase SQL Editor:
1. `sql/supabase_schema.sql`: Core table structure.
2. `sql/create_admin.sql`: Default admin account (`admin`/`admin123`).
3. `sql/add_missing_columns.sql`: Necessary schema updates.

### Running the App
- **Development Mode:**
  ```bash
  python app.py
  ```
- **Production Mode:**
  ```bash
  gunicorn -w 4 -b 0.0.0.0:8000 app:app
  ```

---

## Development Conventions

### Coding Style
- **Formatting:** Adheres to **Black** (100 char line limit).
- **Type Hinting:** Used in major functions (see `app.py` and `data_supabase.py`).
- **Linting:** Configured for `flake8`, `isort`, and `mypy` (see `pyproject.toml`).

### Project Structure
- `templates/`: Role-specific subdirectories (e.g., `templates/doctor/`, `templates/admin/`) to keep the UI logic separated.
- `static/`: Separated into `css/` and `js/`.
- `sql/`: Contains all schema definitions and migrations.

### Security Practices
- **Audit Logs:** Every major action (login, record update, registration) is recorded in the `audit_logs` table via the `log_action` utility.
- **Input Validation:** All forms use `Flask-WTF` for CSRF protection and server-side validation.
- **RBAC Decorators:** Use `@login_required` and `@role_required('role_name')` to protect routes.

### Testing & Quality
- **Test Framework:** `pytest` is configured for the project.
- **CI/CD:** Commands for linting and type checking are available via `black`, `flake8`, and `mypy`.

---

## Key Documentation
- [ARCHITECTURE.md](ARCHITECTURE.md): Deep dive into system design and security layers.
- [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md): Detailed table relationships and constraints.
- [SUPABASE_SETUP.md](SUPABASE_SETUP.md): Step-by-step guide for database configuration.
- [QUICKSTART.md](QUICKSTART.md): 10-minute setup guide for new developers.
