import streamlit as st
import requests
from backend.db.profile_repository import (
    load_industry_profile,
    load_investor_profile,
    load_researcher_profile,
)

API_URL = "http://localhost:8000"


def login_page():
    st.title("Lab2Launch")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    # ---------------- LOGIN ----------------
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):

            if not email or not password:
                st.error("Please enter email and password")
                return

            try:
                res = requests.post(
                    f"{API_URL}/login",
                    json={
                        "email": email,
                        "password": password
                    }
                )

                data = res.json()

                if data["status"] == "success":
                    user_id = data.get("user_id", email)

                    st.session_state.logged_in = True
                    st.session_state.user_type = data["role"]
                    st.session_state.profile_completed = True
                    st.session_state.just_signed_up = False
                    st.session_state.user_id = user_id

                    # -------- LOAD RESEARCHER --------
                    res = load_researcher_profile(user_id)
                    if res:
                        _, rid, name, domain, h, i10, kw = res
                        st.session_state.rp1 = rid
                        st.session_state.rp2 = name
                        st.session_state.rp3 = domain
                        st.session_state.rp4 = h
                        st.session_state.rp5 = i10
                        st.session_state.rp6 = kw

                    # -------- LOAD INDUSTRY --------
                    ind = load_industry_profile(user_id)
                    if ind:
                        _, cid, name, domain, loc, size, model = ind
                        st.session_state.ip1 = cid
                        st.session_state.ip2 = name
                        st.session_state.ip3 = domain
                        st.session_state.ip4 = loc
                        st.session_state.ip5 = size
                        st.session_state.ip6 = model

                    # -------- LOAD INVESTOR --------
                    inv = load_investor_profile(user_id)
                    if inv:
                        _, iid, name, domain, risk, geo, invs = inv
                        st.session_state.invp1 = iid
                        st.session_state.invp2 = name
                        st.session_state.invp3 = domain
                        st.session_state.invp4 = risk
                        st.session_state.invp5 = geo
                        st.session_state.invp6 = invs

                    st.rerun()
                else:
                    st.error(data["message"])

            except Exception as e:
                st.error("Backend not running")


    # ---------------- SIGNUP ----------------
    with tab2:
        name = st.text_input("Name", key="signup_name")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pass")

        signup_role = st.selectbox(
            "Register as",
            ["Researcher", "Industry", "Investor"],
            key="signup_role"
        )

        if st.button("Sign Up"):

            if not email or not password or not name:
                st.error("All fields required")
                return

            try:
                res = requests.post(
                    f"{API_URL}/signup",
                    json={
                        "email": email,
                        "password": password,
                        "role": signup_role.lower()
                    }
                )

                data = res.json()

                if data["status"] == "success":
                    st.session_state.user_id = data.get("user_id", email)
                    st.session_state.logged_in = True
                    st.session_state.user_type = signup_role.lower()
                    st.session_state.profile_completed = False
                    st.session_state.just_signed_up = True
                    st.rerun()
                else:
                    st.error(data["message"])

            except Exception as e:
                st.error("Backend not running")
