import streamlit as st
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from auth.login import login_page
from pages.researcher import researcher_page
from pages.industry import industry_page
from pages.investor import investor_page
from pages.researcher_profile import researcher_profile_page
from pages.industry_profile import industry_profile_page
from pages.investor_profile import investor_profile_page
from components.logo import background_css, logo_header_html, get_logo_base64

st.set_page_config(layout="wide", page_icon="🚀")

from backend.db.profile_repository import init_db

init_db()

# Inject logo background watermark CSS
st.markdown(background_css(), unsafe_allow_html=True)

# Enhanced styling with logo and better colors
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

* {
    font-family: 'Poppins', sans-serif;
}

[data-testid="stSidebarNav"] {display: none;}

/* Header and Title Styling */
h1, h2, h3 {
    color: #0f6b57;
    font-weight: 700;
}

/* Enhanced Button Styling */
div.stButton > button {
    background: linear-gradient(135deg, #0f6b57 0%, #0a4e3f 100%);
    color: white;
    border-radius: 8px;
    font-weight: 600;
    border: none;
    padding: 10px 20px;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(15, 107, 87, 0.2);
}

div.stButton > button:hover {
    background: linear-gradient(135deg, #0a4e3f 0%, #063d30 100%);
    box-shadow: 0 4px 12px rgba(15, 107, 87, 0.4);
    transform: translateY(-2px);
}

/* Enhanced Dashboard Card */
.dash-card {
    border: 2px solid #e8f3f0;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    background: linear-gradient(135deg, #ffffff 0%, #f0faf8 100%);
    min-height: 100px;
    box-shadow: 0 2px 8px rgba(15, 107, 87, 0.08);
    transition: all 0.3s ease;
}

.dash-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(15, 107, 87, 0.15);
    border-color: #0f6b57;
}

.dash-label {
    color: #0f6b57;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.5rem;
}

.dash-value {
    color: #14231f;
    font-size: 1.5rem;
    font-weight: 700;
    line-height: 1.25;
}

.dash-note {
    color: #6f7f79;
    font-size: 0.85rem;
    margin-top: 0.5rem;
    line-height: 1.4;
}

/* Result Pills with gradient */
.result-pill {
    display: inline-block;
    border: 1px solid #0f6b57;
    border-radius: 20px;
    padding: 0.35rem 0.75rem;
    margin: 0.15rem 0.35rem 0.15rem 0;
    background: linear-gradient(135deg, #e8f3f0 0%, #d4e9e3 100%);
    color: #0f6b57;
    font-size: 0.8rem;
    font-weight: 600;
    transition: all 0.2s ease;
}

.result-pill:hover {
    background: linear-gradient(135deg, #0f6b57 0%, #0a4e3f 100%);
    color: white;
}

/* Delete Button Styling */
.delete-btn button {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
}

.delete-btn button:hover {
    background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%) !important;
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] button {
    color: #0f6b57;
    font-weight: 600;
    border-radius: 8px 8px 0 0;
}

.stTabs [aria-selected="true"] {
    border-bottom: 3px solid #0f6b57;
    color: #0f6b57 !important;
}

/* Input fields enhancement */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
    border: 2px solid #e8f3f0 !important;
    border-radius: 8px !important;
    padding: 10px 12px !important;
    transition: all 0.3s ease !important;
}

.stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus {
    border-color: #0f6b57 !important;
    box-shadow: 0 0 0 3px rgba(15, 107, 87, 0.1) !important;
}

/* Divider styling */
hr {
    border-color: #e8f3f0;
    margin: 2rem 0;
}

/* Logo container */
.logo-header {
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 2rem 0;
    gap: 1.5rem;
}

.logo-header img {
    height: 80px;
    width: auto;
}

.logo-title {
    color: #0f6b57;
    font-size: 2rem;
    font-weight: 700;
}

.logo-subtitle {
    color: #6f7f79;
    font-size: 0.95rem;
    letter-spacing: 3px;
}

/* Success message styling */
.stSuccess {
    background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%) !important;
    border: 1px solid #6ee7b7 !important;
    border-radius: 8px !important;
}

/* Error message styling */
.stError {
    background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%) !important;
    border: 1px solid #fca5a5 !important;
    border-radius: 8px !important;
}

/* Container styling */
.stContainer {
    background: #ffffff;
    border-radius: 12px;
    padding: 1.5rem;
}

</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_type" not in st.session_state:
    st.session_state.user_type = None

# Add logo and title at the top when the user is logged in
if st.session_state.get("logged_in", False):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(logo_header_html(height=90), unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <h1 style="color: #0f6b57; margin-bottom: 0;">Lab2Launch</h1>
            <p style="color: #6f7f79; font-size: 0.95rem; letter-spacing: 2px; text-transform: uppercase;">
                Research • Connect • Launch
            </p>
        </div>
        """, unsafe_allow_html=True)
    # Sidebar logo
    logo_b64 = get_logo_base64()
    st.sidebar.markdown(
        f'<div style="text-align:center; padding:1rem 0 0.5rem;">'
        f'<img src="data:image/jpeg;base64,{logo_b64}" style="width:120px; height:auto;">'
        f'</div>',
        unsafe_allow_html=True,
    )

def main():
    if not st.session_state.logged_in:
        login_page()

    else:
        role = str(st.session_state.user_type).strip().lower()

        if st.session_state.get("just_signed_up", False) and not st.session_state.get("profile_completed", False):

            if role == "researcher":
                researcher_profile_page()

            elif role == "industry":
                industry_profile_page()

            elif role == "investor":
                investor_profile_page()

        else:
            # normal dashboard
            if st.sidebar.button("Logout"):
                st.session_state.clear()
                st.rerun()

            if role == "researcher":
                researcher_page()

            elif role == "industry":
                industry_page()

            elif role == "investor":
                investor_page()

if __name__ == "__main__":
    main()
