import streamlit as st
from database_config import get_database_manager
import re

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone) is not None

def show_login_page():
    """Display the login page with authentication"""
    st.title("🏥 AI Prescriptor - Doctor Login")
    
    # Initialize database
    db_manager = get_database_manager()
    
    # Create tabs for login and registration
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.header("Doctor Login")
        
        with st.form("login_form"):
            doctor_id = st.text_input("Doctor ID", placeholder="Enter your doctor ID")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_button = st.form_submit_button("Login", use_container_width=True)
            
            if login_button:
                if doctor_id and password:
                    # Verify doctor credentials
                    doctor = db_manager.verify_doctor(doctor_id, password)
                    if doctor:
                        st.success("Login successful!")
                        # Store doctor info in session state
                        st.session_state['logged_in'] = True
                        st.session_state['doctor'] = doctor
                        st.rerun()
                    else:
                        st.error("Invalid doctor ID or password. Please try again.")
                else:
                    st.warning("Please fill in all fields.")
    
    with tab2:
        st.header("Doctor Registration")
        
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_doctor_id = st.text_input("Doctor ID", placeholder="Create a unique doctor ID")
                new_name = st.text_input("Full Name", placeholder="Enter your full name")
                specialization = st.text_input("Specialization", placeholder="e.g., Cardiology, Neurology")
            
            with col2:
                new_password = st.text_input("Password", type="password", placeholder="Create a password")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                email = st.text_input("Email", placeholder="Enter your email")
                phone = st.text_input("Phone", placeholder="Enter your phone number")
            
            register_button = st.form_submit_button("Register", use_container_width=True)
            
            if register_button:
                # Validate inputs
                if not all([new_doctor_id, new_name, new_password, confirm_password]):
                    st.error("Please fill in all required fields.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters long.")
                elif email and not validate_email(email):
                    st.error("Please enter a valid email address.")
                elif phone and not validate_phone(phone):
                    st.error("Please enter a valid phone number.")
                else:
                    # Try to register the doctor
                    success = db_manager.register_doctor(
                        new_doctor_id, new_password, new_name, 
                        specialization, email, phone
                    )
                    if success:
                        st.success("Registration successful! You can now login.")
                    else:
                        st.error("Registration failed. Doctor ID might already exist.")

def show_logout():
    """Show logout button and handle logout"""
    if st.sidebar.button("Logout", use_container_width=True):
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def check_authentication():
    """Check if user is authenticated"""
    if 'logged_in' not in st.session_state:
        return False
    return st.session_state['logged_in'] 