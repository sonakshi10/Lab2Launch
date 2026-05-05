import streamlit as st

def industry_page():
    st.title("Industry Workspace")

    tab1, tab2, tab3 = st.tabs([
        "Find Researchers",
        "Manage Business & Projects",
        "Find Investors"
    ])

    # -------------------------
    # FIND RESEARCHERS
    # -------------------------
    with tab1:
        st.subheader("Find Researchers")
        st.caption("Describe your problem to find relevant researchers.")

        problem = st.text_area("Problem Statement", key="ind_problem")

        if st.button("Find Best Matches"):
            st.success("Search executed")
            st.write("Matching researchers will appear here")

    # -------------------------
    # BUSINESS + PROJECT
    # -------------------------
    with tab2:
        st.subheader("Business Information")
        st.caption("This helps improve matching accuracy.")

        col1, col2 = st.columns(2)

        with col1:
            st.text_input("Company ID", value="C001", key="b1")
            st.text_input("Company Name", key="b2")
            st.text_input("Industry Domain", key="b3")

        with col2:
            st.text_input("Location", key="b4")
            st.text_input("Company Size", key="b5")
            st.text_input("Business Model", key="b6")

        st.divider()

        st.subheader("Project Details")
        st.caption("Define a project to match with researchers or investors.")

        col1, col2 = st.columns(2)

        with col1:
            st.text_input("Project ID", value="PR001", key="pr1")
            st.text_area("Problem Statement", key="pr2")
            st.text_input("Domains", key="pr3")
            st.text_input("Timeline", key="pr4")

        with col2:
            st.selectbox("Risk Appetite", ["Low", "Medium", "High"], key="pr5")
            st.text_input("Budget", key="pr6")
            st.text_input("Team Size", key="pr7")

        st.text_area("Targets / Expected Outcome", key="pr8")

        public = st.toggle("Make Project Public (visible to researchers & investors)")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Add / Update Project"):
                st.success("Project saved successfully")

        with col2:
            if st.button("Delete Project", type="secondary"):
                st.warning("Project deleted")

        with col3:
            if st.button("Clear Form"):
                st.rerun()

    # -------------------------
    # INVESTORS
    # -------------------------
    with tab3:
        st.subheader("Public Investors")
        st.caption("Browse investors open to funding projects.")

        if st.button("Load Investors"):
            st.success("Loaded investors")
            st.write("Investor list will appear here")