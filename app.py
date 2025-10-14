#!/usr/bin/env python3
"""
Healthcare Portal - Flask Web Application
A comprehensive healthcare management system with role-based access control.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import os
import hashlib
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client
import re
from functools import wraps

# Load environment variables
load_dotenv()

class HealthcareApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.setup_config()
        self.setup_database()
        self.setup_routes()
    
    def setup_config(self):
        """Configure Flask app"""
        self.app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
        self.app.config['SESSION_TIMEOUT'] = int(os.getenv('SESSION_TIMEOUT', 3600))
        self.app.config['PASSWORD_MIN_LENGTH'] = int(os.getenv('PASSWORD_MIN_LENGTH', 8))
        self.app.config['MAX_LOGIN_ATTEMPTS'] = int(os.getenv('MAX_LOGIN_ATTEMPTS', 5))
        
        # Session configuration
        self.app.permanent_session_lifetime = timedelta(seconds=self.app.config['SESSION_TIMEOUT'])
    
    def setup_database(self):
        """Initialize Supabase connection"""
        try:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_ANON_KEY")
            
            if not url or not key:
                raise ValueError("Supabase URL and ANON_KEY must be set in .env file")
            
            self.supabase = create_client(url, key)
            print("✅ Connected to Supabase database")
            
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            self.supabase = None
    
    # Utility Functions
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def validate_password(self, password: str) -> tuple[bool, str]:
        """Validate password strength"""
        min_length = self.app.config['PASSWORD_MIN_LENGTH']
        
        if len(password) < min_length:
            return False, f"Password must be at least {min_length} characters long"
        
        if not re.search(r"[A-Za-z]", password):
            return False, "Password must contain at least one letter"
        
        if not re.search(r"[0-9]", password):
            return False, "Password must contain at least one number"
        
        return True, ""
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def log_action(self, user_id: int, action: str, table_name: str = None, record_id: int = None):
        """Log user actions for audit purposes"""
        try:
            if self.supabase:
                log_data = {
                    "user_id": user_id,
                    "action": action,
                    "table_name": table_name,
                    "record_id": record_id,
                    "ip_address": request.remote_addr,
                    "user_agent": request.headers.get('User-Agent', '')[:500]
                }
                self.supabase.table("audit_logs").insert(log_data).execute()
        except Exception as e:
            print(f"Warning: Could not log action: {e}")
    
    # Authentication Decorators
    def login_required(self, f):
        """Decorator to require login"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    
    def role_required(self, *roles):
        """Decorator to require specific roles"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if 'user_id' not in session:
                    flash('Please log in to access this page.', 'warning')
                    return redirect(url_for('login'))
                
                if session.get('role') not in roles:
                    flash('You do not have permission to access this page.', 'danger')
                    return redirect(url_for('dashboard'))
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def setup_routes(self):
        """Set up all Flask routes"""
        
        @self.app.route('/')
        def index():
            """Home page"""
            return render_template('index.html')
        
        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            """Login page and processing"""
            if request.method == 'POST':
                username = request.form.get('username', '').strip()
                password = request.form.get('password', '')
                
                if not username or not password:
                    flash('Please enter both username and password.', 'danger')
                    return render_template('login.html')
                
                try:
                    hashed_password = self.hash_password(password)
                    
                    # Check user credentials
                    result = self.supabase.table("users").select(
                        "id, username, role, first_name, last_name, email"
                    ).eq("username", username).eq("password", hashed_password).execute()
                    
                    if result.data:
                        user = result.data[0]
                        
                        # Create session
                        session.permanent = True
                        session['user_id'] = user['id']
                        session['username'] = user['username']
                        session['role'] = user['role']
                        session['first_name'] = user['first_name']
                        session['last_name'] = user['last_name']
                        
                        # Log the login
                        self.log_action(user['id'], "USER_LOGIN", "users", user['id'])
                        
                        flash(f'Welcome, {user["first_name"]}!', 'success')
                        return redirect(url_for('dashboard'))
                    else:
                        flash('Invalid username or password.', 'danger')
                        
                except Exception as e:
                    flash(f'Login error: {str(e)}', 'danger')
            
            return render_template('login.html')
        
        @self.app.route('/register', methods=['GET', 'POST'])
        def register():
            """Registration page and processing"""
            if request.method == 'POST':
                # Get form data
                username = request.form.get('username', '').strip()
                password = request.form.get('password', '')
                confirm_password = request.form.get('confirm_password', '')
                role = request.form.get('role', '')
                email = request.form.get('email', '').strip()
                first_name = request.form.get('first_name', '').strip()
                last_name = request.form.get('last_name', '').strip()
                phone_number = request.form.get('phone_number', '').strip() or None
                address = request.form.get('address', '').strip() or None
                
                # Validation
                if not all([username, password, role, first_name, last_name]):
                    flash('Please fill in all required fields.', 'danger')
                    return render_template('register.html')
                
                if password != confirm_password:
                    flash('Passwords do not match.', 'danger')
                    return render_template('register.html')
                
                # Validate password strength
                is_valid, error_msg = self.validate_password(password)
                if not is_valid:
                    flash(error_msg, 'danger')
                    return render_template('register.html')
                
                # Validate email if provided
                if email and not self.validate_email(email):
                    flash('Please enter a valid email address.', 'danger')
                    return render_template('register.html')
                
                if role not in ['patient', 'nurse', 'doctor', 'administrator']:
                    flash('Invalid role selected.', 'danger')
                    return render_template('register.html')
                
                try:
                    # Check if username already exists
                    existing_user = self.supabase.table("users").select("id").eq("username", username).execute()
                    if existing_user.data:
                        flash('Username already exists. Please choose another.', 'danger')
                        return render_template('register.html')
                    
                    # Check if email already exists
                    if email:
                        existing_email = self.supabase.table("users").select("id").eq("email", email).execute()
                        if existing_email.data:
                            flash('Email already registered. Please use another.', 'danger')
                            return render_template('register.html')
                    
                    # Create user
                    hashed_password = self.hash_password(password)
                    user_data = {
                        "username": username,
                        "password": hashed_password,
                        "role": role,
                        "email": email,
                        "first_name": first_name,
                        "last_name": last_name,
                        "phone_number": phone_number,
                        "address": address
                    }
                    
                    result = self.supabase.table("users").insert(user_data).execute()
                    
                    if result.data:
                        user_id = result.data[0]["id"]
                        
                        # Insert into role-specific tables
                        if role == 'patient':
                            emergency_contact = request.form.get('emergency_contact', '').strip() or None
                            insurance_info = request.form.get('insurance_info', '').strip() or None
                            blood_type = request.form.get('blood_type', '').strip() or None
                            
                            patient_data = {
                                "patient_id": user_id,
                                "emergency_contact": emergency_contact,
                                "insurance_info": insurance_info,
                                "blood_type": blood_type
                            }
                            self.supabase.table("patients").insert(patient_data).execute()
                        
                        elif role in ['doctor', 'nurse']:
                            specialization = request.form.get('specialization', '').strip() or ("Nursing" if role == 'nurse' else None)
                            license_number = request.form.get('license_number', '').strip() or None
                            department = request.form.get('department', '').strip() or None
                            
                            staff_data = {
                                "staff_id": user_id,
                                "specialization": specialization,
                                "license_number": license_number,
                                "hire_date": datetime.now().date().isoformat(),
                                "department": department,
                                "status": "active"
                            }
                            self.supabase.table("medical_staff").insert(staff_data).execute()
                        
                        # Log the registration
                        self.log_action(user_id, "USER_REGISTERED", "users", user_id)
                        
                        flash(f'Registration successful! Welcome, {first_name}!', 'success')
                        return redirect(url_for('login'))
                    else:
                        flash('Registration failed. Please try again.', 'danger')
                        
                except Exception as e:
                    flash(f'Registration error: {str(e)}', 'danger')
            
            return render_template('register.html')
        
        @self.app.route('/logout')
        def logout():
            """Logout and clear session"""
            if 'user_id' in session:
                self.log_action(session['user_id'], "USER_LOGOUT", "users", session['user_id'])
            
            session.clear()
            flash('You have been logged out successfully.', 'info')
            return redirect(url_for('index'))
        
        @self.app.route('/dashboard')
        @self.login_required
        def dashboard():
            """Main dashboard - redirects based on user role"""
            role = session.get('role')
            
            if role == 'patient':
                return redirect(url_for('patient_dashboard'))
            elif role == 'nurse':
                return redirect(url_for('nurse_dashboard'))
            elif role == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            elif role == 'administrator':
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid user role.', 'danger')
                return redirect(url_for('logout'))
        
        @self.app.route('/patient/dashboard')
        @self.role_required('patient')
        def patient_dashboard():
            """Patient dashboard"""
            try:
                user_id = session['user_id']
                
                # Get patient info
                patient_result = self.supabase.table("patients").select("*").eq("patient_id", user_id).execute()
                patient_info = patient_result.data[0] if patient_result.data else {}
                
                # Get recent medical records
                records_result = self.supabase.table("medical_records").select(
                    "*, users!doctor_id(first_name, last_name)"
                ).eq("patient_id", user_id).order("visit_date", desc=True).limit(5).execute()
                
                # Get upcoming appointments
                appointments_result = self.supabase.table("appointments").select(
                    "*, users!doctor_id(first_name, last_name)"
                ).eq("patient_id", user_id).gte(
                    "appointment_date", datetime.now().isoformat()
                ).order("appointment_date", desc=False).limit(5).execute()
                
                return render_template('patient/dashboard.html', 
                                     patient_info=patient_info,
                                     medical_records=records_result.data,
                                     appointments=appointments_result.data)
            except Exception as e:
                flash(f'Error loading dashboard: {str(e)}', 'danger')
                return render_template('patient/dashboard.html', 
                                     patient_info={}, medical_records=[], appointments=[])
        
        @self.app.route('/doctor/dashboard')
        @self.role_required('doctor')
        def doctor_dashboard():
            """Doctor dashboard"""
            try:
                user_id = session['user_id']
                
                # Get doctor info
                doctor_result = self.supabase.table("medical_staff").select("*").eq("staff_id", user_id).execute()
                doctor_info = doctor_result.data[0] if doctor_result.data else {}
                
                # Get today's appointments
                today = datetime.now().date()
                appointments_result = self.supabase.table("appointments").select(
                    "*, users!patient_id(first_name, last_name)"
                ).eq("doctor_id", user_id).gte(
                    "appointment_date", today.isoformat()
                ).lte(
                    "appointment_date", (today + timedelta(days=1)).isoformat()
                ).order("appointment_date", desc=False).execute()
                
                # Get recent patients
                patients_result = self.supabase.table("medical_records").select(
                    "patient_id, users!patient_id(first_name, last_name, id)"
                ).eq("doctor_id", user_id).order("visit_date", desc=True).limit(10).execute()
                
                # Remove duplicates
                seen_patients = set()
                unique_patients = []
                for record in patients_result.data:
                    patient_id = record['patient_id']
                    if patient_id not in seen_patients:
                        seen_patients.add(patient_id)
                        unique_patients.append(record['users'])
                
                return render_template('doctor/dashboard.html',
                                     doctor_info=doctor_info,
                                     appointments=appointments_result.data,
                                     recent_patients=unique_patients[:5])
            except Exception as e:
                flash(f'Error loading dashboard: {str(e)}', 'danger')
                return render_template('doctor/dashboard.html',
                                     doctor_info={}, appointments=[], recent_patients=[])
        
        @self.app.route('/nurse/dashboard')
        @self.role_required('nurse')
        def nurse_dashboard():
            """Nurse dashboard"""
            try:
                user_id = session['user_id']
                
                # Get nurse info
                nurse_result = self.supabase.table("medical_staff").select("*").eq("staff_id", user_id).execute()
                nurse_info = nurse_result.data[0] if nurse_result.data else {}
                
                # Get today's appointments (for the department or all)
                today = datetime.now().date()
                appointments_result = self.supabase.table("appointments").select(
                    "*, patient:users!patient_id(first_name, last_name), doctor:users!doctor_id(first_name, last_name)"
                ).gte(
                    "appointment_date", today.isoformat()
                ).lte(
                    "appointment_date", (today + timedelta(days=1)).isoformat()
                ).order("appointment_date", desc=False).limit(20).execute()
                
                # Get recent patients
                patients_result = self.supabase.table("users").select(
                    "id, first_name, last_name, phone_number"
                ).eq("role", "patient").order("created_at", desc=True).limit(10).execute()
                
                return render_template('nurse/dashboard.html',
                                     nurse_info=nurse_info,
                                     appointments=appointments_result.data,
                                     recent_patients=patients_result.data)
            except Exception as e:
                flash(f'Error loading dashboard: {str(e)}', 'danger')
                return render_template('nurse/dashboard.html',
                                     nurse_info={}, appointments=[], recent_patients=[])
        
        @self.app.route('/admin/dashboard')
        @self.role_required('administrator')
        def admin_dashboard():
            """Administrator dashboard"""
            try:
                # Get system statistics
                patients_count = self.supabase.table("users").select("id", count="exact").eq("role", "patient").execute()
                doctors_count = self.supabase.table("users").select("id", count="exact").eq("role", "doctor").execute()
                nurses_count = self.supabase.table("users").select("id", count="exact").eq("role", "nurse").execute()
                admins_count = self.supabase.table("users").select("id", count="exact").eq("role", "administrator").execute()
                
                appointments_count = self.supabase.table("appointments").select("id", count="exact").execute()
                records_count = self.supabase.table("medical_records").select("id", count="exact").execute()
                
                # Get recent activity
                recent_users = self.supabase.table("users").select(
                    "id, username, role, first_name, last_name, created_at"
                ).order("created_at", desc=True).limit(10).execute()
                
                recent_logs = self.supabase.table("audit_logs").select(
                    "*, users(username, first_name, last_name)"
                ).order("created_at", desc=True).limit(15).execute()
                
                stats = {
                    'patients': patients_count.count,
                    'doctors': doctors_count.count,
                    'nurses': nurses_count.count,
                    'administrators': admins_count.count,
                    'appointments': appointments_count.count,
                    'medical_records': records_count.count,
                    'total_users': patients_count.count + doctors_count.count + nurses_count.count + admins_count.count
                }
                
                return render_template('admin/dashboard.html',
                                     stats=stats,
                                     recent_users=recent_users.data,
                                     recent_logs=recent_logs.data)
            except Exception as e:
                flash(f'Error loading dashboard: {str(e)}', 'danger')
                return render_template('admin/dashboard.html',
                                     stats={}, recent_users=[], recent_logs=[])
        
        # API Routes
        @self.app.route('/api/patients')
        @self.role_required('doctor', 'nurse', 'administrator')
        def api_patients():
            """API endpoint to get patients list"""
            try:
                result = self.supabase.table("users").select(
                    "id, first_name, last_name, email, phone_number, created_at"
                ).eq("role", "patient").order("first_name", desc=False).execute()
                
                return jsonify({
                    'success': True,
                    'data': result.data
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/appointments/<int:user_id>')
        @self.login_required
        def api_user_appointments(user_id):
            """API endpoint to get user's appointments"""
            try:
                # Check if user can access this data
                if session['role'] == 'patient' and session['user_id'] != user_id:
                    return jsonify({'success': False, 'error': 'Unauthorized'}), 403
                
                if session['role'] == 'patient':
                    result = self.supabase.table("appointments").select(
                        "*, users!doctor_id(first_name, last_name)"
                    ).eq("patient_id", user_id).order("appointment_date", desc=False).execute()
                elif session['role'] == 'doctor':
                    result = self.supabase.table("appointments").select(
                        "*, users!patient_id(first_name, last_name)"
                    ).eq("doctor_id", session['user_id']).order("appointment_date", desc=False).execute()
                else:
                    # Nurse or Admin
                    result = self.supabase.table("appointments").select(
                        "*, patient:users!patient_id(first_name, last_name), doctor:users!doctor_id(first_name, last_name)"
                    ).order("appointment_date", desc=False).limit(50).execute()
                
                return jsonify({
                    'success': True,
                    'data': result.data
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/appointments/<int:appointment_id>/status', methods=['PATCH'])
        @self.role_required('doctor', 'nurse', 'administrator')
        def update_appointment_status(appointment_id):
            """API endpoint to update appointment status"""
            try:
                data = request.get_json()
                new_status = data.get('status')

                if not new_status:
                    return jsonify({
                        'success': False,
                        'error': 'Status is required'
                    }), 400

                if new_status not in ['scheduled', 'completed', 'cancelled', 'no_show']:
                    return jsonify({
                        'success': False,
                        'error': 'Invalid status'
                    }), 400

                # Update the appointment
                result = self.supabase.table("appointments").update({
                    'status': new_status
                }).eq("id", appointment_id).execute()

                if result.data:
                    # Log the action
                    self.log_action(session['user_id'], f"APPOINTMENT_STATUS_UPDATED_{new_status.upper()}",
                                  "appointments", appointment_id)

                    return jsonify({
                        'success': True,
                        'message': 'Status updated successfully'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to update status'
                    }), 500

            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/vital-signs', methods=['POST'])
        @self.role_required('nurse', 'doctor', 'administrator')
        def record_vital_signs():
            """API endpoint to record patient vital signs"""
            try:
                patient_id = request.form.get('patient_id')
                temperature = request.form.get('temperature')
                blood_pressure = request.form.get('blood_pressure')
                pulse = request.form.get('pulse')
                respiratory_rate = request.form.get('respiratory_rate')
                oxygen_saturation = request.form.get('oxygen_saturation')
                notes = request.form.get('notes', '').strip()

                if not patient_id:
                    return jsonify({
                        'success': False,
                        'error': 'Patient ID is required'
                    }), 400

                # Create vital signs record as a medical record
                vital_signs_data = {
                    'patient_id': int(patient_id),
                    'doctor_id': session['user_id'],  # Nurse recording, using their ID
                    'visit_date': datetime.now().isoformat(),
                    'visit_type': 'vital_signs',
                    'notes': f"""Vital Signs Recorded by {session.get('first_name', 'Nurse')}:
Temperature: {temperature}°F
Blood Pressure: {blood_pressure}
Pulse: {pulse} bpm
Respiratory Rate: {respiratory_rate}
Oxygen Saturation: {oxygen_saturation}%

Additional Notes: {notes if notes else 'None'}"""
                }

                result = self.supabase.table("medical_records").insert(vital_signs_data).execute()

                if result.data:
                    self.log_action(session['user_id'], "VITAL_SIGNS_RECORDED", "medical_records", result.data[0]['id'])
                    return jsonify({
                        'success': True,
                        'message': 'Vital signs recorded successfully'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to record vital signs'
                    }), 500

            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/patient-notes', methods=['POST'])
        @self.role_required('nurse', 'doctor', 'administrator')
        def add_patient_notes():
            """API endpoint to add patient notes"""
            try:
                patient_id = request.form.get('patient_id')
                note_type = request.form.get('note_type')
                notes = request.form.get('notes', '').strip()

                if not all([patient_id, note_type, notes]):
                    return jsonify({
                        'success': False,
                        'error': 'All fields are required'
                    }), 400

                # Create note as a medical record
                note_data = {
                    'patient_id': int(patient_id),
                    'doctor_id': session['user_id'],
                    'visit_date': datetime.now().isoformat(),
                    'visit_type': note_type,
                    'notes': f"""Note Type: {note_type.replace('_', ' ').title()}
Recorded by: {session.get('first_name', 'Staff')} {session.get('last_name', '')} ({session.get('role', 'staff').title()})

{notes}"""
                }

                result = self.supabase.table("medical_records").insert(note_data).execute()

                if result.data:
                    self.log_action(session['user_id'], f"NOTE_ADDED_{note_type.upper()}", "medical_records", result.data[0]['id'])
                    return jsonify({
                        'success': True,
                        'message': 'Notes added successfully'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to add notes'
                    }), 500

            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        # Profile Management
        @self.app.route('/profile', methods=['GET', 'POST'])
        @self.login_required
        def profile():
            """User profile management"""
            if request.method == 'POST':
                try:
                    user_id = session['user_id']
                    
                    # Get form data
                    first_name = request.form.get('first_name', '').strip()
                    last_name = request.form.get('last_name', '').strip()
                    email = request.form.get('email', '').strip()
                    phone_number = request.form.get('phone_number', '').strip() or None
                    address = request.form.get('address', '').strip() or None
                    
                    # Validate email if provided
                    if email and not self.validate_email(email):
                        flash('Please enter a valid email address.', 'danger')
                        return redirect(url_for('profile'))
                    
                    # Update user data
                    update_data = {
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'phone_number': phone_number,
                        'address': address
                    }
                    
                    result = self.supabase.table("users").update(update_data).eq("id", user_id).execute()
                    
                    if result.data:
                        # Update session data
                        session['first_name'] = first_name
                        session['last_name'] = last_name
                        
                        self.log_action(user_id, "PROFILE_UPDATED", "users", user_id)
                        flash('Profile updated successfully!', 'success')
                    else:
                        flash('Failed to update profile.', 'danger')
                        
                except Exception as e:
                    flash(f'Error updating profile: {str(e)}', 'danger')
            
            # Get current user data
            try:
                user_id = session['user_id']
                result = self.supabase.table("users").select("*").eq("id", user_id).execute()
                user_data = result.data[0] if result.data else {}
                
                # Get role-specific data
                role_data = {}
                if session['role'] == 'patient':
                    patient_result = self.supabase.table("patients").select("*").eq("patient_id", user_id).execute()
                    role_data = patient_result.data[0] if patient_result.data else {}
                elif session['role'] in ['doctor', 'nurse']:
                    staff_result = self.supabase.table("medical_staff").select("*").eq("staff_id", user_id).execute()
                    role_data = staff_result.data[0] if staff_result.data else {}
                
                return render_template('profile.html', user_data=user_data, role_data=role_data)
            except Exception as e:
                flash(f'Error loading profile: {str(e)}', 'danger')
                return render_template('profile.html', user_data={}, role_data={})
        
        # Appointments Management
        @self.app.route('/appointments')
        @self.login_required
        def appointments():
            """View all appointments"""
            try:
                user_id = session['user_id']
                role = session['role']

                if role == 'patient':
                    result = self.supabase.table("appointments").select(
                        "*, doctor:users!doctor_id(first_name, last_name)"
                    ).eq("patient_id", user_id).order("appointment_date", desc=False).execute()
                elif role == 'doctor':
                    result = self.supabase.table("appointments").select(
                        "*, patient:users!patient_id(first_name, last_name)"
                    ).eq("doctor_id", user_id).order("appointment_date", desc=False).execute()
                else:  # nurse or admin
                    result = self.supabase.table("appointments").select(
                        "*, patient:users!patient_id(first_name, last_name), doctor:users!doctor_id(first_name, last_name)"
                    ).order("appointment_date", desc=False).limit(100).execute()

                return render_template('appointments/list.html', appointments=result.data)
            except Exception as e:
                flash(f'Error loading appointments: {str(e)}', 'danger')
                return render_template('appointments/list.html', appointments=[])

        @self.app.route('/appointments/book', methods=['GET', 'POST'])
        @self.login_required
        def book_appointment():
            """Book a new appointment"""
            if request.method == 'POST':
                try:
                    patient_id = session['user_id'] if session['role'] == 'patient' else request.form.get('patient_id')
                    doctor_id = request.form.get('doctor_id')
                    appointment_date = request.form.get('appointment_date')
                    appointment_time = request.form.get('appointment_time')
                    reason = request.form.get('reason', '').strip()

                    if not all([patient_id, doctor_id, appointment_date]):
                        flash('Please fill in all required fields.', 'danger')
                        return redirect(url_for('book_appointment'))

                    appointment_data = {
                        'patient_id': int(patient_id),
                        'doctor_id': int(doctor_id),
                        'appointment_date': appointment_date,
                        'appointment_time': appointment_time,
                        'reason': reason,
                        'status': 'scheduled'
                    }

                    result = self.supabase.table("appointments").insert(appointment_data).execute()

                    if result.data:
                        self.log_action(session['user_id'], "APPOINTMENT_BOOKED", "appointments", result.data[0]['id'])
                        flash('Appointment booked successfully!', 'success')
                        return redirect(url_for('appointments'))
                    else:
                        flash('Failed to book appointment.', 'danger')

                except Exception as e:
                    flash(f'Error booking appointment: {str(e)}', 'danger')

            # Get list of doctors and patients for the form
            try:
                # Get doctors
                doctors_result = self.supabase.table("users").select(
                    "id, first_name, last_name"
                ).eq("role", "doctor").execute()

                # Try to get specializations from medical_staff table
                doctors = []
                if doctors_result.data:
                    for doc in doctors_result.data:
                        specialization = 'General Practice'
                        try:
                            # Try to fetch specialization
                            staff_result = self.supabase.table("medical_staff").select(
                                "specialization"
                            ).eq("staff_id", doc['id']).execute()
                            if staff_result.data and len(staff_result.data) > 0:
                                specialization = staff_result.data[0].get('specialization', 'General Practice')
                        except:
                            pass  # Use default if medical_staff table doesn't exist or error occurs

                        doctor_data = {
                            'id': doc['id'],
                            'first_name': doc['first_name'],
                            'last_name': doc['last_name'],
                            'specialization': specialization
                        }
                        doctors.append(doctor_data)

                patients = []
                if session['role'] != 'patient':
                    patients = self.supabase.table("users").select("id, first_name, last_name").eq("role", "patient").execute()

                return render_template('appointments/book.html',
                                     doctors=doctors,
                                     patients=patients.data if patients else [])
            except Exception as e:
                flash(f'Error loading form: {str(e)}', 'danger')
                return render_template('appointments/book.html', doctors=[], patients=[])

        @self.app.route('/appointments/<int:appointment_id>')
        @self.login_required
        def appointment_details(appointment_id):
            """View appointment details"""
            try:
                user_id = session['user_id']
                role = session['role']

                # Get appointment with patient and doctor info
                appointment = self.supabase.table("appointments").select("*").eq("id", appointment_id).execute()

                if not appointment.data:
                    flash('Appointment not found.', 'danger')
                    return redirect(url_for('appointments'))

                appointment = appointment.data[0]

                # Check if user has permission to view this appointment
                if role == 'patient' and appointment['patient_id'] != user_id:
                    flash('You do not have permission to view this appointment.', 'danger')
                    return redirect(url_for('appointments'))

                if role == 'doctor' and appointment['doctor_id'] != user_id:
                    flash('You do not have permission to view this appointment.', 'danger')
                    return redirect(url_for('appointments'))

                # Get patient information
                patient = self.supabase.table("users").select(
                    "id, first_name, last_name, email, phone_number"
                ).eq("id", appointment['patient_id']).execute()
                patient = patient.data[0] if patient.data else None

                # Get doctor information
                doctor = self.supabase.table("users").select(
                    "id, first_name, last_name, email, phone_number"
                ).eq("id", appointment['doctor_id']).execute()
                doctor = doctor.data[0] if doctor.data else None

                # Get related medical records (if staff or admin)
                medical_records = []
                if role in ['doctor', 'nurse', 'administrator']:
                    records_result = self.supabase.table("medical_records").select(
                        "*, users!doctor_id(first_name, last_name)"
                    ).eq("patient_id", appointment['patient_id']).order("visit_date", desc=True).limit(5).execute()
                    medical_records = records_result.data if records_result.data else []

                return render_template('appointments/details.html',
                                     appointment=appointment,
                                     patient=patient,
                                     doctor=doctor,
                                     medical_records=medical_records)

            except Exception as e:
                flash(f'Error loading appointment details: {str(e)}', 'danger')
                return redirect(url_for('appointments'))

        # Patients Management
        @self.app.route('/patients')
        @self.role_required('doctor', 'nurse', 'administrator')
        def patients_list():
            """View list of all patients"""
            try:
                result = self.supabase.table("users").select(
                    "id, first_name, last_name, email, phone_number, address, created_at"
                ).eq("role", "patient").order("first_name", desc=False).execute()

                return render_template('patients/list.html', patients=result.data)
            except Exception as e:
                flash(f'Error loading patients: {str(e)}', 'danger')
                return render_template('patients/list.html', patients=[])

        @self.app.route('/patients/<int:patient_id>')
        @self.role_required('doctor', 'nurse', 'administrator')
        def patient_details(patient_id):
            """View patient details"""
            try:
                # Get patient info
                user_result = self.supabase.table("users").select("*").eq("id", patient_id).eq("role", "patient").execute()
                if not user_result.data:
                    flash('Patient not found.', 'danger')
                    return redirect(url_for('patients_list'))

                patient_data = user_result.data[0]

                # Get patient-specific info
                patient_info = self.supabase.table("patients").select("*").eq("patient_id", patient_id).execute()

                # Get medical records
                records = self.supabase.table("medical_records").select(
                    "*, users!doctor_id(first_name, last_name)"
                ).eq("patient_id", patient_id).order("visit_date", desc=True).execute()

                # Get appointments
                appointments = self.supabase.table("appointments").select(
                    "*, users!doctor_id(first_name, last_name)"
                ).eq("patient_id", patient_id).order("appointment_date", desc=False).execute()

                return render_template('patients/details.html',
                                     patient=patient_data,
                                     patient_info=patient_info.data[0] if patient_info.data else {},
                                     medical_records=records.data,
                                     appointments=appointments.data)
            except Exception as e:
                flash(f'Error loading patient details: {str(e)}', 'danger')
                return redirect(url_for('patients_list'))

        # Medical Records
        @self.app.route('/medical-records')
        @self.login_required
        def medical_records():
            """View medical records"""
            try:
                user_id = session['user_id']
                role = session['role']

                if role == 'patient':
                    result = self.supabase.table("medical_records").select(
                        "*, users!doctor_id(first_name, last_name)"
                    ).eq("patient_id", user_id).order("visit_date", desc=True).execute()
                elif role == 'doctor':
                    result = self.supabase.table("medical_records").select(
                        "*, users!patient_id(first_name, last_name)"
                    ).eq("doctor_id", user_id).order("visit_date", desc=True).execute()
                else:  # nurse or admin
                    result = self.supabase.table("medical_records").select(
                        "*, patient:users!patient_id(first_name, last_name), doctor:users!doctor_id(first_name, last_name)"
                    ).order("visit_date", desc=True).limit(100).execute()

                return render_template('medical_records/list.html', records=result.data)
            except Exception as e:
                flash(f'Error loading medical records: {str(e)}', 'danger')
                return render_template('medical_records/list.html', records=[])

        @self.app.route('/medical-records/add', methods=['GET', 'POST'])
        @self.role_required('doctor', 'nurse')
        def add_medical_record():
            """Add a new medical record"""
            if request.method == 'POST':
                try:
                    patient_id = request.form.get('patient_id')
                    doctor_id = session['user_id'] if session['role'] == 'doctor' else request.form.get('doctor_id')
                    visit_date = request.form.get('visit_date')
                    symptoms = request.form.get('symptoms', '').strip()
                    diagnosis = request.form.get('diagnosis', '').strip()
                    treatment = request.form.get('treatment', '').strip()
                    prescription = request.form.get('prescription', '').strip()
                    notes = request.form.get('notes', '').strip()
                    visit_type = request.form.get('visit_type', 'general')

                    if not all([patient_id, doctor_id, visit_date]):
                        flash('Please fill in all required fields.', 'danger')
                        return redirect(url_for('add_medical_record'))

                    record_data = {
                        'patient_id': int(patient_id),
                        'doctor_id': int(doctor_id),
                        'visit_date': visit_date,
                        'symptoms': symptoms,
                        'diagnosis': diagnosis,
                        'treatment': treatment,
                        'prescription': prescription,
                        'notes': notes,
                        'visit_type': visit_type
                    }

                    result = self.supabase.table("medical_records").insert(record_data).execute()

                    if result.data:
                        self.log_action(session['user_id'], "MEDICAL_RECORD_CREATED", "medical_records", result.data[0]['id'])
                        flash('Medical record added successfully!', 'success')
                        return redirect(url_for('medical_records'))
                    else:
                        flash('Failed to add medical record.', 'danger')

                except Exception as e:
                    flash(f'Error adding medical record: {str(e)}', 'danger')

            # Get lists for the form
            try:
                patients = self.supabase.table("users").select("id, first_name, last_name").eq("role", "patient").execute()
                doctors = []
                if session['role'] == 'nurse':
                    doctors = self.supabase.table("users").select("id, first_name, last_name").eq("role", "doctor").execute()

                return render_template('medical_records/add.html',
                                     patients=patients.data if patients else [],
                                     doctors=doctors.data if doctors else [])
            except Exception as e:
                flash(f'Error loading form: {str(e)}', 'danger')
                return render_template('medical_records/add.html', patients=[], doctors=[])

        # Error Handlers
        @self.app.errorhandler(404)
        def not_found(error):
            return render_template('errors/404.html'), 404

        @self.app.errorhandler(500)
        def internal_error(error):
            return render_template('errors/500.html'), 500

        @self.app.errorhandler(403)
        def forbidden(error):
            return render_template('errors/403.html'), 403

    def run(self, debug=True, host='127.0.0.1', port=5000):
        """Run the Flask application"""
        if not self.supabase:
            print("❌ Cannot start application: Database connection failed")
            return
        
        print(f"🏥 Starting Healthcare Portal...")
        print(f"🌐 Server running at: http://{host}:{port}")
        print(f"🔧 Debug mode: {debug}")
        
        self.app.run(debug=debug, host=host, port=port)

# Create and run the application
if __name__ == "__main__":
    healthcare_app = HealthcareApp()
    healthcare_app.run(debug=True)