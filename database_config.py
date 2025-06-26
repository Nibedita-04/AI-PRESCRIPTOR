import mysql.connector
from mysql.connector import Error
import bcrypt
import streamlit as st
import os

# Database configuration - Update these values as needed
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Nibedita_612',  # Set your MySQL password here
    'database': 'ai_prescriptor'
}

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            # Try to connect to the database
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                self.create_tables()
                return True
        except Error as e:
            if e.errno == 1045:  # Access denied error
                st.error("""
                **Database Connection Error: Access Denied**
                
                Please update the MySQL password in `database_config.py`:
                1. Open `database_config.py`
                2. Find the `DB_CONFIG` section
                3. Set your MySQL password: `'password': 'your_password_here'`
                4. Save the file and restart the app
                
                If you don't have a password set, you can also try:
                - Setting `'password': None` instead of `'password': ''`
                """)
            elif e.errno == 1049:  # Database doesn't exist
                st.error("""
                **Database Not Found**
                
                The database 'ai_prescriptor' doesn't exist. Please:
                1. Run `streamlit run setup_database.py` to create it, or
                2. Create it manually in MySQL Workbench
                """)
            else:
                st.error(f"Database connection error: {e}")
            return False
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            cursor = self.connection.cursor()
            
            # Create doctors table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS doctors (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    doctor_id VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    specialization VARCHAR(100),
                    email VARCHAR(100),
                    phone VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create patients table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    doctor_id INT,
                    patient_name VARCHAR(100) NOT NULL,
                    age INT,
                    gender VARCHAR(20),
                    symptoms TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (doctor_id) REFERENCES doctors(id)
                )
            """)
            
            # Create prescriptions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prescriptions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    patient_id INT,
                    doctor_id INT,
                    medicine_name VARCHAR(100) NOT NULL,
                    days INT,
                    tablets_per_day INT,
                    meal_time VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients(id),
                    FOREIGN KEY (doctor_id) REFERENCES doctors(id)
                )
            """)
            
            self.connection.commit()
            cursor.close()
            
        except Error as e:
            st.error(f"Error creating tables: {e}")
    
    def register_doctor(self, doctor_id, password, name, specialization="", email="", phone=""):
        """Register a new doctor"""
        try:
            cursor = self.connection.cursor()
            
            # Hash the password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute("""
                INSERT INTO doctors (doctor_id, password_hash, name, specialization, email, phone)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (doctor_id, password_hash, name, specialization, email, phone))
            
            self.connection.commit()
            cursor.close()
            return True
            
        except Error as e:
            st.error(f"Error registering doctor: {e}")
            return False
    
    def verify_doctor(self, doctor_id, password):
        """Verify doctor login credentials"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM doctors WHERE doctor_id = %s", (doctor_id,))
            doctor = cursor.fetchone()
            
            if doctor and bcrypt.checkpw(password.encode('utf-8'), doctor['password_hash'].encode('utf-8')):
                cursor.close()
                return doctor
            else:
                cursor.close()
                return None
                
        except Error as e:
            st.error(f"Error verifying doctor: {e}")
            return None
    
    def save_patient(self, doctor_id, patient_data):
        """Save patient information"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT INTO patients (doctor_id, patient_name, age, gender, symptoms)
                VALUES (%s, %s, %s, %s, %s)
            """, (doctor_id, patient_data['Name'], patient_data['Age'], 
                  patient_data['Gender'], patient_data['Symptoms']))
            
            patient_id = cursor.lastrowid
            self.connection.commit()
            cursor.close()
            return patient_id
            
        except Error as e:
            st.error(f"Error saving patient: {e}")
            return None
    
    def save_prescriptions(self, patient_id, doctor_id, prescriptions):
        """Save prescriptions for a patient"""
        try:
            cursor = self.connection.cursor()
            
            for prescription in prescriptions:
                cursor.execute("""
                    INSERT INTO prescriptions (patient_id, doctor_id, medicine_name, days, tablets_per_day, meal_time)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (patient_id, doctor_id, prescription['Medicine Name'], 
                      prescription['Number of Days'], prescription['Tablets per Day'], 
                      prescription['Meal Time']))
            
            self.connection.commit()
            cursor.close()
            return True
            
        except Error as e:
            st.error(f"Error saving prescriptions: {e}")
            return False
    
    def close_connection(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()

# Initialize database manager
@st.cache_resource
def get_database_manager():
    return DatabaseManager() 