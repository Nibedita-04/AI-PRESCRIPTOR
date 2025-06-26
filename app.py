import streamlit as st
import pandas as pd
import speech_recognition as sr
from pydub import AudioSegment
import io
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import av
from fpdf import FPDF
from datetime import datetime
import whisper
import tempfile
import os
from rapidfuzz import process, fuzz
import requests

# Import custom modules
from database_config import get_database_manager
from theme_config import apply_theme, get_theme_colors
from login_page import show_login_page, show_logout, check_authentication
from utils import extract_prescription, word_to_num

# Page configuration
st.set_page_config(
    page_title="AI Prescriptor",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'prescriptions' not in st.session_state:
    st.session_state['prescriptions'] = []

# Load Whisper model for better transcription
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")

whisper_model = load_whisper_model()

# Load medicines data from CSV file
@st.cache_data
def load_medicines_data():
    """Loads medicine data from a CSV file and caches it."""
    try:
        df = pd.read_csv('medicines.csv')
        return df
    except FileNotFoundError:
        st.error("The 'medicines.csv' file was not found. Please make sure it's in the correct directory.")
        return pd.DataFrame()

medicines_df = load_medicines_data()
if not medicines_df.empty:
    medicines_list = medicines_df['name'].tolist()
else:
    medicines_list = []

# Check authentication
if not check_authentication():
    show_login_page()
    st.stop()

# Get database manager
db_manager = get_database_manager()

# Apply theme
theme = st.sidebar.radio('Theme', ['Light', 'Dark'], index=1 if st.session_state.get('theme') == 'Dark' else 0)
st.session_state['theme'] = theme
apply_theme(theme)

# Show logout button in sidebar
show_logout()

# Display doctor info in sidebar
if 'doctor' in st.session_state:
    st.sidebar.title('👨‍⚕️ Doctor Info')
    doctor = st.session_state['doctor']
    st.sidebar.write(f"**Name:** {doctor['name']}")
    st.sidebar.write(f"**ID:** {doctor['doctor_id']}")
    if doctor.get('specialization'):
        st.sidebar.write(f"**Specialization:** {doctor['specialization']}")

# --- MAIN LAYOUT ---
st.title('🏥 AI Prescriptor')

# Patient Info Section
with st.expander('Patient Information', expanded=True):
    with st.form('patient_info_form'):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input('Patient Name')
            gender = st.selectbox('Gender', ['Male', 'Female', 'Other'])
        with col2:
            age = st.number_input('Age', min_value=0, max_value=120, step=1)
            symptoms = st.text_area('Symptoms')
        submitted = st.form_submit_button('Save Patient Info')
    
    if submitted:
        if name and age > 0:
            patient_data = {
                'Name': name,
                'Age': age,
                'Gender': gender,
                'Symptoms': symptoms
            }
            st.session_state['patient'] = patient_data
            
            # Save to database
            patient_id = db_manager.save_patient(st.session_state['doctor']['id'], patient_data)
            if patient_id:
                st.session_state['patient_id'] = patient_id
                st.success('Patient info saved successfully!')
            else:
                st.error('Failed to save patient info to database.')
        else:
            st.warning('Please fill in patient name and age.')

    # --- OLLAMA AI SUGGESTION ---
    if symptoms:
        if st.button('Suggest Medicines with AI (Llama3)'):
            with st.spinner('Querying AI for suggestions...'):
                # Prepare prompt with symptoms and a sample of medicine names + compositions
                prompt = f"""
Given the following patient symptoms: {symptoms}
Suggest the most relevant medicines from this list, based on their compositions:
"""
                # Limit to first 30 medicines for prompt size
                for idx, row in medicines_df.iterrows():
                    prompt += f"\n- {row['name']}: {row['short_composition1']} {row['short_composition2']}"
                    if idx > 30:
                        break
                prompt += "\nReturn only the medicine names, comma separated."
                try:
                    response = requests.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": "llama3",
                            "prompt": prompt,
                            "stream": False
                        },
                        timeout=60
                    )
                    result = response.json()
                    ai_suggestions = [name.strip() for name in result['response'].split(',') if name.strip()]
                    st.session_state['ai_suggested_medicines'] = ai_suggestions
                except Exception as e:
                    st.error(f"Ollama API error: {e}")
        # Show AI suggestions with add buttons
        if 'ai_suggested_medicines' in st.session_state and st.session_state['ai_suggested_medicines']:
            st.write('### AI Suggested Medicines (Click "Add" to include in prescription)')
            for i, med_name in enumerate(st.session_state['ai_suggested_medicines']):
                col_med, col_btn = st.columns([4, 1])
                with col_med:
                    st.write(med_name)
                with col_btn:
                    if st.button(f"Add AI Suggestion", key=f"add_ai_suggested_{i}"):
                        prescription = {
                            'Medicine Name': med_name,
                            'Number of Days': 1,
                            'Dosage per Day': 1,
                            'Meal Time': 'After Meal'
                        }
                        st.session_state['prescriptions'].append(prescription)
                        st.success(f"Added {med_name} to prescription!")

