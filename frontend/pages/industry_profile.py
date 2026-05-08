import streamlit as st
from backend.db.profile_repository import save_industry_profile


def industry_profile_page():
    st.title("Create Industry Profile")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Company ID", key="indp1")
        st.text_input("Company Name", key="indp2")
        st.text_input("Industry Domain", key="indp3")

    with col2:
        st.text_input("Location", key="indp4")
        st.selectbox("Company Size", ["Startup", "SME", "Enterprise"], key="indp5")

    st.text_area("Business Model / Collaboration Interests", key="indp6")

    if st.button("Save Profile"):
        user_id = st.session_state.get("user_id")
        if not user_id:
            st.error("Session expired. Please log out and sign in again.")
            return

        save_industry_profile(
            user_id,
            (
                st.session_state.indp1,
                st.session_state.indp2,
                st.session_state.indp3,
                st.session_state.indp4,
                st.session_state.indp5,
                st.session_state.indp6,
            ),
        )
        st.session_state.ip1 = st.session_state.indp1
        st.session_state.ip2 = st.session_state.indp2
        st.session_state.ip3 = st.session_state.indp3
        st.session_state.ip4 = st.session_state.indp4
        st.session_state.ip5 = st.session_state.indp5
        st.session_state.ip6 = st.session_state.indp6
        st.session_state.profile_completed = True
        st.success("Saved permanently")
        st.rerun()
