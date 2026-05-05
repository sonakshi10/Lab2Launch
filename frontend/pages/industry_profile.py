import streamlit as st

def industry_profile_page():
    st.title("Create Industry Profile")

    st.caption("Tell us about your company to improve matching.")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Company ID", key="ip1")
        st.text_input("Company Name", key="ip2")
        st.text_input("Industry Domain", key="ip3")

    with col2:
        st.text_input("Location", key="ip4")
        st.text_input("Company Size", key="ip5")
        st.text_input("Business Model", key="ip6")

    if st.button("Save Profile"):
        st.session_state.profile_completed = True
        st.success("Profile created successfully")
        st.rerun()