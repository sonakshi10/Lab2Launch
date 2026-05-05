import streamlit as st
from auth.login import login_page
from pages.researcher import researcher_page
from pages.industry import industry_page
from pages.investor import investor_page

st.set_page_config(layout="wide")

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
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

        role = st.session_state.user_type

        if role == "Researcher":
            researcher_page()
        elif role == "Industry":
            industry_page()
        elif role == "Investor":
            investor_page()

if __name__ == "__main__":
    main()