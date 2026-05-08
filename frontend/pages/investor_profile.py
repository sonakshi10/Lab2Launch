import streamlit as st
from backend.db.profile_repository import save_investor_profile
from components.logo import logo_header_html

def investor_profile_page():
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.markdown(logo_header_html(height=90), unsafe_allow_html=True)
    st.title("Create Investor Profile")

    st.caption("Define your investment interests.")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Investor ID", key="invp1")
        st.text_input("Name", key="invp2")
        st.text_input("Domains of Interest", key="invp3")

    with col2:
        st.selectbox("Risk Appetite", ["Low", "Medium", "High"], key="invp4")
        st.text_input("Geographic Focus", key="invp5")

    st.text_area("Previous Investments", key="invp6")

    if st.button("Save Profile"):
        user_id = st.session_state.get("user_id")
        if not user_id:
            st.error("Session expired. Please log out and sign in again.")
            return

        save_investor_profile(
            user_id,
            (
                st.session_state.invp1,
                st.session_state.invp2,
                st.session_state.invp3,
                st.session_state.invp4,
                st.session_state.invp5,
                st.session_state.invp6,
            ),
        )
        st.session_state.profile_completed = True
        st.success("Saved permanently")
        st.rerun()
