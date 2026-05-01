import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        .stApp {
            background-color: #2b2b2b;
            background-image: 
                radial-gradient(#3a3a3a 15%, transparent 16%),
                radial-gradient(#3a3a3a 15%, transparent 16%),
                linear-gradient(#2b2b2b 0%, #333333 100%);
            background-size: 100px 100px, 100px 100px, 100% 100%;
            background-position: 0 0, 50px 50px, 0 0;
            color: #e0e0e0;
        }
        .hero-title {
            font-size: 3.5rem !important; 
            font-weight: 900;
            color: #fff;
            text-align: center;
            text-shadow: 0 0 20px #00c3ff, 0 0 40px #00c3ff;
            margin-top: 20px;
            line-height: 1.1;
        }
        .hero-subtitle {
            font-size: 1.2rem;
            color: #00c3ff;
            text-align: center;
            margin-bottom: 40px;
            font-weight: bold;
            letter-spacing: 5px;
        }
        .q-card {
            padding: 25px;
            border-radius: 15px;
            background: rgba(40, 40, 40, 0.85);
            border: 2px solid #00c3ff;
            box-shadow: 0 0 20px rgba(0, 195, 255, 0.4);
            margin-bottom: 25px;
        }
        .q-card h3 {
            font-size: 1.3rem !important;
            color: #fff;
            line-height: 1.6;
        }
        div.stButton > button {
            border-radius: 8px;
            border: 1px solid #00c3ff;
            background: rgba(0, 195, 255, 0.1) !important;
            color: #00c3ff !important;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)