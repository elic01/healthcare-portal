import os
import hashlib
import getpass
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import Optional, Dict, Any

# Load environment variables
load_dotenv()

class HealthcareSystem:
    def __init__(self):
        self.supabase = None
        self.current_user = None
        self.connect_to_database()
    
    def connect_to_database(self):
        """Establish connection to Supabase database"""
        try:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_ANON_KEY")
            
            if not url or not key:
                raise ValueError("Supabase URL and ANON_KEY must be set in .env file")
            
            self.supabase = create_client(url, key)
            print("Successfully connected to Supabase database!")
            
        except Exception as e:
            print(f"Error connecting to Supabase: {e}")
            self.supabase = None
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def validate_password(self, password: str) -> bool:
        """Validate password meets minimum requirements"""
        min_length = int(os.getenv("PASSWORD_MIN_LENGTH", 8))
        
        if len(password) < min_length:
            print(f"Password must be at least {min_length} characters long")
            return False
        
        # Additional password validation can be added here
        return True
    
    def register_user(self):
        """Register a new user"""
        if not self.supabase:
            print("Database connection not available")
            return
        
        print("\n=== User Registration ===")
        
        # Get user input
        username = input("Username: ").strip()
        if not username:
            print("Username cannot be empty!")
            return
        
        # Check if username already exists
        try:
            existing_user = self.supabase.table("users").select("id").eq("username", username).execute()
            if existing_user.data:
                print("Username already exists!")
                return
        except Exception as e:
            print(f"Error checking username: {e}")
            return
        
        password = getpass.getpass("Password: ")
        if not self.validate_password(password):
            return
            
        confirm_password = getpass.getpass("Confirm Password: ")
        
        if password != confirm_password:
            print("Passwords do not match!")
            return
        
        # Role selection
        print("\nAvailable Roles:")
        print("1. Patient")
        print("2. Nurse") 
        print("3. Doctor")
        print("4. Administrator")
        
        role_choice = input("Select role (1-4): ").strip()
        roles = {'1': 'patient', '2': 'nurse', '3': 'doctor', '4': 'administrator'}
        role = roles.get(role_choice)
        
        if not role:
            print("Invalid role selection!")
            return
        
        # Additional information
        email = input("Email: ").strip()
        if email:
            # Check if email already exists
            try:
                existing_email = self.supabase.table("users").select("id").eq("email", email).execute()
                if existing_email.data:
                    print("Email already registered!")
                    return
            except Exception as e:
                print(f"Error checking email: {e}")
                return
        
        first_name = input("First Name: ").strip()
        last_name = input("Last Name: ").strip()
        phone_number = input("Phone Number (optional): ").strip() or None
        address = input("Address (optional): ").strip() or None
        
        try:
            # Insert new user
            hashed_password = self.hash_password(password)
            
            user_data = {
                "username": username,
                "password": hashed_password,
                "role": role,
                "email": email if email else None,
                "first_name": first_name,
                "last_name": last_name,
                "phone_number": phone_number,
                "address": address
            }
            
            # Insert user
            result = self.supabase.table("users").insert(user_data).execute()
            
            if not result.data:
                print("Error creating user account")
                return
            
            user_id = result.data[0]["id"]
            
            # Insert into role-specific tables
            if role == 'patient':
                emergency_contact = input("Emergency Contact: ").strip() or None
                insurance_info = input("Insurance Information: ").strip() or None
                blood_type = input("Blood Type (optional): ").strip() or None
                
                patient_data = {
                    "patient_id": user_id,
                    "emergency_contact": emergency_contact,
                    "insurance_info": insurance_info,
                    "blood_type": blood_type
                }
                
                self.supabase.table("patients").insert(patient_data).execute()
            
            elif role in ['doctor', 'nurse']:
                specialization = input("Specialization: ").strip() if role == 'doctor' else "Nursing"
                license_number = input("License Number: ").strip()
                department = input("Department: ").strip() or None
                
                staff_data = {
                    "staff_id": user_id,
                    "specialization": specialization,
                    "license_number": license_number,
                    "hire_date": datetime.now().date().isoformat(),
                    "department": department,
                    "status": "active"
                }
                
                self.supabase.table("medical_staff").insert(staff_data).execute()
            
            print(f"\n✅ Registration successful! Welcome, {first_name}!")
            
            # Log the registration
            self.log_action(user_id, "USER_REGISTERED", "users", user_id)
            
        except Exception as e:
            print(f"Error during registration: {e}")
    
    def login_user(self):
        """Login existing user"""
        if not self.supabase:
            print("Database connection not available")
            return
        
        print("\n=== User Login ===")
        
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")
        
        try:
            hashed_password = self.hash_password(password)
            
            # Check user credentials
            result = self.supabase.table("users").select(
                "id, username, role, first_name, last_name, email"
            ).eq("username", username).eq("password", hashed_password).execute()
            
            if result.data:
                user = result.data[0]
                self.current_user = user
                print(f"\n✅ Login successful! Welcome, {user['first_name']}!")
                print(f"Role: {user['role'].title()}")
                
                # Log the login
                self.log_action(user['id'], "USER_LOGIN", "users", user['id'])
                
                self.show_user_dashboard(user)
            else:
                print("❌ Invalid username or password!")
                
        except Exception as e:
            print(f"Error during login: {e}")
    
    def log_action(self, user_id: int, action: str, table_name: str = None, record_id: int = None, 
                  old_values: dict = None, new_values: dict = None):
        """Log user actions for audit purposes"""
        try:
            if self.supabase:
                log_data = {
                    "user_id": user_id,
                    "action": action,
                    "table_name": table_name,
                    "record_id": record_id,
                    "old_values": old_values,
                    "new_values": new_values
                }
                self.supabase.table("audit_logs").insert(log_data).execute()
        except Exception as e:
            print(f"Warning: Could not log action: {e}")
    
    def show_user_dashboard(self, user: dict):
        """Show role-specific dashboard"""
        role = user['role']
        
        if role == 'patient':
            self.patient_dashboard(user)
        elif role == 'nurse':
            self.nurse_dashboard(user)
        elif role == 'doctor':
            self.doctor_dashboard(user)
        elif role == 'administrator':
            self.admin_dashboard(user)
    
    def patient_dashboard(self, user: dict):
        """Patient-specific dashboard"""
        while True:
            print(f"\n=== Patient Dashboard ===")
            print(f"Welcome, {user['first_name']} {user['last_name']}")
            print("\nAvailable Options:")
            print("1. View My Profile")
            print("2. View My Medical Records")
            print("3. View My Appointments") 
            print("4. Update Profile")
            print("5. Logout")
            
            choice = input("Select option (1-5): ").strip()
            
            if choice == '1':
                self.view_patient_profile(user['id'])
            elif choice == '2':
                self.view_medical_records(user['id'])
            elif choice == '3':
                self.view_appointments(user['id'])
            elif choice == '4':
                self.update_profile(user)
            elif choice == '5':
                print("Logging out...")
                self.current_user = None
                break
            else:
                print("Invalid option! Please try again.")
    
    def nurse_dashboard(self, user: dict):
        """Nurse-specific dashboard"""
        while True:
            print(f"\n=== Nurse Dashboard ===")
            print(f"Welcome, Nurse {user['first_name']} {user['last_name']}")
            print("\nAvailable Options:")
            print("1. View Patient List")
            print("2. View My Schedule")
            print("3. View Patient Details")
            print("4. Update My Profile")
            print("5. Logout")
            
            choice = input("Select option (1-5): ").strip()
            
            if choice == '1':
                self.view_patient_list()
            elif choice == '2':
                self.view_schedule(user['id'])
            elif choice == '3':
                patient_id = input("Enter Patient ID: ").strip()
                if patient_id.isdigit():
                    self.view_patient_details(int(patient_id))
                else:
                    print("Invalid Patient ID")
            elif choice == '4':
                self.update_profile(user)
            elif choice == '5':
                print("Logging out...")
                self.current_user = None
                break
            else:
                print("Invalid option! Please try again.")
    
    def doctor_dashboard(self, user: dict):
        """Doctor-specific dashboard"""
        while True:
            print(f"\n=== Doctor Dashboard ===")
            print(f"Welcome, Dr. {user['last_name']}")
            print("\nAvailable Options:")
            print("1. View Patient List")
            print("2. View My Appointments")
            print("3. View Patient Medical History")
            print("4. Add Medical Record")
            print("5. Update My Profile")
            print("6. Logout")
            
            choice = input("Select option (1-6): ").strip()
            
            if choice == '1':
                self.view_patient_list()
            elif choice == '2':
                self.view_appointments(user['id'], is_doctor=True)
            elif choice == '3':
                patient_id = input("Enter Patient ID: ").strip()
                if patient_id.isdigit():
                    self.view_medical_records(int(patient_id))
                else:
                    print("Invalid Patient ID")
            elif choice == '4':
                self.add_medical_record(user['id'])
            elif choice == '5':
                self.update_profile(user)
            elif choice == '6':
                print("Logging out...")
                self.current_user = None
                break
            else:
                print("Invalid option! Please try again.")
    
    def admin_dashboard(self, user: dict):
        """Administrator-specific dashboard"""
        while True:
            print(f"\n=== Administrator Dashboard ===")
            print(f"Welcome, {user['first_name']} {user['last_name']}")
            print("\nAvailable Options:")
            print("1. View All Users")
            print("2. View System Statistics")
            print("3. View Audit Logs")
            print("4. Manage Users")
            print("5. Update My Profile")
            print("6. Logout")
            
            choice = input("Select option (1-6): ").strip()
            
            if choice == '1':
                self.view_all_users()
            elif choice == '2':
                self.view_system_stats()
            elif choice == '3':
                self.view_audit_logs()
            elif choice == '4':
                self.manage_users()
            elif choice == '5':
                self.update_profile(user)
            elif choice == '6':
                print("Logging out...")
                self.current_user = None
                break
            else:
                print("Invalid option! Please try again.")
    
    def view_patient_profile(self, patient_id: int):
        """View patient profile information"""
        try:
            # Get user info
            user_result = self.supabase.table("users").select("*").eq("id", patient_id).execute()
            if not user_result.data:
                print("Patient not found")
                return
                
            user = user_result.data[0]
            
            # Get patient-specific info
            patient_result = self.supabase.table("patients").select("*").eq("patient_id", patient_id).execute()
            patient_info = patient_result.data[0] if patient_result.data else {}
            
            print(f"\n=== Patient Profile ===")
            print(f"Name: {user['first_name']} {user['last_name']}")
            print(f"Username: {user['username']}")
            print(f"Email: {user.get('email', 'Not provided')}")
            print(f"Phone: {user.get('phone_number', 'Not provided')}")
            print(f"Address: {user.get('address', 'Not provided')}")
            print(f"Emergency Contact: {patient_info.get('emergency_contact', 'Not provided')}")
            print(f"Insurance Info: {patient_info.get('insurance_info', 'Not provided')}")
            print(f"Blood Type: {patient_info.get('blood_type', 'Not provided')}")
            
        except Exception as e:
            print(f"Error viewing profile: {e}")
    
    def view_medical_records(self, patient_id: int):
        """View medical records for a patient"""
        try:
            result = self.supabase.table("medical_records").select(
                "*, users!doctor_id(first_name, last_name)"
            ).eq("patient_id", patient_id).order("visit_date", desc=True).execute()
            
            if not result.data:
                print("No medical records found")
                return
            
            print(f"\n=== Medical Records ===")
            for record in result.data:
                doctor = record.get('users', {})
                doctor_name = f"Dr. {doctor.get('first_name', '')} {doctor.get('last_name', '')}"
                
                print(f"\nDate: {record['visit_date']}")
                print(f"Doctor: {doctor_name}")
                print(f"Diagnosis: {record.get('diagnosis', 'Not provided')}")
                print(f"Treatment: {record.get('treatment', 'Not provided')}")
                print(f"Prescription: {record.get('prescription', 'Not provided')}")
                print(f"Notes: {record.get('notes', 'Not provided')}")
                print("-" * 40)
                
        except Exception as e:
            print(f"Error viewing medical records: {e}")
    
    def view_appointments(self, user_id: int, is_doctor: bool = False):
        """View appointments for user"""
        try:
            if is_doctor:
                result = self.supabase.table("appointments").select(
                    "*, users!patient_id(first_name, last_name)"
                ).eq("doctor_id", user_id).order("appointment_date", desc=False).execute()
                user_type = "doctor"
            else:
                result = self.supabase.table("appointments").select(
                    "*, users!doctor_id(first_name, last_name)"  
                ).eq("patient_id", user_id).order("appointment_date", desc=False).execute()
                user_type = "patient"
            
            if not result.data:
                print("No appointments found")
                return
            
            print(f"\n=== My Appointments ===")
            for appointment in result.data:
                other_user = appointment.get('users', {})
                if user_type == "patient":
                    other_name = f"Dr. {other_user.get('first_name', '')} {other_user.get('last_name', '')}"
                    print(f"Doctor: {other_name}")
                else:
                    other_name = f"{other_user.get('first_name', '')} {other_user.get('last_name', '')}"
                    print(f"Patient: {other_name}")
                
                print(f"Date/Time: {appointment['appointment_date']}")
                print(f"Duration: {appointment['duration_minutes']} minutes")
                print(f"Status: {appointment['status']}")
                print(f"Reason: {appointment.get('reason', 'Not provided')}")
                print(f"Notes: {appointment.get('notes', 'Not provided')}")
                print("-" * 40)
                
        except Exception as e:
            print(f"Error viewing appointments: {e}")
    
    def view_patient_list(self):
        """View list of all patients (for medical staff)"""
        try:
            result = self.supabase.table("users").select(
                "id, first_name, last_name, email, phone_number"
            ).eq("role", "patient").execute()
            
            if not result.data:
                print("No patients found")
                return
            
            print(f"\n=== Patient List ===")
            print(f"{'ID':<5} {'Name':<25} {'Email':<25} {'Phone':<15}")
            print("-" * 70)
            
            for patient in result.data:
                name = f"{patient.get('first_name', '')} {patient.get('last_name', '')}"
                email = patient.get('email', 'N/A')
                phone = patient.get('phone_number', 'N/A')
                print(f"{patient['id']:<5} {name:<25} {email:<25} {phone:<15}")
                
        except Exception as e:
            print(f"Error viewing patient list: {e}")
    
    def update_profile(self, user: dict):
        """Update user profile"""
        print(f"\n=== Update Profile ===")
        print("Leave blank to keep current value")
        
        first_name = input(f"First Name ({user.get('first_name', '')}): ").strip()
        last_name = input(f"Last Name ({user.get('last_name', '')}): ").strip()
        email = input(f"Email ({user.get('email', '')}): ").strip()
        phone = input(f"Phone ({user.get('phone_number', '')}): ").strip()
        address = input(f"Address ({user.get('address', '')}): ").strip()
        
        update_data = {}
        if first_name:
            update_data['first_name'] = first_name
        if last_name:
            update_data['last_name'] = last_name
        if email:
            update_data['email'] = email
        if phone:
            update_data['phone_number'] = phone
        if address:
            update_data['address'] = address
        
        if update_data:
            try:
                self.supabase.table("users").update(update_data).eq("id", user['id']).execute()
                print("✅ Profile updated successfully!")
                
                # Update current user data
                user.update(update_data)
                
                self.log_action(user['id'], "PROFILE_UPDATED", "users", user['id'])
                
            except Exception as e:
                print(f"Error updating profile: {e}")
        else:
            print("No changes made")
    
    def add_medical_record(self, doctor_id: int):
        """Add a medical record (for doctors)"""
        print(f"\n=== Add Medical Record ===")
        
        patient_id = input("Patient ID: ").strip()
        if not patient_id.isdigit():
            print("Invalid Patient ID")
            return
        
        patient_id = int(patient_id)
        
        # Verify patient exists
        try:
            patient_check = self.supabase.table("users").select("first_name, last_name").eq("id", patient_id).eq("role", "patient").execute()
            if not patient_check.data:
                print("Patient not found")
                return
            
            patient_name = f"{patient_check.data[0]['first_name']} {patient_check.data[0]['last_name']}"
            print(f"Adding record for: {patient_name}")
            
            diagnosis = input("Diagnosis: ").strip()
            treatment = input("Treatment: ").strip()
            prescription = input("Prescription: ").strip()
            notes = input("Notes: ").strip()
            
            record_data = {
                "patient_id": patient_id,
                "doctor_id": doctor_id,
                "visit_date": datetime.now().isoformat(),
                "diagnosis": diagnosis or None,
                "treatment": treatment or None,
                "prescription": prescription or None,
                "notes": notes or None
            }
            
            result = self.supabase.table("medical_records").insert(record_data).execute()
            
            if result.data:
                print("✅ Medical record added successfully!")
                self.log_action(doctor_id, "MEDICAL_RECORD_ADDED", "medical_records", result.data[0]['id'])
            else:
                print("Error adding medical record")
                
        except Exception as e:
            print(f"Error adding medical record: {e}")
    
    def view_all_users(self):
        """View all users (admin only)"""
        try:
            result = self.supabase.table("users").select(
                "id, username, role, first_name, last_name, email, created_at"
            ).order("created_at", desc=True).execute()
            
            print(f"\n=== All Users ===")
            print(f"{'ID':<5} {'Username':<15} {'Role':<12} {'Name':<25} {'Email':<25} {'Created':<12}")
            print("-" * 100)
            
            for user in result.data:
                name = f"{user.get('first_name', '')} {user.get('last_name', '')}"
                email = user.get('email', 'N/A')
                created = user['created_at'][:10] if user.get('created_at') else 'N/A'
                
                print(f"{user['id']:<5} {user['username']:<15} {user['role']:<12} {name:<25} {email:<25} {created:<12}")
                
        except Exception as e:
            print(f"Error viewing users: {e}")
    
    def view_system_stats(self):
        """View system statistics (admin only)"""
        try:
            # Count users by role
            patients = self.supabase.table("users").select("id", count="exact").eq("role", "patient").execute()
            doctors = self.supabase.table("users").select("id", count="exact").eq("role", "doctor").execute()
            nurses = self.supabase.table("users").select("id", count="exact").eq("role", "nurse").execute()
            admins = self.supabase.table("users").select("id", count="exact").eq("role", "administrator").execute()
            
            # Count appointments
            appointments = self.supabase.table("appointments").select("id", count="exact").execute()
            
            # Count medical records
            records = self.supabase.table("medical_records").select("id", count="exact").execute()
            
            print(f"\n=== System Statistics ===")
            print(f"Total Patients: {patients.count}")
            print(f"Total Doctors: {doctors.count}")
            print(f"Total Nurses: {nurses.count}")
            print(f"Total Administrators: {admins.count}")
            print(f"Total Users: {patients.count + doctors.count + nurses.count + admins.count}")
            print(f"Total Appointments: {appointments.count}")
            print(f"Total Medical Records: {records.count}")
            
        except Exception as e:
            print(f"Error viewing statistics: {e}")
    
    def view_audit_logs(self):
        """View recent audit logs (admin only)"""
        try:
            result = self.supabase.table("audit_logs").select(
                "*, users(username, first_name, last_name)"
            ).order("created_at", desc=True).limit(20).execute()
            
            print(f"\n=== Recent Audit Logs ===")
            for log in result.data:
                user = log.get('users', {})
                username = user.get('username', 'System')
                timestamp = log['created_at'][:19] if log.get('created_at') else 'N/A'
                
                print(f"Time: {timestamp}")
                print(f"User: {username}")
                print(f"Action: {log['action']}")
                print(f"Table: {log.get('table_name', 'N/A')}")
                print("-" * 40)
                
        except Exception as e:
            print(f"Error viewing audit logs: {e}")
    
    def manage_users(self):
        """Manage users (admin only) - placeholder for future implementation"""
        print("\n=== User Management ===")
        print("This feature will be implemented in a future version.")
        print("Available actions will include:")
        print("- Deactivate/reactivate users")
        print("- Reset passwords")
        print("- Change user roles")
        print("- Delete user accounts")
    
    def view_schedule(self, user_id: int):
        """View schedule (for nurses/doctors)"""
        try:
            result = self.supabase.table("appointments").select(
                "*, users!patient_id(first_name, last_name)"
            ).eq("doctor_id", user_id).gte(
                "appointment_date", datetime.now().isoformat()
            ).order("appointment_date", desc=False).limit(10).execute()
            
            print(f"\n=== My Upcoming Schedule ===")
            if not result.data:
                print("No upcoming appointments")
                return
            
            for appointment in result.data:
                patient = appointment.get('users', {})
                patient_name = f"{patient.get('first_name', '')} {patient.get('last_name', '')}"
                
                print(f"Date/Time: {appointment['appointment_date']}")
                print(f"Patient: {patient_name}")
                print(f"Duration: {appointment['duration_minutes']} minutes")
                print(f"Reason: {appointment.get('reason', 'Not provided')}")
                print("-" * 30)
                
        except Exception as e:
            print(f"Error viewing schedule: {e}")
    
    def view_patient_details(self, patient_id: int):
        """View detailed patient information (for medical staff)"""
        try:
            # Get user info
            user_result = self.supabase.table("users").select("*").eq("id", patient_id).eq("role", "patient").execute()
            if not user_result.data:
                print("Patient not found")
                return
                
            user = user_result.data[0]
            
            # Get patient-specific info
            patient_result = self.supabase.table("patients").select("*").eq("patient_id", patient_id).execute()
            patient_info = patient_result.data[0] if patient_result.data else {}
            
            print(f"\n=== Patient Details ===")
            print(f"Name: {user['first_name']} {user['last_name']}")
            print(f"Email: {user.get('email', 'Not provided')}")
            print(f"Phone: {user.get('phone_number', 'Not provided')}")
            print(f"Address: {user.get('address', 'Not provided')}")
            print(f"Date of Birth: {user.get('date_of_birth', 'Not provided')}")
            print(f"Emergency Contact: {patient_info.get('emergency_contact', 'Not provided')}")
            print(f"Insurance Info: {patient_info.get('insurance_info', 'Not provided')}")
            print(f"Blood Type: {patient_info.get('blood_type', 'Not provided')}")
            print(f"Medical History: {patient_info.get('medical_history', 'Not provided')}")
            print(f"Allergies: {patient_info.get('allergies', 'Not provided')}")
            
            # Recent medical records
            records = self.supabase.table("medical_records").select(
                "visit_date, diagnosis, treatment"
            ).eq("patient_id", patient_id).order("visit_date", desc=True).limit(3).execute()
            
            if records.data:
                print(f"\n=== Recent Medical Records ===")
                for record in records.data:
                    print(f"Date: {record['visit_date'][:10]}")
                    print(f"Diagnosis: {record.get('diagnosis', 'Not provided')}")
                    print(f"Treatment: {record.get('treatment', 'Not provided')}")
                    print("-" * 30)
                    
        except Exception as e:
            print(f"Error viewing patient details: {e}")
    
    def main_menu(self):
        """Main application menu"""
        while True:
            print("\n" + "="*50)
            print("🏥 PATIENT DATA MANAGEMENT SYSTEM")
            print("="*50)
            print("1. Login")
            print("2. Register")
            print("3. Test Database Connection")
            print("4. Exit")
            
            choice = input("Select option (1-4): ").strip()
            
            if choice == '1':
                self.login_user()
            elif choice == '2':
                self.register_user()
            elif choice == '3':
                self.test_connection()
            elif choice == '4':
                print("Thank you for using Healthcare Portal. Goodbye!")
                break
            else:
                print("Invalid option! Please try again.")
    
    def test_connection(self):
        """Test database connection"""
        if self.supabase:
            try:
                # Try to fetch user count
                result = self.supabase.table("users").select("id", count="exact").execute()
                print(f"✅ Database connection successful! Total users: {result.count}")
            except Exception as e:
                print(f"❌ Database connection test failed: {e}")
                print("Make sure you have executed the SQL schema in your Supabase dashboard")
        else:
            print("❌ No database connection available")

# Main application
if __name__ == "__main__":
    print("🏥 Starting Healthcare Portal...")
    healthcare_system = HealthcareSystem()
    
    if not healthcare_system.supabase:
        print("❌ Failed to connect to database. Please check your configuration.")
        exit(1)
    
    try:
        healthcare_system.main_menu()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        print("Goodbye!")