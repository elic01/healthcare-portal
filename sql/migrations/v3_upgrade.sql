-- ============================================================================
-- Healthcare Portal - Database Migration to v3.0
-- ============================================================================
-- This script upgrades the database schema from v2.0 to v3.0
-- Execute this entire script in your Supabase SQL Editor
-- Date: 2025-10-14
-- ============================================================================

-- ============================================================================
-- 1. NEW TABLES FOR v3.0 FEATURES
-- ============================================================================

-- Messages table (patient-doctor communication)
CREATE TABLE IF NOT EXISTS messages (
    id BIGSERIAL PRIMARY KEY,
    sender_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recipient_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE,
    parent_message_id BIGINT REFERENCES messages(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Documents table (file uploads)
CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    patient_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL,  -- medical_record, prescription, lab_result, etc.
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    description TEXT,
    uploaded_by BIGINT REFERENCES users(id) ON DELETE SET NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Prescriptions table
CREATE TABLE IF NOT EXISTS prescriptions (
    id BIGSERIAL PRIMARY KEY,
    patient_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    doctor_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    medical_record_id BIGINT REFERENCES medical_records(id) ON DELETE SET NULL,
    medication_name VARCHAR(200) NOT NULL,
    dosage VARCHAR(100),
    frequency VARCHAR(100),
    duration VARCHAR(100),
    instructions TEXT,
    quantity INTEGER,
    refills_allowed INTEGER DEFAULT 0,
    refills_remaining INTEGER DEFAULT 0,
    start_date DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'cancelled', 'expired')),
    pharmacy_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Lab Results table
CREATE TABLE IF NOT EXISTS lab_results (
    id BIGSERIAL PRIMARY KEY,
    patient_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    doctor_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    test_name VARCHAR(200) NOT NULL,
    test_type VARCHAR(100),
    result_value VARCHAR(100),
    result_unit VARCHAR(50),
    reference_range VARCHAR(100),
    status VARCHAR(20) DEFAULT 'normal' CHECK (status IN ('normal', 'abnormal', 'critical', 'pending')),
    test_date DATE NOT NULL,
    result_date DATE,
    lab_name VARCHAR(200),
    notes TEXT,
    document_id BIGINT REFERENCES documents(id) ON DELETE SET NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL,  -- appointment, message, system, alert
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    link VARCHAR(500),
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE,
    priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Settings table
CREATE TABLE IF NOT EXISTS user_settings (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    dark_mode BOOLEAN DEFAULT FALSE,
    email_notifications BOOLEAN DEFAULT TRUE,
    sms_notifications BOOLEAN DEFAULT FALSE,
    language VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'UTC',
    items_per_page INTEGER DEFAULT 20,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    two_factor_secret VARCHAR(100),
    notification_preferences JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Password Reset Tokens table
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(100) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMP WITH TIME ZONE,
    ip_address INET,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Login Attempts table (for security)
CREATE TABLE IF NOT EXISTS login_attempts (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50),
    ip_address INET NOT NULL,
    user_agent TEXT,
    success BOOLEAN NOT NULL,
    failure_reason VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- 2. ALTER EXISTING TABLES - ADD NEW COLUMNS
-- ============================================================================

-- Add soft delete to users
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_changed_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS account_locked_until TIMESTAMP WITH TIME ZONE;

-- Add more fields to patients
ALTER TABLE patients ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE patients ADD COLUMN IF NOT EXISTS primary_doctor_id BIGINT REFERENCES users(id) ON DELETE SET NULL;
ALTER TABLE patients ADD COLUMN IF NOT EXISTS profile_image VARCHAR(500);

-- Add fields to medical_staff
ALTER TABLE medical_staff ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE medical_staff ADD COLUMN IF NOT EXISTS profile_image VARCHAR(500);
ALTER TABLE medical_staff ADD COLUMN IF NOT EXISTS bio TEXT;
ALTER TABLE medical_staff ADD COLUMN IF NOT EXISTS consultation_fee DECIMAL(10,2);

-- Add fields to appointments
ALTER TABLE appointments ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE appointments ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE appointments ADD COLUMN IF NOT EXISTS reminder_sent BOOLEAN DEFAULT FALSE;
ALTER TABLE appointments ADD COLUMN IF NOT EXISTS reminder_sent_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE appointments ADD COLUMN IF NOT EXISTS meeting_link VARCHAR(500);
ALTER TABLE appointments ADD COLUMN IF NOT EXISTS is_virtual BOOLEAN DEFAULT FALSE;

-- Add fields to medical_records
ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS follow_up_required BOOLEAN DEFAULT FALSE;
ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS follow_up_date DATE;
ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS vital_signs JSONB;

-- ============================================================================
-- 3. CREATE INDEXES FOR PERFORMANCE
-- ============================================================================

-- Messages indexes
CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_recipient ON messages(recipient_id);
CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_unread ON messages(recipient_id, is_read) WHERE is_read = FALSE;

-- Documents indexes
CREATE INDEX IF NOT EXISTS idx_documents_user ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_patient ON documents(patient_id);
CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(document_type);
CREATE INDEX IF NOT EXISTS idx_documents_active ON documents(is_deleted) WHERE is_deleted = FALSE;

-- Prescriptions indexes
CREATE INDEX IF NOT EXISTS idx_prescriptions_patient ON prescriptions(patient_id);
CREATE INDEX IF NOT EXISTS idx_prescriptions_doctor ON prescriptions(doctor_id);
CREATE INDEX IF NOT EXISTS idx_prescriptions_status ON prescriptions(status);
CREATE INDEX IF NOT EXISTS idx_prescriptions_active ON prescriptions(status) WHERE status = 'active';

-- Lab Results indexes
CREATE INDEX IF NOT EXISTS idx_lab_results_patient ON lab_results(patient_id);
CREATE INDEX IF NOT EXISTS idx_lab_results_date ON lab_results(test_date DESC);
CREATE INDEX IF NOT EXISTS idx_lab_results_status ON lab_results(status);
CREATE INDEX IF NOT EXISTS idx_lab_results_active ON lab_results(is_deleted) WHERE is_deleted = FALSE;

-- Notifications indexes
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;
CREATE INDEX IF NOT EXISTS idx_notifications_created ON notifications(created_at DESC);

-- Login Attempts indexes
CREATE INDEX IF NOT EXISTS idx_login_attempts_ip ON login_attempts(ip_address);
CREATE INDEX IF NOT EXISTS idx_login_attempts_username ON login_attempts(username);
CREATE INDEX IF NOT EXISTS idx_login_attempts_created ON login_attempts(created_at DESC);

-- Existing tables - add new indexes
CREATE INDEX IF NOT EXISTS idx_users_deleted ON users(is_deleted) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_users_last_login ON users(last_login DESC);
CREATE INDEX IF NOT EXISTS idx_patients_doctor ON patients(primary_doctor_id);
CREATE INDEX IF NOT EXISTS idx_appointments_virtual ON appointments(is_virtual) WHERE is_virtual = TRUE;

-- ============================================================================
-- 4. CREATE TRIGGERS FOR AUTOMATIC TIMESTAMPS
-- ============================================================================

CREATE TRIGGER update_messages_updated_at BEFORE UPDATE ON messages
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_prescriptions_updated_at BEFORE UPDATE ON prescriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_lab_results_updated_at BEFORE UPDATE ON lab_results
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_settings_updated_at BEFORE UPDATE ON user_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 5. CREATE VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Active appointments view
CREATE OR REPLACE VIEW active_appointments AS
SELECT
    a.*,
    u_patient.first_name || ' ' || u_patient.last_name as patient_name,
    u_doctor.first_name || ' ' || u_doctor.last_name as doctor_name
FROM appointments a
JOIN users u_patient ON a.patient_id = u_patient.id
JOIN users u_doctor ON a.doctor_id = u_doctor.id
WHERE a.is_deleted = FALSE
    AND a.status != 'cancelled'
ORDER BY a.appointment_date ASC;

-- Active prescriptions view
CREATE OR REPLACE VIEW active_prescriptions AS
SELECT
    p.*,
    u_patient.first_name || ' ' || u_patient.last_name as patient_name,
    u_doctor.first_name || ' ' || u_doctor.last_name as doctor_name
FROM prescriptions p
JOIN users u_patient ON p.patient_id = u_patient.id
JOIN users u_doctor ON p.doctor_id = u_doctor.id
WHERE p.status = 'active'
ORDER BY p.created_at DESC;

-- Unread messages view
CREATE OR REPLACE VIEW unread_messages AS
SELECT
    m.*,
    u_sender.first_name || ' ' || u_sender.last_name as sender_name,
    u_recipient.first_name || ' ' || u_recipient.last_name as recipient_name
FROM messages m
JOIN users u_sender ON m.sender_id = u_sender.id
JOIN users u_recipient ON m.recipient_id = u_recipient.id
WHERE m.is_read = FALSE
ORDER BY m.created_at DESC;

-- ============================================================================
-- 6. INSERT DEFAULT DATA
-- ============================================================================

-- Create default user settings for existing users
INSERT INTO user_settings (user_id, dark_mode, email_notifications)
SELECT id, FALSE, TRUE
FROM users
WHERE NOT EXISTS (
    SELECT 1 FROM user_settings WHERE user_settings.user_id = users.id
);

-- ============================================================================
-- 7. GRANT PERMISSIONS (If using RLS)
-- ============================================================================

-- Enable RLS on new tables
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE prescriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE lab_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;

-- Create policies (example for messages - users can only see their own)
CREATE POLICY messages_select_own ON messages
    FOR SELECT
    USING (sender_id = auth.uid() OR recipient_id = auth.uid());

CREATE POLICY messages_insert_own ON messages
    FOR INSERT
    WITH CHECK (sender_id = auth.uid());

-- ============================================================================
-- 8. DATA MIGRATION & CLEANUP
-- ============================================================================

-- Update existing appointments without time set
UPDATE appointments
SET appointment_time = EXTRACT(TIME FROM appointment_date)
WHERE appointment_time IS NULL;

-- Set password_changed_at for existing users
UPDATE users
SET password_changed_at = created_at
WHERE password_changed_at IS NULL;

-- ============================================================================
-- 9. CREATE FUNCTIONS FOR COMMON OPERATIONS
-- ============================================================================

-- Function to get unread message count
CREATE OR REPLACE FUNCTION get_unread_count(p_user_id BIGINT)
RETURNS INTEGER AS $$
BEGIN
    RETURN (SELECT COUNT(*)
            FROM messages
            WHERE recipient_id = p_user_id
            AND is_read = FALSE);
END;
$$ LANGUAGE plpgsql;

-- Function to mark notifications as read
CREATE OR REPLACE FUNCTION mark_notifications_read(p_user_id BIGINT)
RETURNS VOID AS $$
BEGIN
    UPDATE notifications
    SET is_read = TRUE,
        read_at = NOW()
    WHERE user_id = p_user_id
    AND is_read = FALSE;
END;
$$ LANGUAGE plpgsql;

-- Function to soft delete records
CREATE OR REPLACE FUNCTION soft_delete(
    p_table_name TEXT,
    p_record_id BIGINT
)
RETURNS VOID AS $$
BEGIN
    EXECUTE format('UPDATE %I SET is_deleted = TRUE, deleted_at = NOW() WHERE id = $1', p_table_name)
    USING p_record_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 10. VERIFICATION QUERIES
-- ============================================================================

-- Verify new tables were created
SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
AND table_name IN ('messages', 'documents', 'prescriptions', 'lab_results', 'notifications', 'user_settings', 'password_reset_tokens', 'login_attempts')
ORDER BY table_name;

-- Verify new columns were added
SELECT
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name IN ('users', 'patients', 'medical_staff', 'appointments', 'medical_records')
AND column_name IN ('is_deleted', 'deleted_at', 'last_login', 'profile_image')
ORDER BY table_name, column_name;

-- Count records
SELECT
    'users' as table_name, COUNT(*) as record_count FROM users
UNION ALL
SELECT 'messages', COUNT(*) FROM messages
UNION ALL
SELECT 'documents', COUNT(*) FROM documents
UNION ALL
SELECT 'prescriptions', COUNT(*) FROM prescriptions
UNION ALL
SELECT 'lab_results', COUNT(*) FROM lab_results
UNION ALL
SELECT 'notifications', COUNT(*) FROM notifications
UNION ALL
SELECT 'user_settings', COUNT(*) FROM user_settings;

-- ============================================================================
-- MIGRATION COMPLETE!
-- ============================================================================
--
-- Next steps:
-- 1. Verify all tables and columns were created
-- 2. Update application code to use new features
-- 3. Test thoroughly before deploying to production
-- 4. Update documentation
--
-- ============================================================================

SELECT '✅ Database migration to v3.0 completed successfully!' as status;
