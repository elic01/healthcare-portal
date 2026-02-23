-- Seed Data for Healthcare Portal
-- This script creates test accounts for all roles

-- 1. Create Doctor
INSERT INTO users (username, password, role, first_name, last_name, email) 
VALUES (
    'doctor',
    'f348d5628621f3d8f59c8cabda0f8eb0aa7e0514a90be7571020b1336f26c113', -- doctor123
    'doctor',
    'John',
    'Smith',
    'dr.smith@pdms.com'
) ON CONFLICT (username) DO NOTHING;

-- Get doctor id and insert into medical_staff
INSERT INTO medical_staff (staff_id, specialization, license_number, hire_date, department, status)
SELECT id, 'Cardiology', 'LIC-DOC-001', CURRENT_DATE, 'Cardiology', 'active'
FROM users WHERE username = 'doctor'
ON CONFLICT (staff_id) DO NOTHING;

-- 2. Create Nurse
INSERT INTO users (username, password, role, first_name, last_name, email) 
VALUES (
    'nurse',
    '35608f3146571aa100227a3e68290979ba8a452179a080f888625106076e7de2', -- nurse123
    'nurse',
    'Jane',
    'Doe',
    'nurse.jane@pdms.com'
) ON CONFLICT (username) DO NOTHING;

-- Get nurse id and insert into medical_staff
INSERT INTO medical_staff (staff_id, specialization, license_number, hire_date, department, status)
SELECT id, 'Emergency Care', 'LIC-NUR-001', CURRENT_DATE, 'ER', 'active'
FROM users WHERE username = 'nurse'
ON CONFLICT (staff_id) DO NOTHING;

-- 3. Create Patient
INSERT INTO users (username, password, role, first_name, last_name, email) 
VALUES (
    'patient',
    'd4587ea9ead060c13fd994f21ecfa7926272a78854a2c20136b10a3c9e53e71e', -- patient123
    'patient',
    'Alice',
    'Johnson',
    'alice.j@example.com'
) ON CONFLICT (username) DO NOTHING;

-- Get patient id and insert into patients
INSERT INTO patients (patient_id, emergency_contact, insurance_info, blood_type)
SELECT id, 'Bob Johnson (555-0199)', 'Blue Cross #BC123456', 'O+'
FROM users WHERE username = 'patient'
ON CONFLICT (patient_id) DO NOTHING;

-- 4. Create an initial appointment
INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason, status)
SELECT 
    (SELECT id FROM users WHERE username = 'patient'),
    (SELECT id FROM users WHERE username = 'doctor'),
    CURRENT_DATE + interval '1 day',
    '10:00',
    'Routine checkup for Alice Johnson',
    'scheduled'
ON CONFLICT DO NOTHING;

-- 5. Create an initial medical record
INSERT INTO medical_records (patient_id, doctor_id, visit_date, diagnosis, treatment, prescription, notes, visit_type)
SELECT 
    (SELECT id FROM users WHERE username = 'patient'),
    (SELECT id FROM users WHERE username = 'doctor'),
    CURRENT_DATE - interval '7 days',
    'Common Cold',
    'Rest and hydration',
    'Vitamin C, Acetaminophen',
    'Patient complained of mild fever and congestion.',
    'general'
ON CONFLICT DO NOTHING;
