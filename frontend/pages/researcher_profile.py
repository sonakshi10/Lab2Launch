import streamlit as st
from backend.db.profile_repository import save_researcher_profile
from components.logo import logo_header_html

def researcher_profile_page():
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.markdown(logo_header_html(height=90), unsafe_allow_html=True)
    st.title("Create Researcher Profile")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Researcher ID", key="rp1")
        st.text_input("Full Name", key="rp2")
        st.text_input("Primary Domain", key="rp3")

    with col2:
        st.number_input("h-index", key="rp4")
        st.number_input("i10-index", key="rp5")

    st.text_area("Key Research Areas / Keywords", key="rp6")

    if st.button("Save Profile"):
        user_id = st.session_state.get("user_id")
        if not user_id:
            st.error("Session expired. Please log out and sign in again.")
            return

        save_researcher_profile(
            user_id,
            (
                st.session_state.rp1,
                st.session_state.rp2,
                st.session_state.rp3,
                st.session_state.rp4,
                st.session_state.rp5,
                st.session_state.rp6,
            ),
        )
        st.session_state.profile_completed = True
        st.success("Saved permanently")
        st.rerun()
