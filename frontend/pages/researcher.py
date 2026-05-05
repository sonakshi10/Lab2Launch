import streamlit as st

def researcher_page():
    st.title("Researcher Workspace")

    tab1, tab2, tab3 = st.tabs([
        "Profile & Opportunities",
        "Upload Paper",
        "Search Papers"
    ])

    # -------------------------
    # PROFILE + OPPORTUNITIES
    # -------------------------
    with tab1:
        st.subheader("Researcher Profile")
        st.caption("These details help match you with projects and collaborators.")

        col1, col2 = st.columns(2)

        with col1:
            researcher_id = st.text_input("Researcher ID", value="R001", key="r1")
            name = st.text_input("Full Name", value="John Doe", key="r2")
            domain = st.text_input(
                "Research Domain",
                value="AI, Climate",
                key="r3"
            )

        with col2:
            h_index = st.number_input(
                "h-index (impact of your research)",
                value=10,
                key="r4"
            )
            i10_index = st.number_input(
                "i10-index (papers with 10+ citations)",
                value=5,
                key="r5"
            )

        st.text_area(
            "Key Areas / Keywords",
            value="machine learning, sustainability",
            key="r6"
        )

        if st.button("Save Profile"):
            st.success("Profile saved successfully")

        st.divider()

        # -------------------------
        # PROJECTS
        # -------------------------
        st.subheader("Relevant Projects")
        st.caption("Projects aligned with your research interests.")

        st.info("Projects will appear here")

        st.divider()

        # -------------------------
        # RESEARCHERS
        # -------------------------
        st.subheader("Similar Researchers")

        query = st.text_area(
            "Describe your research focus",
            key="res_q"
        )

        if st.button("Find Similar Researchers"):
            st.success("Search executed")
            st.write("Matching researchers will appear here")

    # -------------------------
    # UPLOAD PAPER
    # -------------------------
    with tab2:
        st.subheader("Upload Research Paper")

        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

        col1, col2 = st.columns(2)

        with col1:
            st.text_input("Paper ID", value="P001", key="p1")
            st.text_input("Title", key="p2")
            st.number_input("Publication Year", value=2023, key="p3")
            st.text_input("Venue", key="p4")

        with col2:
            st.number_input("Impact Score", value=0, key="p5")
            st.number_input("Citations", value=0, key="p6")
            st.number_input("Pages", value=10, key="p7")

        st.text_area("Keywords", key="p8")
        st.text_area("Abstract", key="p9")

        if st.button("Upload & Save Paper"):
            st.success("Paper uploaded successfully")

    # -------------------------
    # SEARCH PAPERS
    # -------------------------
    with tab3:
        st.subheader("Search Papers")

        query = st.text_input("Search papers", key="search_papers")

        if st.button("Search Papers"):
            st.success("Search executed")
            st.write("Results will appear here")