# 🏥 AI Prescriptor

A web-based medical prescription application built with Streamlit that allows doctors to create prescriptions using voice commands, AI suggestions, and manual entry.

## Features

- 🎤 **Voice-to-Text Prescription**: Record or upload audio to automatically transcribe prescriptions
- 🤖 **AI Medicine Suggestions**: Get intelligent medicine recommendations based on symptoms
- 📝 **Manual Prescription Entry**: Add medicines manually with detailed dosage information
- 📊 **Patient Management**: Store patient information and medical history
- 📄 **PDF Generation**: Generate professional prescription PDFs
- 🔐 **Secure Authentication**: Doctor login system with encrypted passwords
- 🎨 **Theme Support**: Light and dark mode themes

## System Requirements

- Python 3.8 or higher
- MySQL Database
- FFmpeg (for audio processing)
- 4GB RAM minimum
- Internet connection (for AI features)

## Quick Setup

### 1. Clone or Download the Project
```bash
# If using git
git clone <repository-url>
cd DEMO

# Or download and extract the ZIP file
```

### 2. Run Setup Check
```bash
python setup_new_system.py
```

This script will check all dependencies and guide you through the installation process.

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install System Dependencies

#### Windows
1. **FFmpeg**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - Extract to a folder (e.g., `C:\ffmpeg`)
   - Add to PATH: `C:\ffmpeg\bin`

2. **MySQL**: Download MySQL Installer from [mysql.com](https://dev.mysql.com/downloads/installer/)
   - Run installer and follow setup wizard
   - Remember the root password you set

#### macOS
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install ffmpeg mysql
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg mysql-server
```

### 5. Configure Database

1. **Start MySQL Service**
   ```bash
   # Windows: MySQL should start automatically
   # macOS: brew services start mysql
   # Linux: sudo systemctl start mysql
   ```

2. **Create Database**
   ```sql
   mysql -u root -p
   CREATE DATABASE ai_prescriptor;
   EXIT;
   ```

3. **Update Database Configuration**
   Edit `database_config.py` and update the `DB_CONFIG`:
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'user': 'root',
       'password': '',  # Update this
       'database': 'ai_prescriptor'
   }
   ```

4. **Run Database Setup**
   ```bashs
   streamlit run setup_database.py
   ```

### 6. Run the Application
```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## Usage

### First Time Setup
1. **Register a Doctor Account**: Use the registration form to create your doctor profile
2. **Login**: Use your credentials to access the application

### Creating Prescriptions
1. **Add Patient Information**: Fill in patient details (name, age, gender, symptoms)
2. **Choose Input Method**:
   - **Voice Recording**: Click the microphone and speak your prescription
   - **Audio Upload**: Upload an audio file with your prescription
   - **Manual Entry**: Add medicines one by one with dosage details
   - **AI Suggestions**: Get AI-powered medicine recommendations based on symptoms
3. **Review and Edit**: Modify dosages, timing, and duration as needed
4. **Generate PDF**: Download a professional prescription document

## File Structure

```
DEMO/
├── app.py                 # Main application file
├── database_config.py     # Database connection and management
├── login_page.py         # Authentication system
├── theme_config.py       # UI theme configuration
├── utils.py              # Utility functions
├── setup_database.py     # Database initialization
├── setup_new_system.py   # System setup checker
├── medicines.csv         # Medicine database
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Troubleshooting

### Common Issues

1. **"FFmpeg not found"**
   - Install FFmpeg and add to PATH
   - Restart your terminal/command prompt

2. **"MySQL connection failed"**
   - Check if MySQL service is running
   - Verify password in `database_config.py`
   - Ensure database `ai_prescriptor` exists

3. **"Package not found"**
   - Run: `pip install -r requirements.txt`
   - If using virtual environment, activate it first

4. **"Audio processing failed"**
   - Ensure FFmpeg is properly installed
   - Check audio file format (supports wav, mp3, m4a)

5. **"Whisper model download failed"**
   - Check internet connection
   - The model will download automatically on first use

### Getting Help

1. Run the setup checker: `python setup_new_system.py`
2. Check the console output for specific error messages
3. Ensure all system dependencies are installed
4. Verify database configuration

## Security Notes

- Change default MySQL password
- Use strong passwords for doctor accounts
- Keep the application updated
- Don't share sensitive patient data

## License

This project is for educational and demonstration purposes. Please ensure compliance with local medical regulations before using in clinical settings.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Run the setup checker script
3. Review error messages in the console
4. Ensure all dependencies are properly installed 