# Audio Processing Functions
def process_audio_file(audio_file):
    """Process uploaded audio file"""
    try:
        # Convert audio to WAV format
        audio = AudioSegment.from_file(audio_file)
        audio = audio.set_frame_rate(16000).set_channels(1)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            audio.export(temp_file.name, format="wav")
            temp_path = temp_file.name
        
        # Transcribe using Whisper
        result = whisper_model.transcribe(temp_path)
        os.unlink(temp_path)  # Clean up temp file
        
        return result["text"]
    except Exception as e:
        st.error(f"Error processing audio: {e}")
        return None

def process_audio_input(audio_bytes):
    """Process recorded audio input"""
    try:
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="wav")
        audio = audio.set_frame_rate(16000).set_channels(1)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            audio.export(temp_file.name, format="wav")
            temp_path = temp_file.name
        
        # Transcribe using Whisper
        result = whisper_model.transcribe(temp_path)
        os.unlink(temp_path)  # Clean up temp file
        
        return result["text"]
    except Exception as e:
        st.error(f"Error processing audio: {e}")
        return None

# Main prescription functionality
if 'patient' in st.session_state:
    # Audio Upload & Recording Section
    with st.expander('Add Prescription via Audio', expanded=True):
        st.write('You can upload an audio file or record your prescription:')
        col1, col2 = st.columns(2)
        
        with col1:
            uploaded_file = st.file_uploader('Upload an audio file', type=['wav', 'mp3', 'm4a'], key='audio_upload')
            if uploaded_file is not None:
                if st.button('Process Uploaded Audio'):
                    with st.spinner('Processing audio...'):
                        transcribed_text = process_audio_file(uploaded_file)
                        if transcribed_text:
                            st.write('**Transcribed Text:**')
                            st.write(transcribed_text)
                            # Extract suggestions only (do not auto-add)
                            suggestions = extract_prescription(transcribed_text, medicines_list)
                            st.session_state['suggested_medicines'] = suggestions
                            if suggestions:
                                st.success(f'Found {len(suggestions)} medicine suggestion(s) from audio!')
                            else:
                                st.warning('No medicines found in the audio.')
        
        with col2:
            simple_audio = st.audio_input('Record your prescription', key='audio_record')
            if simple_audio is not None:
                if st.button('Process Recorded Audio'):
                    with st.spinner('Processing audio...'):
                        audio_bytes = simple_audio.read()
                        transcribed_text = process_audio_input(audio_bytes)
                        if transcribed_text:
                            st.write('**Transcribed Text:**')
                            st.write(transcribed_text)
                            # Extract suggestions only (do not auto-add)
                            suggestions = extract_prescription(transcribed_text, medicines_list)
                            st.session_state['suggested_medicines'] = suggestions
                            if suggestions:
                                st.success(f'Found {len(suggestions)} medicine suggestion(s) from audio!')
                            else:
                                st.warning('No medicines found in the audio.')
        # Show suggested medicines with add buttons
        if 'suggested_medicines' in st.session_state and st.session_state['suggested_medicines']:
            st.write('### Suggested Medicines (Click "Add" to include in prescription)')
            for i, med in enumerate(st.session_state['suggested_medicines']):
                col_med, col_btn = st.columns([4, 1])
                with col_med:
                    st.write(f"{med['Medicine Name']} - {med['Number of Days']} days, {med.get('Dosage per Day', med.get('Tablets per Day', 1))} per day, {med['Meal Time']}")
                with col_btn:
                    if st.button(f"Add", key=f"add_suggested_{i}"):
                        st.session_state['prescriptions'].append(med)
                        st.success(f"Added {med['Medicine Name']} to prescription!")

    # Manual Entry Section
    with st.expander('Add Prescription Manually', expanded=False):
        with st.form('prescription_form'):
            med_name = st.selectbox('Medicine Name', medicines_list)
            if med_name:
                try:
                    med_details = medicines_df[medicines_df['name'].str.strip().str.lower() == med_name.strip().lower()].iloc[0]
                    st.info(f"**Details:** {med_details['manufacturer_name']} - {med_details['type']}")
                except (IndexError, KeyError):
                    st.warning("Could not retrieve details for the selected medicine.")
            
            num_days = st.number_input('Number of Days', min_value=1, max_value=30, step=1, value=1)
            tablets_per_day = st.number_input('Dosage per Day', min_value=1, max_value=10, step=1, value=1)
            meal_time = st.selectbox('When to take?', ['After Meal', 'Before Meal'])
            add_med = st.form_submit_button('Add Medicine')
            
            if add_med and med_name:
                prescription = {
                    'Medicine Name': med_name,
                    'Number of Days': num_days,
                    'Dosage per Day': tablets_per_day,
                    'Meal Time': meal_time
                }
                st.session_state['prescriptions'].append(prescription)
                st.success('Medicine added to prescription!')

    # Prescription List Section
    with st.expander('Current Prescription List', expanded=True):
        if st.session_state['prescriptions']:
            st.write('### Edit Prescriptions')
            for idx, prescription in enumerate(st.session_state['prescriptions']):
                cols = st.columns([3, 2, 2, 3, 2])
                with cols[0]:
                    st.write(prescription['Medicine Name'])
                with cols[1]:
                    num_days = st.number_input('Number of Days', min_value=1, max_value=30, step=1, value=prescription['Number of Days'], key=f'edit_days_{idx}')
                with cols[2]:
                    dosage_per_day = st.number_input('Dosage per Day', min_value=1, max_value=10, step=1, value=prescription.get('Dosage per Day', prescription.get('Tablets per Day', 1)), key=f'edit_dosage_{idx}')
                with cols[3]:
                    meal_time = st.selectbox('Meal Time', ['After Meal', 'Before Meal'], index=0 if prescription['Meal Time'] == 'After Meal' else 1, key=f'edit_meal_{idx}')
                with cols[4]:
                    if st.button('Update', key=f'update_presc_{idx}'):
                        st.session_state['prescriptions'][idx]['Number of Days'] = num_days
                        st.session_state['prescriptions'][idx]['Dosage per Day'] = dosage_per_day
                        st.session_state['prescriptions'][idx]['Meal Time'] = meal_time
                        st.success(f"Updated {prescription['Medicine Name']}!")
            st.write('---')
            df = pd.DataFrame(st.session_state['prescriptions'])
            st.table(df.rename(columns={'Dosage per Day': 'Dosage per Day'}))
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button('Clear All Prescriptions'):
                    st.session_state['prescriptions'] = []
                    st.rerun()
            
            with col2:
                if st.button('Save to Database'):
                    if 'patient_id' in st.session_state:
                        success = db_manager.save_prescriptions(
                            st.session_state['patient_id'],
                            st.session_state['doctor']['id'],
                            st.session_state['prescriptions']
                        )
                        if success:
                            st.success('Prescriptions saved to database!')
                        else:
                            st.error('Failed to save prescriptions to database.')
                    else:
                        st.error('Please save patient info first.')
            
            with col3:
                # PDF Generation
                class PDF(FPDF):
                    def header(self):
                        self.set_font('Helvetica', 'B', 15)
                        self.cell(0, 10, 'AI Prescriptor - Medical Prescription', 0, 1, 'C')
                        self.ln(5)

                    def footer(self):
                        self.set_y(-15)
                        self.set_font('Helvetica', 'I', 8)
                        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
                        self.set_y(-30)
                        self.set_font('Helvetica', 'I', 10)
                        self.cell(0, 10, 'Doctor\'s Signature: ___________________', 0, 1, 'R')

                def create_prescription_pdf(patient_info, prescriptions, doctor_info):
                    pdf = PDF('P', 'mm', 'A4')
                    pdf.add_page()
                    
                    # Header with doctor info
                    pdf.set_font('Helvetica', 'B', 12)
                    pdf.cell(0, 10, f"Dr. {doctor_info['name']}", 0, 1, 'R')
                    if doctor_info.get('specialization'):
                        pdf.set_font('Helvetica', '', 10)
                        pdf.cell(0, 8, f"Specialization: {doctor_info['specialization']}", 0, 1, 'R')
                    pdf.ln(5)
                    
                    # Patient Info
                    pdf.set_font('Helvetica', 'B', 12)
                    pdf.cell(0, 10, 'Patient Information', 0, 1, 'L')
                    pdf.set_font('Helvetica', '', 11)
                    pdf.cell(0, 8, f"Name: {patient_info['Name']}", 0, 1, 'L')
                    pdf.cell(0, 8, f"Age: {patient_info['Age']} / Gender: {patient_info['Gender']}", 0, 1, 'L')
                    pdf.cell(0, 8, f"Date: {datetime.now().strftime('%Y-%m-%d')}", 0, 1, 'L')
                    if patient_info.get('Symptoms'):
                        pdf.cell(0, 8, f"Symptoms: {patient_info['Symptoms']}", 0, 1, 'L')
                    pdf.ln(10)

                    # Prescription Table Header
                    pdf.set_font('Helvetica', 'B', 11)
                    pdf.set_fill_color(230, 230, 230)
                    col_widths = {'Medicine': 60, 'Days': 20, 'Dosage/Day': 25, 'Timing': 40}
                    pdf.cell(col_widths['Medicine'], 10, 'Medicine Name', 1, 0, 'C', True)
                    pdf.cell(col_widths['Days'], 10, 'Days', 1, 0, 'C', True)
                    pdf.cell(col_widths['Dosage/Day'], 10, 'Dosage/Day', 1, 0, 'C', True)
                    pdf.cell(col_widths['Timing'], 10, 'Timing', 1, 1, 'C', True)

                    # Prescription Table Rows
                    pdf.set_font('Helvetica', '', 10)
                    for p in prescriptions:
                        pdf.cell(col_widths['Medicine'], 10, p['Medicine Name'], 1, 0, 'L')
                        pdf.cell(col_widths['Days'], 10, str(p['Number of Days']), 1, 0, 'C')
                        pdf.cell(col_widths['Dosage/Day'], 10, str(p.get('Dosage per Day', p.get('Tablets per Day', 1))), 1, 0, 'C')
                        pdf.cell(col_widths['Timing'], 10, p['Meal Time'], 1, 1, 'L')

                    return bytes(pdf.output())

                pdf_bytes = create_prescription_pdf(
                    st.session_state['patient'], 
                    st.session_state['prescriptions'],
                    st.session_state['doctor']
                )
                
                st.download_button(
                    label="Download Prescription PDF",
                    data=pdf_bytes,
                    file_name=f"prescription_{st.session_state['patient']['Name']}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                )
        else:
            st.info('No prescriptions added yet. Upload an audio file or manually add prescriptions above.')

else:
    st.info('Please fill in patient information above to start creating prescriptions.')

# Database connection cleanup
import atexit
atexit.register(db_manager.close_connection) 