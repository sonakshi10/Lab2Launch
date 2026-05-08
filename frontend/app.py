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
from components.logo import background_css, get_logo_base64

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
    color: #1e40af;
    font-weight: 700;
}
            
                        
/* Enhanced Button Styling */
div.stButton > button {
    background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%);
    color: white;
    border-radius: 8px;
    font-weight: 600;
    border: none;
    padding: 10px 20px;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(30, 64, 175, 0.2);
}

div.stButton > button:hover {
    background: linear-gradient(135deg, #1e3a8a 0%, #172554 100%);
    box-shadow: 0 4px 12px rgba(30, 64, 175, 0.4);
    transform: translateY(-2px);
}

/* Enhanced Dashboard Card */
.dash-card {
    border: 2px solid #e0f2fe;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
    min-height: 100px;
    box-shadow: 0 2px 8px rgba(30, 64, 175, 0.08);
    transition: all 0.3s ease;
}

.dash-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(30, 64, 175, 0.15);
    border-color: #1e40af;
}

.dash-label {
    color: #1e40af;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.5rem;
}

.dash-value {
    color: #0f172a;
    font-size: 1.5rem;
    font-weight: 700;
    line-height: 1.25;
}

.dash-note {
    color: #64748b;
    font-size: 0.85rem;
    margin-top: 0.5rem;
    line-height: 1.4;
}

/* Domain box styling */
input[type="text"][value*="Domain"],
.domain-input {
    max-width: 200px !important;
    font-size: 0.9rem !important;
}

/* Result Pills with gradient */
.result-pill {
    display: inline-block;
    border: 1px solid #1e40af;
    border-radius: 20px;
    padding: 0.35rem 0.75rem;
    margin: 0.15rem 0.35rem 0.15rem 0;
    background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
    color: #1e40af;
    font-size: 0.8rem;
    font-weight: 600;
    transition: all 0.2s ease;
}

.result-pill:hover {
    background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%);
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
    color: #1e40af;
    font-weight: 600;
    border-radius: 8px 8px 0 0;
}

.stTabs [aria-selected="true"] {
    border-bottom: 3px solid #1e40af;
    color: #1e40af !important;
}

/* Input fields enhancement */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
    border: 2px solid #e0f2fe !important;
    border-radius: 8px !important;
    padding: 10px 12px !important;
    transition: all 0.3s ease !important;
}

.stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus {
    border-color: #1e40af !important;
    box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1) !important;
}

/* Divider styling */
hr {
    border-color: #e0f2fe;
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
    color: #1e40af;
    font-size: 2rem;
    font-weight: 700;
}

.logo-subtitle {
    color: #64748b;
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

# Top navbar - thin gray horizontal strip
if st.session_state.get("logged_in", False):
    logo_b64 = get_logo_base64()
    st.markdown(
        f"""
        <style>
        .navbar {{
            width: 100%;
            background-color: #f3f4f6;
            padding: 1rem 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid #e5e7eb;
            box-shadow: 0 1px 4px rgba(15, 23, 42, 0.06);
            box-sizing: border-box;
        }}
        .navbar-left {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        .navbar-logo {{
            width: 70px;
            height: auto;
        }}
        .navbar-text h2 {{
            margin: 0;
            font-size: 1.35rem;
            color: #1e40af;
            font-weight: 700;
        }}
        .navbar-text p {{
            margin: 0;
            font-size: 0.78rem;
            color: #64748b;
            letter-spacing: 0.12em;
        }}
        button[aria-label="Logout"] {{
            position: relative;
            top: -80px !important;
            margin-bottom: 0.35rem;
            max-width: 140px;
        }}
        .stButton {{
            margin-bottom: 0 !important;
        }}
        </style>
        <div class="navbar">
            <div class="navbar-left">
                <img src="data:image/jpeg;base64,{logo_b64}" class="navbar-logo" alt="Lab2Launch">
                <div class="navbar-text">
                    <h2>Lab2Launch</h2>
                    <p>RESEARCH • CONNECT • LAUNCH</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("""
    <style>
    .logout-row {
        margin-top: -80px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="logout-row">', unsafe_allow_html=True)
    logout_col1, logout_col2 = st.columns([0.85, 0.15])
    with logout_col2:
        if st.button("Logout", key="top_logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    st.divider()
    st.markdown('</div>', unsafe_allow_html=True)
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
            if role == "researcher":
                researcher_page()

            elif role == "industry":
                industry_page()

            elif role == "investor":
                investor_page()

        # Remove sidebar nav items for cleaner dashboard
        st.sidebar.markdown("")

if __name__ == "__main__":
    main()
