import requests
import streamlit as st
from backend.db.profile_repository import save_investor_profile


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


def _percent(value):
    try:
        return f"{round(float(value) * 100)}%"
    except (TypeError, ValueError):
        return "-"


def _show_project(project):
    with st.container(border=True):
        st.markdown(f"**{project.get('project_id', '')} - {project.get('company_name', '')}**")
        st.markdown(
            f"""
            <span class="result-pill">Match {_match_score(project.get("distance"))}</span>
            <span class="result-pill">{project.get("status") or "Status -"}</span>
            <span class="result-pill">{project.get("risk") or "Risk -"}</span>
            """,
            unsafe_allow_html=True,
        )
        st.write(_shorten(project.get("problem")))
        _dashboard_metrics([
            ("Budget", project.get("budget"), "Capital need"),
            ("Timeline", project.get("timeline"), "Expected duration"),
            ("Team", project.get("team_size"), "Delivery capacity"),
            ("Mode", project.get("collaboration_type"), "Engagement type"),
        ])
        if project.get("domain"):
            st.caption(_shorten(project.get("domain"), 220))
        if project.get("targets"):
            st.caption(_shorten(project.get("targets"), 260))


def investor_page():
    st.title("Investor Workspace")

    tab1, tab2, tab3 = st.tabs([
        "Investor Profile",
        "Find Projects",
        "Portfolio",
    ])

    with tab1:
        _dashboard_metrics([
            ("Budget", st.session_state.get("iv7", "-"), "Capital allocation"),
            ("Risk", st.session_state.get("iv4", st.session_state.get("invp4", "-")), "Investment appetite"),
            ("Funded", st.session_state.get("iv10", 0), "Projects backed"),
            ("Success", _percent(st.session_state.get("iv9", 0)), "Portfolio rate"),
        ])
        st.divider()

        st.subheader("Investor Profile")
        st.caption("Define your investment interests and funding preferences.")

        col1, col2 = st.columns(2)

        with col1:
            st.text_input("Investor ID", value=st.session_state.get("invp1", ""), key="iv1")
            st.text_input("Name", value=st.session_state.get("invp2", ""), key="iv2")
            st.text_input("Domains of Interest", value=st.session_state.get("invp3", ""), key="iv3")
            st.text_input("Budget", key="iv7")

        with col2:
            st.selectbox("Risk Appetite", ["Low", "Medium", "High"], key="iv4")
            st.text_input("Geographic Focus", value=st.session_state.get("invp5", ""), key="iv5")
            st.text_input("Investor Type", key="iv8")
            st.number_input("Portfolio Success Rate", min_value=0.0, max_value=1.0, value=0.0, key="iv9")

        st.text_area("Previous Investments", value=st.session_state.get("invp6", ""), key="iv6")
        st.number_input("Number of Projects Funded", min_value=0, value=0, key="iv10")

        if st.button("Save Investor Profile", key="investor_save_profile"):
            user_id = st.session_state.get("user_id")
            if not user_id:
                st.error("Session expired. Please log out and sign in again.")
            else:
                try:
                    save_investor_profile(
                        user_id,
                        (
                            st.session_state.iv1,
                            st.session_state.iv2,
                            st.session_state.iv3,
                            st.session_state.iv4,
                            st.session_state.iv5,
                            st.session_state.iv6,
                        ),
                    )
                    st.session_state.invp1 = st.session_state.iv1
                    st.session_state.invp2 = st.session_state.iv2
                    st.session_state.invp3 = st.session_state.iv3
                    st.session_state.invp4 = st.session_state.iv4
                    st.session_state.invp5 = st.session_state.iv5
                    st.session_state.invp6 = st.session_state.iv6
                    _post_json("/investor/profile/save", {
                        "investor_id": st.session_state.iv1,
                        "name": st.session_state.iv2,
                        "domains": st.session_state.iv3,
                        "risk": st.session_state.iv4,
                        "geo": st.session_state.iv5,
                        "previous_projects": st.session_state.iv6,
                        "budget": st.session_state.iv7,
                        "investor_type": st.session_state.iv8,
                        "success_rate": float(st.session_state.iv9),
                        "projects_funded": int(st.session_state.iv10),
                    })
                    st.success("Investor profile saved")
                except Exception as exc:
                    st.error(f"Could not save investor profile: {exc}")

    with tab2:
        _dashboard_metrics([
            ("Opportunities", len(st.session_state.get("investor_project_matches", [])), "Projects loaded"),
            ("Risk Target", st.session_state.get("iv4", st.session_state.get("invp4", "-")), "Preferred risk"),
            ("Focus", st.session_state.get("iv5", st.session_state.get("invp5", "-")), "Geography"),
            ("Domains", _shorten(st.session_state.get("iv3", st.session_state.get("invp3", "-")), 32), "Investment thesis"),
        ])
        st.divider()

        st.subheader("Find Projects to Fund")
        st.caption("Search for projects that match your investment interests.")

        default_query = " ".join([
            st.session_state.get("iv3", ""),
            st.session_state.get("iv4", ""),
            st.session_state.get("iv5", ""),
        ]).strip()
        query = st.text_input(
            "Search by domain, problem, geography, or keyword",
            value=default_query,
            key="investor_project_query",
        )

        if st.button("Find Opportunities", key="investor_find_projects"):
            if not query.strip():
                st.error("Enter a project search query.")
            else:
                try:
                    data = _post_json(
                        "/investor/projects/search",
                        {"query": query, "n_results": 10},
                    )
                    st.session_state.investor_project_matches = data.get("results", [])
                except Exception as exc:
                    st.error(f"Could not find projects: {exc}")

        projects = st.session_state.get("investor_project_matches", [])
        if projects:
            _dashboard_metrics([
                ("Projects", len(projects), "Opportunities returned"),
                ("Best Match", _match_score(projects[0].get("distance")), "Top semantic score"),
                ("Budgets", len([p for p in projects if p.get("budget")]), "With budget data"),
                ("Risks", len({p.get("risk") for p in projects if p.get("risk")}), "Distinct appetites"),
            ])
            for project in projects:
                _show_project(project)
        else:
            st.info("Run a search to see investable projects.")

    with tab3:
        portfolio = st.session_state.get("investor_portfolio", [])
        _dashboard_metrics([
            ("Portfolio", len(portfolio), "Linked projects"),
            ("Active", len([p for p in portfolio if "progress" in str(p.get("status", "")).lower()]), "In progress"),
            ("Domains", len({p.get("domain") for p in portfolio if p.get("domain")}), "Represented"),
            ("Capital", len([p for p in portfolio if p.get("budget")]), "Budgeted projects"),
        ])
        st.divider()

        st.subheader("Portfolio")
        st.caption("Projects currently linked to your investor ID.")

        investor_id = st.text_input(
            "Investor ID",
            value=st.session_state.get("iv1") or st.session_state.get("invp1", ""),
            key="portfolio_investor_id",
        )

        if st.button("Load Portfolio", key="investor_load_portfolio"):
            if not investor_id.strip():
                st.error("Enter your investor ID.")
            else:
                try:
                    data = _post_json(
                        "/investor/portfolio",
                        {"investor_id": investor_id},
                    )
                    st.session_state.investor_portfolio = data.get("results", [])
                except Exception as exc:
                    st.error(f"Could not load portfolio: {exc}")

        if portfolio:
            for project in portfolio:
                _show_project(project)
        else:
            st.info("Load your portfolio to see funded projects.")
