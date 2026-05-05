import streamlit as st

def login_page():
    st.title("Lab2Launch")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        user_type = st.selectbox(
            "Login as",
            ["Researcher", "Industry", "Investor"],
            key="login_role"
        )

        if st.button("Login"):
            if email and password:
                st.session_state.logged_in = True
                st.session_state.user_type = user_type
                st.rerun()
            else:
                st.error("Enter credentials")

    with tab2:
        st.text_input("Name", key="signup_name")
        st.text_input("Email", key="signup_email")
        st.text_input("Password", type="password", key="signup_pass")

        st.selectbox(
            "Register as",
            ["Researcher", "Industry", "Investor"],
            key="signup_role"
        )

        if st.button("Sign Up"):
            st.success("User created (connect DB later)")