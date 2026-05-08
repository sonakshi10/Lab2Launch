import requests
import streamlit as st
from backend.db.profile_repository import save_industry_profile
from components.metrics import show_industry_metrics, display_metrics_breakdown


API_URL = "http://localhost:8000"


def _post_json(path, payload):
    response = requests.post(f"{API_URL}{path}", json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


def _shorten(text, limit=420):
    text = str(text or "").strip()
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + "..."


def _match_score(distance):
    if distance in (None, ""):
        return "-"
    try:
        return f"{round(100 / (1 + float(distance)))}%"
    except (TypeError, ValueError):
        return "-"


def _percent(value):
    try:
        return f"{round(float(value) * 100)}%"
    except (TypeError, ValueError):
        return "-"


def _metric_card(label, value, note=""):
    st.markdown(
        f"""
        <div class="dash-card">
            <div class="dash-label">{label}</div>
            <div class="dash-value">{value or "-"}</div>
            <div class="dash-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _dashboard_metrics(items):
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        with col:
            _metric_card(*item)


def _show_researcher(researcher):
    with st.container(border=True):
        st.markdown(f"**{researcher.get('name') or researcher.get('researcher_id')}**")
        st.caption(f"{researcher.get('affiliation', '')} | {researcher.get('country', '')}")
        st.markdown(
            f"""
            <span class="result-pill">Match {_match_score(researcher.get("distance"))}</span>
            <span class="result-pill">{researcher.get("language") or "Language -"}</span>
            """,
            unsafe_allow_html=True,
        )
        _dashboard_metrics([
            ("h-index", researcher.get("h_index"), "Research impact"),
            ("i10-index", researcher.get("i10_index"), "10+ citation papers"),
            ("Patents", researcher.get("patents"), "IP signal"),
            ("Grants", researcher.get("grants"), "Funded work"),
        ])
        
        # Display recommendation metrics if available
        if researcher.get("metrics"):
            show_industry_metrics(researcher["metrics"])
            display_metrics_breakdown(researcher["metrics"])
        
        st.write(f"Matched paper: {researcher.get('matching_paper_title', '-')}")
        st.caption(_shorten(researcher.get("summary"), 260))


def _show_investor(investor):
    with st.container(border=True):
        st.markdown(f"**{investor.get('name') or investor.get('investor_id')}**")
        st.caption(f"{investor.get('investor_type', '')} | {investor.get('geo', '')}")
        _dashboard_metrics([
            ("Budget", investor.get("budget"), "Capital available"),
            ("Risk", investor.get("risk"), "Risk appetite"),
            ("Funded", investor.get("projects_funded"), "Projects backed"),
            ("Success", _percent(investor.get("success_rate")), "Portfolio rate"),
        ])
        st.write(_shorten(investor.get("domains"), 280))
        if investor.get("previous_projects"):
            st.caption(f"Previous projects: {investor['previous_projects']}")


def industry_page():
    st.title("Industry Workspace")

    tab1, tab2, tab3 = st.tabs([
        "Find Researchers",
        "Manage Business & Projects",
        "Find Investors",
    ])

    with tab1:
        _dashboard_metrics([
            ("Company", st.session_state.get("ip2", "-"), st.session_state.get("ip3", "Domain not set")),
            ("Researcher Matches", len(st.session_state.get("industry_researcher_matches", [])), "Loaded candidates"),
            ("Investors", len(st.session_state.get("industry_investors", [])), "Loaded funders"),
            ("Project", st.session_state.get("pr1", "-"), st.session_state.get("pr5", "Risk not set")),
        ])
        st.divider()

        st.subheader("Find Researchers")
        st.caption("Describe your problem to find relevant researchers.")

        default_problem = " ".join([
            st.session_state.get("pr2", ""),
            st.session_state.get("pr3", ""),
            st.session_state.get("pr8", ""),
        ]).strip()
        problem = st.text_area("Problem Statement", value=default_problem, key="ind_problem")

        if st.button("Find Best Matches", key="industry_find_researchers"):
            if not problem.strip():
                st.error("Describe the problem first.")
            else:
                try:
                    with st.spinner("Finding best researcher matches..."):
                        data = _post_json(
                            "/industry/researcher-matches",
                            {
                                "query": problem,
                                "company_domain": st.session_state.get("ip3", ""),
                                "company_country": st.session_state.get("ip4", ""),
                                "n_results": 8
                            },
                        )
                        st.session_state.industry_researcher_matches = data.get("results", [])
                except Exception as exc:
                    st.error(f"Could not find researchers: {exc}")

        matches = st.session_state.get("industry_researcher_matches", [])
        if matches:
            _dashboard_metrics([
                ("Matches", len(matches), "Researchers returned"),
                ("Best Match", _match_score(matches[0].get("distance")), "Top semantic score"),
                ("Patents", sum(int(m.get("patents") or 0) for m in matches), "Across results"),
                ("Countries", len({m.get("country") for m in matches if m.get("country")}), "Represented"),
            ])
            for researcher in matches:
                _show_researcher(researcher)
        else:
            st.info("Run a search to see researcher matches.")

    with tab2:
        _dashboard_metrics([
            ("Employees", st.session_state.get("b7", 0), "Company scale"),
            ("Data Maturity", st.session_state.get("b9", "-"), "Execution readiness"),
            ("Risk", st.session_state.get("pr5", "-"), "Project appetite"),
            ("Public", "Yes" if st.session_state.get("pr_public", True) else "No", "Investor visibility"),
        ])
        st.divider()

        st.subheader("Business Information")
        st.caption("This helps improve matching accuracy.")

        col1, col2 = st.columns(2)

        with col1:
            st.text_input("Company ID", value=st.session_state.get("ip1", ""), key="b1")
            st.text_input("Company Name", value=st.session_state.get("ip2", ""), key="b2")
            st.text_input("Industry Domain", value=st.session_state.get("ip3", ""), key="b3")
            st.number_input("Number of Employees", min_value=0, value=0, key="b7")

        with col2:
            st.text_input("Location", value=st.session_state.get("ip4", ""), key="b4")
            st.text_input("Company Size", value=st.session_state.get("ip5", ""), key="b5")
            st.text_input("Business Model", value=st.session_state.get("ip6", ""), key="b6")
            st.text_input("Annual Turnover", key="b8")

        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Data Infra Maturity", ["Low", "Medium", "High"], key="b9")
        with col2:
            st.text_input("Growth Stage", key="b10")

        if st.button("Save Business Information", key="industry_save_business"):
            user_id = st.session_state.get("user_id")
            if not user_id:
                st.error("Session expired. Please log out and sign in again.")
            else:
                try:
                    save_industry_profile(
                        user_id,
                        (
                            st.session_state.b1,
                            st.session_state.b2,
                            st.session_state.b3,
                            st.session_state.b4,
                            st.session_state.b5,
                            st.session_state.b6,
                        ),
                    )
                    st.session_state.ip1 = st.session_state.b1
                    st.session_state.ip2 = st.session_state.b2
                    st.session_state.ip3 = st.session_state.b3
                    st.session_state.ip4 = st.session_state.b4
                    st.session_state.ip5 = st.session_state.b5
                    st.session_state.ip6 = st.session_state.b6
                    _post_json("/industry/business/save", {
                        "company_id": st.session_state.b1,
                        "company_name": st.session_state.b2,
                        "domain": st.session_state.b3,
                        "location": st.session_state.b4,
                        "employees": int(st.session_state.b7),
                        "size": st.session_state.b5,
                        "model": st.session_state.b6,
                        "turnover": st.session_state.b8,
                        "data_maturity": st.session_state.b9,
                        "growth_stage": st.session_state.b10,
                    })
                    st.success("Business information saved")
                except Exception as exc:
                    st.error(f"Could not save business information: {exc}")

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
            st.selectbox("Collaboration Type", ["Pilot", "Research", "Prototype", "Commercial"], key="pr9")

        st.text_area("Targets / Expected Outcome", key="pr8")
        public = st.toggle("Make Project Public", value=True, key="pr_public")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Add / Update Project", key="industry_save_project"):
                if not st.session_state.pr1 or not st.session_state.pr2:
                    st.error("Project ID and problem statement are required.")
                else:
                    try:
                        _post_json("/industry/project/save", {
                            "project_id": st.session_state.pr1,
                            "company_id": st.session_state.b1,
                            "company_name": st.session_state.b2,
                            "status": "Public" if public else "Draft",
                            "problem": st.session_state.pr2,
                            "budget": st.session_state.pr6,
                            "domains": st.session_state.pr3,
                            "team_size": st.session_state.pr7,
                            "timeline": st.session_state.pr4,
                            "targets": st.session_state.pr8,
                            "risk": st.session_state.pr5,
                            "collaboration_type": st.session_state.pr9,
                            "funded_by": "",
                            "outcome": None,
                            "public": public,
                        })
                        st.success("Project saved")
                    except Exception as exc:
                        st.error(f"Could not save project: {exc}")

        with col2:
            if st.button("Delete Project", type="secondary", key="industry_delete_project"):
                if not st.session_state.pr1:
                    st.error("Enter a project ID to delete.")
                else:
                    try:
                        _post_json("/industry/project/delete", {"project_id": st.session_state.pr1})
                        st.warning("Project deleted")
                    except Exception as exc:
                        st.error(f"Could not delete project: {exc}")

        with col3:
            if st.button("Clear Form", key="industry_clear_project"):
                for key in ["pr1", "pr2", "pr3", "pr4", "pr6", "pr7", "pr8"]:
                    st.session_state[key] = ""
                st.rerun()

    with tab3:
        st.subheader("Public Investors")
        st.caption("Browse investors open to funding projects.")

        investor_query = st.text_input(
            "Search investors by domain, geography, type, or name",
            value=st.session_state.get("b3", ""),
            key="industry_investor_query",
        )

        if st.button("Load Investors", key="industry_load_investors"):
            try:
                data = _post_json(
                    "/industry/investors",
                    {"query": investor_query, "n_results": 20},
                )
                st.session_state.industry_investors = data.get("results", [])
            except Exception as exc:
                st.error(f"Could not load investors: {exc}")

        investors = st.session_state.get("industry_investors", [])
        if investors:
            funded_total = sum(int(i.get("projects_funded") or 0) for i in investors)
            _dashboard_metrics([
                ("Investors", len(investors), "Funders returned"),
                ("Funded Projects", funded_total, "Across returned investors"),
                ("Risk Profiles", len({i.get("risk") for i in investors if i.get("risk")}), "Distinct appetites"),
                ("Regions", len({i.get("geo") for i in investors if i.get("geo")}), "Geographic focus"),
            ])
            for investor in investors:
                _show_investor(investor)
        else:
            st.info("Load investors to see funding matches.")
