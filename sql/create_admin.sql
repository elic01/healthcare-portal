-- Delete the existing admin user (if any) and create a new one with the correct hash
DELETE FROM users WHERE username = 'admin';

-- Create admin user with correct SHA-256 hash for password 'admin123'
INSERT INTO users (username, password, role, first_name, last_name, email) 
VALUES (
    'admin',
    '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',
    'administrator',
    'System',
    'Administrator',
    'admin@pdms.com'
);

-- Verify the admin user was created
SELECT id, username, role, first_name, last_name, email FROM users WHERE username = 'admin';