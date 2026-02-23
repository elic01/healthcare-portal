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
import re
from functools import wraps
import psycopg2
from psycopg2.extras import RealDictCursor
from supabase import create_client, Client

# Load environment variables
load_dotenv()

class DatabaseManager:
    """Wrapper to support both Supabase and Local PostgreSQL"""
    def __init__(self, use_local=False):
        self.use_local = use_local
        self.supabase = None
        self.conn = None
        
        if use_local:
            self.setup_local()
        else:
            self.setup_supabase()

    def setup_supabase(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        if url and key:
            try:
                self.supabase = create_client(url, key)
                print("✅ Connected to Supabase")
            except Exception as e:
                print(f"❌ Supabase Connection Error: {e}")

    def setup_local(self):
        try:
            self.conn = psycopg2.connect(
                dbname=os.getenv("LOCAL_DB_NAME", "healthcare_portal"),
                user=os.getenv("LOCAL_DB_USER", "postgres"),
                password=os.getenv("LOCAL_DB_PASSWORD", "postgres"),
                host=os.getenv("LOCAL_DB_HOST", "localhost"),
                port=os.getenv("LOCAL_DB_PORT", "5432")
            )
            print("✅ Connected to Local PostgreSQL")
        except Exception as e:
            print(f"❌ Local DB Connection Error: {e}")

    def table(self, table_name):
        if not self.use_local and self.supabase:
            return self.supabase.table(table_name)
        return LocalQueryBuilder(self.conn, table_name)

class LocalQueryBuilder:
    """Minimal Query Builder to mimic Supabase syntax for local Postgres"""
    def __init__(self, conn, table_name):
        self.conn = conn
        self.table_name = table_name
        self.filters = []
        self.order_by = ""
        self.limit_val = None
        self.columns = "*"
        self.joins = []

    def select(self, columns="*", count=None):
        # Handle basic Supabase join syntax: "*, users!doctor_id(first_name, last_name)"
        if "!" in columns:
            # Very basic parsing for common healthcare portal joins
            # This is a hack to make the local DB work with existing templates
            self.columns = "*" 
            # In a real app, we'd parse this properly. For now, we'll just return everything
            # and the templates will need to be slightly more robust or we handle it in execute()
        else:
            self.columns = columns
        self.count_type = count
        return self

    def eq(self, column, value):
        self.filters.append((column, "=", value))
        return self

    def gte(self, column, value):
        self.filters.append((column, ">=", value))
        return self

    def lte(self, column, value):
        self.filters.append((column, "<=", value))
        return self

    def order(self, column, desc=False):
        direction = "DESC" if desc else "ASC"
        self.order_by = f"ORDER BY {column} {direction}"
        return self

    def limit(self, value):
        self.limit_val = value
        return self

    def execute(self):
        if not self.conn:
            return type('Result', (), {'data': [], 'count': 0})

        query = f"SELECT {self.columns} FROM {self.table_name}"
        params = []
        
        if self.filters:
            where_clauses = []
            for col, op, val in self.filters:
                where_clauses.append(f"{col} {op} %s")
                params.append(val)
            query += " WHERE " + " AND ".join(where_clauses)
        
        if self.order_by:
            query += f" {self.order_by}"
        if self.limit_val:
            query += f" LIMIT {self.limit_val}"
            
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                data = cur.fetchall()
                data_list = [dict(row) for row in data]
                
                # Convert datetime objects to strings for compatibility with Supabase API
                for item in data_list:
                    for key, value in item.items():
                        if isinstance(value, datetime):
                            item[key] = value.isoformat()

                # Mock Supabase-style nested objects for common joins if they exist as IDs
                for item in data_list:
                    # Mock 'users' join for doctor_id
                    if 'doctor_id' in item and item['doctor_id']:
                        cur.execute("SELECT first_name, last_name, id FROM users WHERE id = %s", (item['doctor_id'],))
                        user_data = cur.fetchone()
                        if user_data:
                            item['users'] = dict(user_data)
                            # Handle different alias expectations
                            item['doctor'] = dict(user_data)
                    
                    # Mock 'users' join for patient_id
                    if 'patient_id' in item and item['patient_id']:
                        cur.execute("SELECT first_name, last_name, id FROM users WHERE id = %s", (item['patient_id'],))
                        user_data = cur.fetchone()
                        if user_data:
                            item['patient'] = dict(user_data)
                            if 'users' not in item:
                                item['users'] = dict(user_data)

                count = len(data_list)
                if hasattr(self, 'count_type') and self.count_type == 'exact':
                    count_query = f"SELECT COUNT(*) FROM {self.table_name}"
                    if self.filters:
                        count_query += " WHERE " + " AND ".join([f"{col} {op} %s" for col, op, val in self.filters])
                        cur.execute(count_query, [val for col, op, val in self.filters])
                    else:
                        cur.execute(count_query)
                    count = cur.fetchone()['count']

                return type('Result', (), {'data': data_list, 'count': count})
        except Exception as e:
            print(f"SQL Error in {self.table_name}: {e}")
            return type('Result', (), {'data': [], 'count': 0})

    def insert(self, data):
        if not self.conn: return type('Result', (), {'data': []})
        if not isinstance(data, list): data = [data]
        
        results = []
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                for item in data:
                    columns = item.keys()
                    placeholders = ["%s"] * len(columns)
                    query = f"INSERT INTO {self.table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)}) RETURNING *"
                    cur.execute(query, list(item.values()))
                    results.append(dict(cur.fetchone()))
            self.conn.commit()
            return type('Result', (), {'data': results})
        except Exception as e:
            self.conn.rollback()
            print(f"Insert Error in {self.table_name}: {e}")
            return type('Result', (), {'data': []})

    def update(self, data):
        if not self.conn: return type('Result', (), {'data': []})
        results = []
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                set_clauses = [f"{k} = %s" for k in data.keys()]
                params = list(data.values())
                query = f"UPDATE {self.table_name} SET {', '.join(set_clauses)}"
                
                if self.filters:
                    where_clauses = [f"{col} {op} %s" for col, op, val in self.filters]
                    query += " WHERE " + " AND ".join(where_clauses)
                    params.extend([val for col, op, val in self.filters])
                
                query += " RETURNING *"
                cur.execute(query, params)
                results = [dict(row) for row in cur.fetchall()]
            self.conn.commit()
            return type('Result', (), {'data': results})
        except Exception as e:
            self.conn.rollback()
            print(f"Update Error in {self.table_name}: {e}")
            return type('Result', (), {'data': []})

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
        self.app.permanent_session_lifetime = timedelta(seconds=self.app.config['SESSION_TIMEOUT'])
    
    def setup_database(self):
        """Initialize Database connection"""
        use_local = os.getenv("USE_LOCAL_DB", "False").lower() == "true"
        self.db = DatabaseManager(use_local=use_local)
        # Compatibility layer
        self.supabase = self.db
    
    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def validate_password(self, password: str) -> tuple[bool, str]:
        min_length = self.app.config['PASSWORD_MIN_LENGTH']
        if len(password) < min_length:
            return False, f"Password must be at least {min_length} characters long"
        if not re.search(r"[A-Za-z]", password):
            return False, "Password must contain at least one letter"
        if not re.search(r"[0-9]", password):
            return False, "Password must contain at least one number"
        return True, ""
    
    def validate_email(self, email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def log_action(self, user_id: int, action: str, table_name: str = None, record_id: int = None):
        try:
            log_data = {
                "user_id": user_id,
                "action": action,
                "table_name": table_name,
                "record_id": record_id,
                "ip_address": request.remote_addr if request else '127.0.0.1',
                "user_agent": (request.headers.get('User-Agent', '')[:500]) if request else 'CLI'
            }
            self.db.table("audit_logs").insert(log_data).execute()
        except Exception as e:
            print(f"Warning: Could not log action: {e}")
    
    def login_required(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login'))
            
            # Verify user still exists in DB (to prevent crashes after DB reset)
            user_check = self.db.table("users").select("id").eq("id", session['user_id']).execute()
            if not user_check.data:
                session.clear()
                flash('Session expired or user no longer exists. Please log in again.', 'warning')
                return redirect(url_for('login'))
                
            return f(*args, **kwargs)
        return decorated_function
    
    def role_required(self, *roles):
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
        @self.app.route('/')
        def index():
            return render_template('index.html')
        
        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                username = request.form.get('username', '').strip()
                password = request.form.get('password', '')
                if not username or not password:
                    flash('Please enter both username and password.', 'danger')
                    return render_template('login.html')
                try:
                    hashed_password = self.hash_password(password)
                    result = self.db.table("users").select("*").eq("username", username).eq("password", hashed_password).execute()
                    if result.data:
                        user = result.data[0]
                        session.permanent = True
                        session['user_id'] = user['id']
                        session['username'] = user['username']
                        session['role'] = user['role']
                        session['first_name'] = user['first_name']
                        session['last_name'] = user['last_name']
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
            if request.method == 'POST':
                username = request.form.get('username', '').strip()
                password = request.form.get('password', '')
                confirm_password = request.form.get('confirm_password', '')
                role = request.form.get('role', '')
                email = request.form.get('email', '').strip()
                first_name = request.form.get('first_name', '').strip()
                last_name = request.form.get('last_name', '').strip()
                phone_number = request.form.get('phone_number', '').strip() or None
                address = request.form.get('address', '').strip() or None
                
                if not all([username, password, role, first_name, last_name]):
                    flash('Please fill in all required fields.', 'danger')
                    return render_template('register.html')
                if password != confirm_password:
                    flash('Passwords do not match.', 'danger')
                    return render_template('register.html')
                is_valid, error_msg = self.validate_password(password)
                if not is_valid:
                    flash(error_msg, 'danger')
                    return render_template('register.html')
                if role not in ['patient', 'nurse', 'doctor', 'administrator']:
                    flash('Invalid role selected.', 'danger')
                    return render_template('register.html')
                
                try:
                    existing_user = self.db.table("users").select("id").eq("username", username).execute()
                    if existing_user.data:
                        flash('Username already exists.', 'danger')
                        return render_template('register.html')
                    
                    user_data = {
                        "username": username, "password": self.hash_password(password),
                        "role": role, "email": email, "first_name": first_name,
                        "last_name": last_name, "phone_number": phone_number, "address": address
                    }
                    result = self.db.table("users").insert(user_data).execute()
                    
                    if result.data:
                        user_id = result.data[0]["id"]
                        if role == 'patient':
                            self.db.table("patients").insert({
                                "patient_id": user_id,
                                "emergency_contact": request.form.get('emergency_contact'),
                                "insurance_info": request.form.get('insurance_info'),
                                "blood_type": request.form.get('blood_type')
                            }).execute()
                        elif role in ['doctor', 'nurse']:
                            self.db.table("medical_staff").insert({
                                "staff_id": user_id,
                                "specialization": request.form.get('specialization'),
                                "license_number": request.form.get('license_number'),
                                "hire_date": datetime.now().date().isoformat(),
                                "department": request.form.get('department'),
                                "status": "active"
                            }).execute()
                        self.log_action(user_id, "USER_REGISTERED", "users", user_id)
                        flash('Registration successful!', 'success')
                        return redirect(url_for('login'))
                except Exception as e:
                    flash(f'Registration error: {str(e)}', 'danger')
            return render_template('register.html')
        
        @self.app.route('/logout')
        def logout():
            if 'user_id' in session:
                self.log_action(session['user_id'], "USER_LOGOUT", "users", session['user_id'])
            session.clear()
            flash('Logged out successfully.', 'info')
            return redirect(url_for('index'))
        
        @self.app.route('/dashboard')
        @self.login_required
        def dashboard():
            role = session.get('role')
            if role == 'patient': return redirect(url_for('patient_dashboard'))
            if role == 'nurse': return redirect(url_for('nurse_dashboard'))
            if role == 'doctor': return redirect(url_for('doctor_dashboard'))
            if role == 'administrator': return redirect(url_for('admin_dashboard'))
            return redirect(url_for('logout'))
        
        @self.app.route('/patient/dashboard')
        @self.role_required('patient')
        def patient_dashboard():
            try:
                user_id = session['user_id']
                patient_info = self.db.table("patients").select("*").eq("patient_id", user_id).execute().data
                records = self.db.table("medical_records").select("*, users!doctor_id(*)").eq("patient_id", user_id).order("visit_date", desc=True).limit(5).execute().data
                appointments = self.db.table("appointments").select("*, users!doctor_id(*)").eq("patient_id", user_id).order("appointment_date").limit(5).execute().data
                return render_template('patient/dashboard.html', patient_info=patient_info[0] if patient_info else {}, medical_records=records, appointments=appointments)
            except Exception as e:
                flash(f'Error loading dashboard: {e}', 'danger')
                return render_template('patient/dashboard.html', patient_info={}, medical_records=[], appointments=[])

        @self.app.route('/doctor/dashboard')
        @self.role_required('doctor')
        def doctor_dashboard():
            try:
                user_id = session['user_id']
                doctor_info = self.db.table("medical_staff").select("*").eq("staff_id", user_id).execute().data
                today = datetime.now().date().isoformat()
                appointments = self.db.table("appointments").select("*, users!patient_id(*)").eq("doctor_id", user_id).gte("appointment_date", today).order("appointment_date").execute().data
                return render_template('doctor/dashboard.html', doctor_info=doctor_info[0] if doctor_info else {}, appointments=appointments)
            except Exception as e:
                flash(f'Error loading dashboard: {e}', 'danger')
                return render_template('doctor/dashboard.html', doctor_info={}, appointments=[])

        @self.app.route('/nurse/dashboard')
        @self.role_required('nurse')
        def nurse_dashboard():
            try:
                today = datetime.now().date().isoformat()
                appointments = self.db.table("appointments").select("*, patient:users!patient_id(*), doctor:users!doctor_id(*)").gte("appointment_date", today).order("appointment_date").limit(20).execute().data
                patients = self.db.table("users").select("*").eq("role", "patient").order("created_at", desc=True).limit(10).execute().data
                return render_template('nurse/dashboard.html', appointments=appointments, recent_patients=patients)
            except Exception as e:
                flash(f'Error loading dashboard: {e}', 'danger')
                return render_template('nurse/dashboard.html', appointments=[], recent_patients=[])

        @self.app.route('/admin/dashboard')
        @self.role_required('administrator')
        def admin_dashboard():
            try:
                stats = {
                    'patients': self.db.table("users").select("id", count="exact").eq("role", "patient").execute().count,
                    'doctors': self.db.table("users").select("id", count="exact").eq("role", "doctor").execute().count,
                    'nurses': self.db.table("users").select("id", count="exact").eq("role", "nurse").execute().count,
                    'administrators': self.db.table("users").select("id", count="exact").eq("role", "administrator").execute().count,
                    'appointments': self.db.table("appointments").select("id", count="exact").execute().count,
                    'medical_records': self.db.table("medical_records").select("id", count="exact").execute().count
                }
                stats['total_users'] = stats['patients'] + stats['doctors'] + stats['nurses'] + stats['administrators']
                
                recent_users = self.db.table("users").select("*").order("created_at", desc=True).limit(10).execute().data
                recent_logs = self.db.table("audit_logs").select("*, users(*)").order("created_at", desc=True).limit(15).execute().data
                return render_template('admin/dashboard.html', stats=stats, recent_users=recent_users, recent_logs=recent_logs)
            except Exception as e:
                flash(f'Error loading dashboard: {e}', 'danger')
                return render_template('admin/dashboard.html', stats={}, recent_users=[], recent_logs=[])

        @self.app.route('/api/admin/stats')
        @self.role_required('administrator')
        def api_admin_stats():
            try:
                patients = self.db.table("users").select("id", count="exact").eq("role", "patient").execute().count
                doctors = self.db.table("users").select("id", count="exact").eq("role", "doctor").execute().count
                nurses = self.db.table("users").select("id", count="exact").eq("role", "nurse").execute().count
                admins = self.db.table("users").select("id", count="exact").eq("role", "administrator").execute().count
                
                stats = {
                    'patients': patients,
                    'doctors': doctors,
                    'nurses': nurses,
                    'administrators': admins,
                    'total_users': patients + doctors + nurses + admins,
                    'appointments': self.db.table("appointments").select("id", count="exact").execute().count,
                    'medical_records': self.db.table("medical_records").select("id", count="exact").execute().count
                }
                return jsonify({'success': True, 'stats': stats})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/profile', methods=['GET', 'POST'])
        @self.login_required
        def profile():
            user_id = session['user_id']
            if request.method == 'POST':
                update_data = {
                    'first_name': request.form.get('first_name'),
                    'last_name': request.form.get('last_name'),
                    'email': request.form.get('email'),
                    'phone_number': request.form.get('phone_number'),
                    'address': request.form.get('address')
                }
                self.db.table("users").update(update_data).eq("id", user_id).execute()
                session['first_name'] = update_data['first_name']
                session['last_name'] = update_data['last_name']
                flash('Profile updated!', 'success')
            
            user_result = self.db.table("users").select("*").eq("id", user_id).execute()
            if not user_result.data:
                session.clear()
                flash('User session invalid. Please log in again.', 'warning')
                return redirect(url_for('login'))
                
            user_data = user_result.data[0]
            return render_template('profile.html', user_data=user_data)

        @self.app.route('/appointments')
        @self.login_required
        def appointments():
            user_id = session['user_id']
            role = session['role']
            query = self.db.table("appointments").select("*, patient:users!patient_id(*), doctor:users!doctor_id(*)")
            if role == 'patient': query = query.eq("patient_id", user_id)
            elif role == 'doctor': query = query.eq("doctor_id", user_id)
            result = query.order("appointment_date").execute()
            return render_template('appointments/list.html', appointments=result.data)

        @self.app.route('/appointments/book', methods=['GET', 'POST'])
        @self.login_required
        def book_appointment():
            if request.method == 'POST':
                data = {
                    'patient_id': session['user_id'] if session['role'] == 'patient' else request.form.get('patient_id'),
                    'doctor_id': request.form.get('doctor_id'),
                    'appointment_date': request.form.get('appointment_date'),
                    'appointment_time': request.form.get('appointment_time'),
                    'reason': request.form.get('reason'),
                    'status': 'scheduled'
                }
                self.db.table("appointments").insert(data).execute()
                flash('Appointment booked!', 'success')
                return redirect(url_for('appointments'))
            
            doctors = self.db.table("users").select("id, first_name, last_name").eq("role", "doctor").execute().data
            patients = self.db.table("users").select("id, first_name, last_name").eq("role", "patient").execute().data if session['role'] != 'patient' else []
            return render_template('appointments/book.html', doctors=doctors, patients=patients)

        @self.app.route('/appointments/<int:appointment_id>')
        @self.login_required
        def appointment_details(appointment_id):
            result = self.db.table("appointments").select("*").eq("id", appointment_id).execute()
            if not result.data: return redirect(url_for('appointments'))
            app = result.data[0]
            patient = self.db.table("users").select("*").eq("id", app['patient_id']).execute().data[0]
            doctor = self.db.table("users").select("*").eq("id", app['doctor_id']).execute().data[0]
            return render_template('appointments/details.html', appointment=app, patient=patient, doctor=doctor)

        @self.app.route('/patients')
        @self.role_required('doctor', 'nurse', 'administrator')
        def patients_list():
            result = self.db.table("users").select("*").eq("role", "patient").order("first_name").execute()
            return render_template('patients/list.html', patients=result.data)

        @self.app.route('/patients/<int:patient_id>')
        @self.role_required('doctor', 'nurse', 'administrator')
        def patient_details(patient_id):
            patient = self.db.table("users").select("*").eq("id", patient_id).execute().data[0]
            records = self.db.table("medical_records").select("*, users!doctor_id(*)").eq("patient_id", patient_id).order("visit_date", desc=True).execute().data
            appointments = self.db.table("appointments").select("*, users!doctor_id(*)").eq("patient_id", patient_id).order("appointment_date").execute().data
            return render_template('patients/details.html', patient=patient, medical_records=records, appointments=appointments)

        @self.app.route('/medical-records')
        @self.login_required
        def medical_records():
            user_id = session['user_id']
            role = session['role']
            query = self.db.table("medical_records").select("*, patient:users!patient_id(*), doctor:users!doctor_id(*)")
            if role == 'patient': query = query.eq("patient_id", user_id)
            elif role == 'doctor': query = query.eq("doctor_id", user_id)
            result = query.order("visit_date", desc=True).execute()
            return render_template('medical_records/list.html', records=result.data)

        @self.app.route('/medical-records/add', methods=['GET', 'POST'])
        @self.role_required('doctor', 'nurse')
        def add_medical_record():
            if request.method == 'POST':
                data = {
                    'patient_id': request.form.get('patient_id'),
                    'doctor_id': session['user_id'] if session['role'] == 'doctor' else request.form.get('doctor_id'),
                    'visit_date': request.form.get('visit_date'),
                    'diagnosis': request.form.get('diagnosis'),
                    'treatment': request.form.get('treatment'),
                    'prescription': request.form.get('prescription'),
                    'notes': request.form.get('notes'),
                    'visit_type': request.form.get('visit_type', 'general')
                }
                self.db.table("medical_records").insert(data).execute()
                flash('Record added!', 'success')
                return redirect(url_for('medical_records'))
            patients = self.db.table("users").select("id, first_name, last_name").eq("role", "patient").execute().data
            doctors = self.db.table("users").select("id, first_name, last_name").eq("role", "doctor").execute().data if session['role'] == 'nurse' else []
            return render_template('medical_records/add.html', patients=patients, doctors=doctors)

    def run(self, debug=True, host='127.0.0.1', port=5000):
        self.app.run(debug=debug, host=host, port=port)

if __name__ == "__main__":
    healthcare_app = HealthcareApp()
    healthcare_app.run(debug=True)
