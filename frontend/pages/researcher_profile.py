import streamlit as st

def researcher_profile_page():
    st.title("Create Researcher Profile")

    st.caption("Complete your profile to start discovering opportunities.")

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
        st.session_state.profile_completed = True
        st.success("Profile created successfully")
        st.rerun()