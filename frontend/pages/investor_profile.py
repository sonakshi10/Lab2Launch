import streamlit as st

def investor_profile_page():
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
        st.session_state.profile_completed = True
        st.success("Profile created successfully")
        st.rerun()