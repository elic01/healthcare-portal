# Database Schema Documentation

This document provides detailed information about the database schema for the Healthcare Portal.

## Table of Contents

- [Overview](#overview)
- [Database Tables](#database-tables)
- [Relationships](#relationships)
- [Indexes](#indexes)
- [Triggers](#triggers)
- [Data Types](#data-types)

## Overview

The Healthcare Portal database uses PostgreSQL (via Supabase) with the following structure:

**Total Tables**: 6
- users
- patients
- medical_staff
- appointments
- medical_records
- audit_logs

## Database Tables

### 1. users

**Description**: Central table for all system users (patients, nurses, doctors, administrators)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Unique user identifier |
| username | VARCHAR(50) | UNIQUE, NOT NULL | User's login username |
| password | VARCHAR(255) | NOT NULL | SHA-256 hashed password |
| role | VARCHAR(20) | NOT NULL, CHECK | User role (patient, nurse, doctor, administrator) |
| email | VARCHAR(100) | UNIQUE | User's email address |
| first_name | VARCHAR(50) | | User's first name |
| last_name | VARCHAR(50) | | User's last name |
| date_of_birth | DATE | | User's date of birth |
| phone_number | VARCHAR(20) | | Contact phone number |
| address | TEXT | | Physical address |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Account creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Last update timestamp |

**Constraints**:
- `CHECK (role IN ('patient', 'nurse', 'doctor', 'administrator'))`

**Indexes**:
- `idx_users_username` on username
- `idx_users_email` on email
- `idx_users_role` on role

**Sample Data**:
```sql
INSERT INTO users (username, password, role, first_name, last_name, email)
VALUES ('admin', 'hashed_password', 'administrator', 'System', 'Administrator', 'admin@pdms.com');
```

---

### 2. patients

**Description**: Patient-specific information and medical details

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| patient_id | BIGINT | PRIMARY KEY, FOREIGN KEY | References users(id) |
| emergency_contact | VARCHAR(100) | | Emergency contact information |
| insurance_info | TEXT | | Health insurance details |
| medical_history | TEXT | | Patient's medical history |
| allergies | TEXT | | Known allergies |
| blood_type | VARCHAR(5) | | Blood type (A+, B+, O-, etc.) |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Record creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Last update timestamp |

**Relationships**:
- `patient_id` REFERENCES `users(id)` ON DELETE CASCADE

**Sample Data**:
```sql
INSERT INTO patients (patient_id, emergency_contact, blood_type, allergies)
VALUES (1, 'Jane Doe - 555-0123', 'A+', 'Penicillin, Peanuts');
```

---

### 3. medical_staff

**Description**: Information specific to medical staff (doctors, nurses)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| staff_id | BIGINT | PRIMARY KEY, FOREIGN KEY | References users(id) |
| specialization | VARCHAR(100) | | Medical specialization |
| license_number | VARCHAR(50) | UNIQUE | Medical license number |
| hire_date | DATE | | Date of employment |
| department | VARCHAR(100) | | Hospital department |
| status | VARCHAR(20) | DEFAULT 'active', CHECK | Employment status |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Record creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Last update timestamp |

**Constraints**:
- `CHECK (status IN ('active', 'inactive', 'on_leave'))`

**Relationships**:
- `staff_id` REFERENCES `users(id)` ON DELETE CASCADE

**Sample Data**:
```sql
INSERT INTO medical_staff (staff_id, specialization, license_number, department)
VALUES (2, 'Cardiology', 'MD-12345', 'Cardiology Department');
```

---

### 4. appointments

**Description**: Patient appointments with doctors

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Unique appointment identifier |
| patient_id | BIGINT | NOT NULL, FOREIGN KEY | Patient's user ID |
| doctor_id | BIGINT | NOT NULL, FOREIGN KEY | Doctor's user ID |
| appointment_date | TIMESTAMP WITH TIME ZONE | NOT NULL | Date and time of appointment |
| appointment_time | TIME | | Appointment time (separate field) |
| duration_minutes | INTEGER | DEFAULT 30 | Appointment duration |
| status | VARCHAR(20) | DEFAULT 'scheduled', CHECK | Appointment status |
| reason | TEXT | | Reason for appointment |
| notes | TEXT | | Additional notes |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Record creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Last update timestamp |

**Constraints**:
- `CHECK (status IN ('scheduled', 'completed', 'cancelled', 'no_show'))`

**Relationships**:
- `patient_id` REFERENCES `users(id)` ON DELETE CASCADE
- `doctor_id` REFERENCES `users(id)` ON DELETE CASCADE

**Indexes**:
- `idx_appointments_patient` on patient_id
- `idx_appointments_doctor` on doctor_id
- `idx_appointments_date` on appointment_date

**Sample Data**:
```sql
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason, status)
VALUES (1, 2, '2025-10-15 10:00:00+00', 'Annual checkup', 'scheduled');
```

---

### 5. medical_records

**Description**: Patient medical records and visit history

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Unique record identifier |
| patient_id | BIGINT | NOT NULL, FOREIGN KEY | Patient's user ID |
| doctor_id | BIGINT | NOT NULL, FOREIGN KEY | Doctor's user ID |
| visit_date | TIMESTAMP WITH TIME ZONE | NOT NULL | Date of visit/record |
| symptoms | TEXT | | Patient's reported symptoms |
| diagnosis | TEXT | | Doctor's diagnosis |
| treatment | TEXT | | Prescribed treatment |
| prescription | TEXT | | Medication prescriptions |
| notes | TEXT | | Additional clinical notes |
| visit_type | VARCHAR(50) | DEFAULT 'general' | Type of visit |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Record creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Last update timestamp |

**Relationships**:
- `patient_id` REFERENCES `users(id)` ON DELETE CASCADE
- `doctor_id` REFERENCES `users(id)` ON DELETE CASCADE

**Indexes**:
- `idx_medical_records_patient` on patient_id

**Sample Data**:
```sql
INSERT INTO medical_records (patient_id, doctor_id, visit_date, symptoms, diagnosis, treatment)
VALUES (1, 2, NOW(), 'Fever, headache', 'Viral infection', 'Rest, fluids, paracetamol');
```

---

### 6. audit_logs

**Description**: Audit trail for compliance and security monitoring

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Unique log identifier |
| user_id | BIGINT | FOREIGN KEY | User who performed action |
| action | VARCHAR(100) | NOT NULL | Action performed |
| table_name | VARCHAR(50) | | Table affected |
| record_id | BIGINT | | ID of affected record |
| old_values | JSONB | | Previous values (for updates) |
| new_values | JSONB | | New values (for updates) |
| ip_address | INET | | User's IP address |
| user_agent | TEXT | | User's browser/client info |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | When action occurred |

**Relationships**:
- `user_id` REFERENCES `users(id)` ON DELETE SET NULL

**Indexes**:
- `idx_audit_logs_user` on user_id
- `idx_audit_logs_created` on created_at

**Sample Data**:
```sql
INSERT INTO audit_logs (user_id, action, table_name, record_id, ip_address)
VALUES (1, 'LOGIN', 'users', 1, '192.168.1.1');
```

---

## Relationships

### Entity Relationship Diagram (Text Format)

```
users (1) ------ (0..1) patients
users (1) ------ (0..1) medical_staff
users (1) ------ (0..*) appointments [as patient]
users (1) ------ (0..*) appointments [as doctor]
users (1) ------ (0..*) medical_records [as patient]
users (1) ------ (0..*) medical_records [as doctor]
users (1) ------ (0..*) audit_logs
```

### Relationship Details

1. **users ↔ patients**: One-to-One
   - A user with role 'patient' has one patient record
   - ON DELETE CASCADE: Deleting user deletes patient record

2. **users ↔ medical_staff**: One-to-One
   - A user with role 'doctor' or 'nurse' has one medical_staff record
   - ON DELETE CASCADE: Deleting user deletes medical_staff record

3. **users ↔ appointments**: One-to-Many (as patient and as doctor)
   - A patient can have multiple appointments
   - A doctor can have multiple appointments
   - ON DELETE CASCADE: Deleting user deletes their appointments

4. **users ↔ medical_records**: One-to-Many (as patient and as doctor)
   - A patient can have multiple medical records
   - A doctor can create multiple medical records
   - ON DELETE CASCADE: Deleting user deletes their records

5. **users ↔ audit_logs**: One-to-Many
   - A user can have multiple audit log entries
   - ON DELETE SET NULL: Deleting user keeps logs but nullifies user_id

## Indexes

### Performance Indexes

| Index Name | Table | Column(s) | Purpose |
|------------|-------|-----------|---------|
| idx_users_username | users | username | Fast login lookups |
| idx_users_email | users | email | Email-based queries |
| idx_users_role | users | role | Role-based filtering |
| idx_appointments_patient | appointments | patient_id | Patient's appointments |
| idx_appointments_doctor | appointments | doctor_id | Doctor's appointments |
| idx_appointments_date | appointments | appointment_date | Date-based queries |
| idx_medical_records_patient | medical_records | patient_id | Patient's records |
| idx_audit_logs_user | audit_logs | user_id | User activity logs |
| idx_audit_logs_created | audit_logs | created_at | Time-based log queries |

### Index Usage Examples

```sql
-- Fast lookup by username (uses idx_users_username)
SELECT * FROM users WHERE username = 'john_doe';

-- Fast patient appointment lookup (uses idx_appointments_patient)
SELECT * FROM appointments WHERE patient_id = 123;

-- Fast date range query (uses idx_appointments_date)
SELECT * FROM appointments
WHERE appointment_date BETWEEN '2025-01-01' AND '2025-12-31';
```

## Triggers

### Automatic Timestamp Updates

**Function**: `update_updated_at_column()`
- Automatically updates the `updated_at` field on row updates
- Written in PL/pgSQL

**Triggers**:
1. `update_users_updated_at` on users table
2. `update_patients_updated_at` on patients table
3. `update_medical_staff_updated_at` on medical_staff table
4. `update_appointments_updated_at` on appointments table
5. `update_medical_records_updated_at` on medical_records table

**Example**:
```sql
-- When you update a user
UPDATE users SET first_name = 'John' WHERE id = 1;
-- updated_at is automatically set to NOW()
```

## Data Types

### Common Data Types Used

| Type | Description | Example |
|------|-------------|---------|
| BIGSERIAL | Auto-incrementing 64-bit integer | IDs |
| BIGINT | 64-bit integer | Foreign keys |
| VARCHAR(n) | Variable-length string (max n chars) | Names, emails |
| TEXT | Unlimited length text | Notes, descriptions |
| DATE | Date (no time) | Birth dates, hire dates |
| TIME | Time (no date) | Appointment times |
| TIMESTAMP WITH TIME ZONE | Date and time with timezone | created_at, updated_at |
| INTEGER | 32-bit integer | Duration, counts |
| JSONB | Binary JSON | Audit log values |
| INET | IP address | IP addresses |

### Timestamp Best Practices

Always use `TIMESTAMP WITH TIME ZONE` for:
- Record creation times (created_at)
- Update times (updated_at)
- Scheduled events (appointment_date)

This ensures timezone-aware date handling across different locations.

## Constraints

### CHECK Constraints

1. **users.role**:
   ```sql
   CHECK (role IN ('patient', 'nurse', 'doctor', 'administrator'))
   ```

2. **medical_staff.status**:
   ```sql
   CHECK (status IN ('active', 'inactive', 'on_leave'))
   ```

3. **appointments.status**:
   ```sql
   CHECK (status IN ('scheduled', 'completed', 'cancelled', 'no_show'))
   ```

### UNIQUE Constraints

1. users.username - No duplicate usernames
2. users.email - No duplicate emails
3. medical_staff.license_number - No duplicate licenses

### NOT NULL Constraints

Critical fields that must have values:
- users.username
- users.password
- users.role
- appointments.patient_id
- appointments.doctor_id
- appointments.appointment_date
- medical_records.patient_id
- medical_records.doctor_id
- medical_records.visit_date
- audit_logs.action

## Common Queries

### Get User with Role Information

```sql
SELECT
    u.*,
    CASE
        WHEN u.role = 'patient' THEN p.blood_type
        WHEN u.role IN ('doctor', 'nurse') THEN ms.specialization
        ELSE NULL
    END as additional_info
FROM users u
LEFT JOIN patients p ON u.id = p.patient_id
LEFT JOIN medical_staff ms ON u.id = ms.staff_id
WHERE u.id = 123;
```

### Get Patient Appointments with Doctor Names

```sql
SELECT
    a.*,
    u_patient.first_name || ' ' || u_patient.last_name as patient_name,
    u_doctor.first_name || ' ' || u_doctor.last_name as doctor_name
FROM appointments a
JOIN users u_patient ON a.patient_id = u_patient.id
JOIN users u_doctor ON a.doctor_id = u_doctor.id
WHERE a.patient_id = 123
ORDER BY a.appointment_date DESC;
```

### Get Patient Medical History

```sql
SELECT
    mr.*,
    u_doctor.first_name || ' ' || u_doctor.last_name as doctor_name
FROM medical_records mr
JOIN users u_doctor ON mr.doctor_id = u_doctor.id
WHERE mr.patient_id = 123
ORDER BY mr.visit_date DESC;
```

### Get Audit Log for a User

```sql
SELECT
    al.*,
    u.username,
    u.first_name || ' ' || u.last_name as full_name
FROM audit_logs al
LEFT JOIN users u ON al.user_id = u.id
WHERE al.user_id = 123
ORDER BY al.created_at DESC
LIMIT 50;
```

## Database Maintenance

### Regular Maintenance Tasks

1. **Vacuum tables** (PostgreSQL maintenance):
   ```sql
   VACUUM ANALYZE users;
   VACUUM ANALYZE appointments;
   VACUUM ANALYZE medical_records;
   ```

2. **Check table sizes**:
   ```sql
   SELECT
       schemaname,
       tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
   FROM pg_tables
   WHERE schemaname = 'public'
   ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
   ```

3. **Monitor index usage**:
   ```sql
   SELECT
       schemaname,
       tablename,
       indexname,
       idx_scan,
       idx_tup_read,
       idx_tup_fetch
   FROM pg_stat_user_indexes
   WHERE schemaname = 'public'
   ORDER BY idx_scan DESC;
   ```

## Migration Notes

### Adding New Columns

When adding new columns, use `IF NOT EXISTS`:

```sql
ALTER TABLE table_name
ADD COLUMN IF NOT EXISTS column_name TYPE;
```

### Modifying Existing Columns

Be careful with data migration:

```sql
-- Add new column
ALTER TABLE users ADD COLUMN temp_column VARCHAR(100);

-- Migrate data
UPDATE users SET temp_column = old_column;

-- Drop old column
ALTER TABLE users DROP COLUMN old_column;

-- Rename new column
ALTER TABLE users RENAME COLUMN temp_column TO old_column;
```

## Backup and Restore

### Using Supabase Dashboard

1. Go to Database > Backups
2. Automatic backups are created daily (free tier: 7 days retention)
3. Can restore from any backup point

### Manual Backup (SQL Dump)

```bash
# Using pg_dump (if you have direct database access)
pg_dump -h [host] -U [user] -d [database] > backup.sql
```

### Restore from Backup

```bash
# Using psql
psql -h [host] -U [user] -d [database] < backup.sql
```

## Security Considerations

### Row Level Security (RLS)

For production, implement RLS policies:

```sql
-- Enable RLS on a table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Create policy (example: users can only see their own data)
CREATE POLICY user_self_select ON users
    FOR SELECT
    USING (auth.uid() = id);
```

### Sensitive Data

Consider encryption for:
- insurance_info
- medical_history
- prescription details

### Audit Trail

The audit_logs table captures:
- Who performed the action
- What action was performed
- When it was performed
- IP address and user agent
- Old and new values (for updates)

Regularly review audit logs for suspicious activity.

## Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Supabase Database Guide](https://supabase.com/docs/guides/database)
- [SQL Tutorial](https://www.postgresql.org/docs/current/tutorial.html)
