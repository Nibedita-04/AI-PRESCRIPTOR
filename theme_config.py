import streamlit as st

def apply_theme(theme):
    """Apply light or dark theme to the application"""
    if theme == 'Dark':
        # Dark theme CSS
        dark_theme = """
        <style>
        .stApp {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        
        .stTextInput > div > div > input {
            background-color: #2d2d2d;
            color: #ffffff;
            border-color: #555555;
        }
        
        .stSelectbox > div > div > select {
            background-color: #2d2d2d;
            color: #ffffff;
            border-color: #555555;
        }
        
        .stTextArea > div > div > textarea {
            background-color: #2d2d2d;
            color: #ffffff;
            border-color: #555555;
        }
        
        .stNumberInput > div > div > input {
            background-color: #2d2d2d;
            color: #ffffff;
            border-color: #555555;
        }
        
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
        }
        
        .stButton > button:hover {
            background-color: #45a049;
        }
        
        .stExpander {
            background-color: #2d2d2d;
            border-color: #555555;
        }
        
        .stDataFrame {
            background-color: #2d2d2d;
            color: #ffffff;
        }
        
        .stTable {
            background-color: #2d2d2d;
            color: #ffffff;
        }
        
        .stSidebar {
            background-color: #2d2d2d;
            color: #ffffff;
        }
        
        .stRadio > div > div > label {
            color: #ffffff;
        }
        
        .stFileUploader > div > div > div {
            background-color: #2d2d2d;
            border-color: #555555;
        }
        
        .stAudioInput > div > div > div {
            background-color: #2d2d2d;
            border-color: #555555;
        }
        
        .stForm {
            background-color: #2d2d2d;
            border-color: #555555;
        }
        
        .stSuccess {
            background-color: #2d2d2d;
            color: #4CAF50;
        }
        
        .stError {
            background-color: #2d2d2d;
            color: #f44336;
        }
        
        .stWarning {
            background-color: #2d2d2d;
            color: #ff9800;
        }
        
        .stInfo {
            background-color: #2d2d2d;
            color: #2196F3;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff;
        }
        
        p {
            color: #ffffff;
        }
        
        .stMarkdown {
            color: #ffffff;
        }
        </style>
        """
        st.markdown(dark_theme, unsafe_allow_html=True)
    else:
        # Light theme CSS (default Streamlit theme)
        light_theme = """
        <style>
        .stApp {
            background-color: #ffffff;
            color: #262730;
        }
        .stTextInput > div > div > input {
            background-color: #fff;
            color: #262730;
            border-color: #e0e0e0;
        }
        .stSelectbox > div > div > select {
            background-color: #fff;
            color: #262730;
            border-color: #e0e0e0;
        }
        .stTextArea > div > div > textarea {
            background-color: #fff;
            color: #262730;
            border-color: #e0e0e0;
        }
        .stNumberInput > div > div > input {
            background-color: #fff;
            color: #262730;
            border-color: #e0e0e0;
        }
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
        }
        .stButton > button:hover {
            background-color: #45a049;
        }
        .stExpander {
            background-color: #fff;
            border-color: #e0e0e0;
            color: #262730;
        }
        .stDataFrame {
            background-color: #fff;
            color: #262730;
        }
        .stTable {
            background-color: #fff;
            color: #262730;
        }
        .stSidebar {
            background-color: #f0f2f6;
            color: #262730;
        }
        .stRadio > div > div > label {
            color: #262730;
        }
        .stFileUploader > div > div > div {
            background-color: #fff;
            border-color: #e0e0e0;
        }
        .stAudioInput > div > div > div {
            background-color: #fff;
            border-color: #e0e0e0;
        }
        .stForm {
            background-color: #fff;
            border-color: #e0e0e0;
            color: #262730;
        }
        .stSuccess {
            background-color: #fff;
            color: #4CAF50;
        }
        .stError {
            background-color: #fff;
            color: #f44336;
        }
        .stWarning {
            background-color: #fff;
            color: #ff9800;
        }
        .stInfo {
            background-color: #fff;
            color: #2196F3;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #262730;
        }
        p {
            color: #262730;
        }
        .stMarkdown {
            color: #262730;
        }
        </style>
        """
        st.markdown(light_theme, unsafe_allow_html=True)

def get_theme_colors(theme):
    """Get color scheme based on theme"""
    if theme == 'Dark':
        return {
            'primary': '#4CAF50',
            'secondary': '#45a049',
            'background': '#1e1e1e',
            'surface': '#2d2d2d',
            'text': '#ffffff',
            'border': '#555555'
        }
    else:
        return {
            'primary': '#4CAF50',
            'secondary': '#45a049',
            'background': '#ffffff',
            'surface': '#f0f2f6',
            'text': '#262730',
            'border': '#e0e0e0'
        } 