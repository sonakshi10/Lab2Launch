import streamlit as st
import requests
from backend.db.profile_repository import save_researcher_profile


API_URL = "http://localhost:8000"


def _post_json(path, payload):
    response = requests.post(f"{API_URL}{path}", json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


def _post_form(path, data, files=None):
    response = requests.post(f"{API_URL}{path}", data=data, files=files, timeout=180)
    response.raise_for_status()
    return response.json()


def _shorten(text, limit=420):
    text = str(text or "").strip()
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + "..."


def _show_project(project):
    with st.container(border=True):
        st.markdown(f"**{project.get('project_id', '')} - {project.get('company_name', '')}**")
        st.write(_shorten(project.get("problem")))
        cols = st.columns(4)
        cols[0].metric("Domain", _shorten(project.get("domain"), 32))
        cols[1].metric("Budget", project.get("budget") or "-")
        cols[2].metric("Risk", project.get("risk") or "-")
        cols[3].metric("Timeline", project.get("timeline") or "-")
        if project.get("targets"):
            st.caption(_shorten(project.get("targets"), 240))


def _show_researcher(researcher):
    with st.container(border=True):
        st.markdown(f"**{researcher.get('name') or researcher.get('researcher_id')}**")
        st.caption(f"{researcher.get('affiliation', '')} | {researcher.get('country', '')}")
        cols = st.columns(3)
        cols[0].metric("h-index", researcher.get("h_index") or "-")
        cols[1].metric("i10-index", researcher.get("i10_index") or "-")
        cols[2].metric("Grants", researcher.get("grants") or "-")
        st.write(f"Matched paper: {researcher.get('matching_paper_title', '-')}")
        if researcher.get("keywords"):
            st.caption(researcher["keywords"])


def _show_paper(paper):
    with st.container(border=True):
        st.markdown(f"**{paper.get('title') or paper.get('paper_id')}**")
        st.caption(
            f"{paper.get('paper_id', '')} | {paper.get('venue', '')} | "
            f"{paper.get('year', '')} | citations: {paper.get('citations', '-')}"
        )
        st.write(_shorten(paper.get("summary") or paper.get("abstract")))
        if paper.get("keywords"):
            st.caption(paper["keywords"])
        if paper.get("pdf_link"):
            st.markdown(f"[Open PDF]({paper['pdf_link']})")

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
            st.text_input(
                "Researcher ID",
                value=st.session_state.get("rp1", ""),
                key="r1"
            )

            st.text_input(
                "Full Name",
                value=st.session_state.get("rp2", ""),
                key="r2"
            )

            st.text_input(
                "Research Domain",
                value=st.session_state.get("rp3", ""),
                key="r3"
            )

        with col2:
            st.number_input(
                "h-index",
                value=st.session_state.get("rp4", 0),
                key="r4"
            )

            st.number_input(
                "i10-index",
                value=st.session_state.get("rp5", 0),
                key="r5"
            )

        st.text_area(
            "Key Areas / Keywords",
            value=st.session_state.get("rp6", ""),
            key="r6"
        )

        if st.button("Save Profile", key="researcher_dashboard_save_profile"):
            user_id = st.session_state.get("user_id")
            if not user_id:
                st.error("Session expired. Please log out and sign in again.")
                return

            save_researcher_profile(
                user_id,
                (
                    st.session_state.r1,
                    st.session_state.r2,
                    st.session_state.r3,
                    st.session_state.r4,
                    st.session_state.r5,
                    st.session_state.r6,
                ),
            )
            st.session_state.rp1 = st.session_state.r1
            st.session_state.rp2 = st.session_state.r2
            st.session_state.rp3 = st.session_state.r3
            st.session_state.rp4 = st.session_state.r4
            st.session_state.rp5 = st.session_state.r5
            st.session_state.rp6 = st.session_state.r6
            st.success("Profile saved successfully")

        st.divider()

        # -------------------------
        # PROJECTS
        # -------------------------
        st.subheader("Relevant Projects")
        st.caption("Projects aligned with your research interests.")

        project_query = " ".join([
            st.session_state.get("r3", ""),
            st.session_state.get("r6", ""),
        ]).strip()

        if st.button("Find Relevant Projects", key="find_relevant_projects"):
            if not project_query:
                st.error("Add a research domain or keywords first.")
            else:
                try:
                    data = _post_json(
                        "/researcher/relevant-projects",
                        {"query": project_query, "n_results": 6},
                    )
                    st.session_state.relevant_projects = data.get("results", [])
                except Exception as exc:
                    st.error(f"Could not load projects: {exc}")

        projects = st.session_state.get("relevant_projects", [])
        if projects:
            for project in projects:
                _show_project(project)
        else:
            st.info("Run the project search to see matched opportunities.")

        st.divider()

        # -------------------------
        # RESEARCHERS
        # -------------------------
        st.subheader("Similar Researchers")

        query = st.text_area(
            "Describe your research focus",
            key="res_q"
        )

        if st.button("Find Similar Researchers", key="find_similar_researchers"):
            if not query.strip():
                st.error("Describe your research focus first.")
            else:
                try:
                    data = _post_json(
                        "/researcher/similar-researchers",
                        {"query": query, "n_results": 8},
                    )
                    st.session_state.similar_researchers = data.get("results", [])
                except Exception as exc:
                    st.error(f"Could not find researchers: {exc}")

        researchers = st.session_state.get("similar_researchers", [])
        if researchers:
            for researcher in researchers:
                _show_researcher(researcher)

    # -------------------------
    # UPLOAD PAPER
    # -------------------------
    with tab2:
        st.subheader("Upload Research Paper")

        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"], key="paper_pdf")

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

        if st.button("Upload & Save Paper", key="upload_save_paper"):
            if not st.session_state.p1 or not st.session_state.p2:
                st.error("Paper ID and title are required.")
            else:
                researcher_id = st.session_state.get("r1") or st.session_state.get("rp1") or st.session_state.get("user_id", "")
                form_data = {
                    "user_id": st.session_state.get("user_id", ""),
                    "researcher_id": researcher_id,
                    "paper_id": st.session_state.p1,
                    "title": st.session_state.p2,
                    "year": int(st.session_state.p3 or 0),
                    "venue": st.session_state.p4,
                    "impact_score": int(st.session_state.p5 or 0),
                    "citations": int(st.session_state.p6 or 0),
                    "pages": int(st.session_state.p7 or 0),
                    "keywords": st.session_state.p8,
                    "abstract": st.session_state.p9,
                    "paper_type": "Uploaded",
                }
                files = None
                if uploaded_file is not None:
                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf",
                        )
                    }

                try:
                    data = _post_form("/researcher/papers/upload", form_data, files)
                    if data.get("status") == "success":
                        st.success(f"Paper saved: {data.get('paper_id')}")
                    else:
                        st.error(data.get("message", "Paper upload failed"))
                except Exception as exc:
                    st.error(f"Could not upload paper: {exc}")

    # -------------------------
    # SEARCH PAPERS
    # -------------------------
    with tab3:
        st.subheader("Search Papers")

        query = st.text_input("Search papers", key="search_papers")

        if st.button("Search Papers", key="search_papers_button"):
            if not query.strip():
                st.error("Enter a paper search query.")
            else:
                try:
                    data = _post_json(
                        "/researcher/papers/search",
                        {"query": query, "n_results": 8},
                    )
                    st.session_state.paper_search_results = data.get("results", [])
                except Exception as exc:
                    st.error(f"Could not search papers: {exc}")

        papers = st.session_state.get("paper_search_results", [])
        if papers:
            for paper in papers:
                _show_paper(paper)
