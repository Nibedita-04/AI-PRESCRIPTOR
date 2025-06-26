import mysql.connector
from mysql.connector import Error
import streamlit as st

# Use the same database configuration as the main app
from database_config import DB_CONFIG

def create_database():
    """Create the MySQL database if it doesn't exist"""
    try:
        # Connect to MySQL server (without specifying database)
        connection_config = DB_CONFIG.copy()
        connection_config.pop('database', None)  # Remove database name for initial connection
        
        connection = mysql.connector.connect(**connection_config)
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database
            cursor.execute("CREATE DATABASE IF NOT EXISTS ai_prescriptor")
            st.success("Database 'ai_prescriptor' created successfully!")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        if e.errno == 1045:  # Access denied error
            st.error("""
            **Access Denied Error**
            
            Please update the MySQL password in `database_config.py`:
            1. Open `database_config.py`
            2. Find the `DB_CONFIG` section
            3. Set your MySQL password: `'password': 'your_password_here'`
            4. Save the file and try again
            """)
        else:
            st.error(f"Error creating database: {e}")
        return False

def test_connection():
    """Test the database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            st.success("✅ Database connection successful!")
            st.info(f"Connected to: {connection.server_host}:{connection.server_port}")
            st.info(f"Database: {DB_CONFIG['database']}")
            connection.close()
            return True
        else:
            st.error("Failed to connect to database.")
            return False
            
    except Error as e:
        if e.errno == 1045:  # Access denied error
            st.error("""
            **Access Denied Error**
            
            Please update the MySQL password in `database_config.py`:
            1. Open `database_config.py`
            2. Find the `DB_CONFIG` section
            3. Set your MySQL password: `'password': 'your_password_here'`
            4. Save the file and try again
            """)
        elif e.errno == 1049:  # Database doesn't exist
            st.error("""
            **Database Not Found**
            
            The database 'ai_prescriptor' doesn't exist. 
            Click "Create Database" button above to create it.
            """)
        else:
            st.error(f"Database connection error: {e}")
        return False

def main():
    st.title("🔧 Database Setup")
    st.write("This script will help you set up the MySQL database for the AI Prescriptor application.")
    
    st.warning("""
    **Prerequisites:**
    1. MySQL Server must be installed and running
    2. You need to know your MySQL root password
    3. Update the password in `database_config.py` if needed
    """)
    
    # Show current configuration
    st.subheader("Current Database Configuration")
    st.code(f"""
Host: {DB_CONFIG['host']}
User: {DB_CONFIG['user']}
Database: {DB_CONFIG['database']}
Password: {'*' * len(DB_CONFIG['password']) if DB_CONFIG['password'] else '(empty)'}
    """)
    
    if not DB_CONFIG['password']:
        st.warning("⚠️ No password set. If your MySQL requires a password, please update `database_config.py`")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Create Database", use_container_width=True):
            create_database()
    
    with col2:
        if st.button("Test Connection", use_container_width=True):
            test_connection()
    
    st.info("""
    **Next Steps:**
    1. Make sure MySQL server is running
    2. Update the password in `database_config.py` if needed
    3. Test the connection
    4. Run the main application: `streamlit run app.py`
    """)
    
    st.subheader("Troubleshooting")
    st.markdown("""
    **Common Issues:**
    
    **Access Denied (1045):**
    - Update the password in `database_config.py`
    - Make sure MySQL server is running
    - Check if the username is correct
    
    **Database Not Found (1049):**
    - Click "Create Database" button above
    
    **Connection Refused:**
    - Make sure MySQL server is running
    - Check if the port is correct (default: 3306)
    """)

if __name__ == "__main__":
    main() 