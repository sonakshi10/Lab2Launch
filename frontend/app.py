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

st.set_page_config(layout="wide")

from backend.db.profile_repository import init_db

init_db()

# hide default nav
st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none;}
div.stButton > button {
    background-color: #0f6b57;
    color: white;
    border-radius: 6px;
    font-weight: 600;
}

div.stButton > button:hover {
    background-color: #0a4e3f;
}

.delete-btn button {
    background-color: #a23b3b !important;
}

.delete-btn button:hover {
    background-color: #7a2c2c !important;
}

</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_type" not in st.session_state:
    st.session_state.user_type = None

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
