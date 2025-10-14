-- Add missing columns to medical_records and appointments tables
-- Run this in your Supabase SQL Editor to fix the schema

-- ============================================
-- Fix medical_records table
-- ============================================

-- Add symptoms column
ALTER TABLE medical_records
ADD COLUMN IF NOT EXISTS symptoms TEXT;

-- Add visit_type column
ALTER TABLE medical_records
ADD COLUMN IF NOT EXISTS visit_type VARCHAR(50) DEFAULT 'general';

-- ============================================
-- Fix appointments table
-- ============================================

-- Add appointment_time column
ALTER TABLE appointments
ADD COLUMN IF NOT EXISTS appointment_time TIME;

-- ============================================
-- Verify the changes
-- ============================================

-- Verify medical_records columns
SELECT 'medical_records' as table_name, column_name, data_type
FROM information_schema.columns
WHERE table_name = 'medical_records'
ORDER BY ordinal_position;

-- Verify appointments columns
SELECT 'appointments' as table_name, column_name, data_type
FROM information_schema.columns
WHERE table_name = 'appointments'
ORDER BY ordinal_position;
