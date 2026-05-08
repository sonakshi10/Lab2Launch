"""
Frontend components for displaying recommendation metrics across different personas.
These components work with Streamlit to show metric cards and visualizations.
"""

import streamlit as st
from typing import Dict, List, Any, Optional


# ============================================================
# Metric Card Components
# ============================================================

def metric_card(label: str, value: Any, note: str = "", width_percent: int = None):
    """
    Render a single metric card with label, value, and optional note.
    """
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


def metric_row(items: List[tuple]):
    """
    Display multiple metrics in a row (auto columns).
    items: list of (label, value, note) tuples
    """
    cols = st.columns(len(items))
    for col, (label, value, note) in zip(cols, items):
        with col:
            metric_card(label, value, note)


def metric_gauge(label: str, value: float, note: str = ""):
    """
    Display a metric as a gauge/slider (0-100 scale).
    """
    value = float(value) if value else 0
    cols = st.columns([1, 2])
    
    with cols[0]:
        st.markdown(
            f"""
            <div class="dash-card">
                <div class="dash-label">{label}</div>
                <div class="dash-value">{round(value)}%</div>
                <div class="dash-note">{note}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    with cols[1]:
        # Visual gauge
        st.progress(min(value / 100.0, 1.0))


# ============================================================
# Metric Display Templates
# ============================================================

def show_researcher_metrics(metrics: Dict[str, float]):
    """
    Display metrics for Researcher → Company recommendations.
    """
    if not metrics:
        return
    
    st.subheader("Match Metrics", divider="gray")
    
    # Overall score prominently
    cols = st.columns(7)
    with cols[0]:
        st.markdown(
            f"""
            <div class="dash-card" style="background: linear-gradient(135deg, #0f6b57 0%, #0a4e3f 100%); color: white;">
                <div class="dash-label" style="color: rgba(255,255,255,0.8);">Overall Score</div>
                <div class="dash-value" style="font-size: 2rem;">{round(metrics.get('overall_score', 0))}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    # Individual metrics
    metric_items = [
        ("Domain Fit", f"{round(metrics.get('domain_fit', 0))}%", "Industry alignment"),
        ("Research Strength", f"{round(metrics.get('research_strength', 0))}%", "H-index & grants"),
        ("Commercialization", f"{round(metrics.get('commercialization_fit', 0))}%", "IP potential"),
        ("Collaboration", f"{round(metrics.get('collaboration_fit', 0))}%", "Work style match"),
        ("Geography", f"{round(metrics.get('geography_fit', 0))}%", "Location fit"),
        ("Text Match", f"{round(metrics.get('text_fit', 0))}%", "Semantic relevance"),
    ]
    
    cols = st.columns(6)
    for col, (label, value, note) in zip(cols, metric_items):
        with col:
            metric_card(label, value, note)


def show_industry_metrics(metrics: Dict[str, float]):
    """
    Display metrics for Company → Researcher recommendations.
    """
    if not metrics:
        return
    
    st.subheader("Match Metrics", divider="gray")
    
    # Overall score prominently
    cols = st.columns(6)
    with cols[0]:
        st.markdown(
            f"""
            <div class="dash-card" style="background: linear-gradient(135deg, #0f6b57 0%, #0a4e3f 100%); color: white;">
                <div class="dash-label" style="color: rgba(255,255,255,0.8);">Overall Score</div>
                <div class="dash-value" style="font-size: 2rem;">{round(metrics.get('overall_score', 0))}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    # Individual metrics
    metric_items = [
        ("Domain Fit", f"{round(metrics.get('domain_fit', 0))}%", "Research domain match"),
        ("Text Match", f"{round(metrics.get('text_fit', 0))}%", "Semantic similarity"),
        ("Research Strength", f"{round(metrics.get('research_strength', 0))}%", "Scholar quality"),
        ("Commercialization", f"{round(metrics.get('commercialization_fit', 0))}%", "IP & patents"),
        ("Collaboration", f"{round(metrics.get('collaboration_fit', 0))}%", "Engagement fit"),
        ("Geography", f"{round(metrics.get('geography_fit', 0))}%", "Location proximity"),
    ]
    
    cols = st.columns(6)
    for col, (label, value, note) in zip(cols, metric_items):
        with col:
            metric_card(label, value, note)


def show_investor_metrics(metrics: Dict[str, float]):
    """
    Display metrics for Investor → Project recommendations.
    """
    if not metrics:
        return
    
    st.subheader("Investment Fit Analysis", divider="gray")
    
    # Overall score prominently
    cols = st.columns(4)
    with cols[0]:
        st.markdown(
            f"""
            <div class="dash-card" style="background: linear-gradient(135deg, #0f6b57 0%, #0a4e3f 100%); color: white;">
                <div class="dash-label" style="color: rgba(255,255,255,0.8);">Investment Score</div>
                <div class="dash-value" style="font-size: 2rem;">{round(metrics.get('overall_score', 0))}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    # Primary metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Strategic Fit**", help="How well the investment aligns with your profile")
        metric_items = [
            ("Domain Fit", f"{round(metrics.get('domain_fit', 0))}%", "Investment focus"),
            ("Risk Alignment", f"{round(metrics.get('risk_fit', 0))}%", "Risk appetite match"),
            ("Geography", f"{round(metrics.get('geography_fit', 0))}%", "Geographic preference"),
        ]
        for label, value, note in metric_items:
            metric_card(label, value, note)
    
    with col2:
        st.markdown("**Financial & Commercial**", help="Project viability and potential returns")
        metric_items = [
            ("Budget Fit", f"{round(metrics.get('budget_fit', 0))}%", "Capital alignment"),
            ("Project Maturity", f"{round(metrics.get('project_maturity', 0))}%", "Development stage"),
            ("Commercial Potential", f"{round(metrics.get('commercial_potential', 0))}%", "Revenue outlook"),
        ]
        for label, value, note in metric_items:
            metric_card(label, value, note)
    
    # Company readiness as a separate section
    st.markdown("**Execution Capability**", help="Can the company deliver?")
    metric_card("Company Readiness", f"{round(metrics.get('company_readiness', 0))}%", "Operational maturity")


def show_metrics_summary(metrics: Dict[str, float], metric_type: str = "researcher"):
    """
    Display a compact summary of metrics for use in lists/tables.
    """
    if not metrics:
        return ""
    
    overall = round(metrics.get('overall_score', 0))
    
    if metric_type == "investor":
        domain = round(metrics.get('domain_fit', 0))
        budget = round(metrics.get('budget_fit', 0))
        return f"Overall: {overall}% | Domain: {domain}% | Budget: {budget}%"
    elif metric_type == "industry":
        domain = round(metrics.get('domain_fit', 0))
        research = round(metrics.get('research_strength', 0))
        return f"Overall: {overall}% | Domain: {domain}% | Research: {research}%"
    else:  # researcher
        domain = round(metrics.get('domain_fit', 0))
        research = round(metrics.get('research_strength', 0))
        return f"Overall: {overall}% | Domain: {domain}% | Research: {research}%"


def display_metrics_breakdown(metrics: Dict[str, float]):
    """
    Display detailed metrics breakdown in expandable sections.
    """
    with st.expander("📊 Detailed Metrics Breakdown"):
        # Create a table-like display
        metric_data = []
        for key, value in metrics.items():
            if key != "overall_score":
                # Convert snake_case to Title Case
                label = key.replace("_", " ").title()
                metric_data.append({
                    "Metric": label,
                    "Score": f"{round(float(value))}%",
                })
        
        if metric_data:
            st.dataframe(metric_data, use_container_width=True, hide_index=True)


def get_metric_color(score: float) -> str:
    """
    Return a color code based on metric score (0-100).
    Used for highlighting high/low scores.
    """
    score = float(score) if score else 0
    if score >= 75:
        return "#22c55e"  # Green - Excellent
    elif score >= 50:
        return "#eab308"  # Yellow - Good
    elif score >= 25:
        return "#f97316"  # Orange - Fair
    else:
        return "#ef4444"  # Red - Poor


def score_badge(score: float, show_percentage: bool = True):
    """
    Display a score as a colored badge.
    """
    score = float(score) if score else 0
    color = get_metric_color(score)
    score_str = f"{round(score)}%" if show_percentage else f"{round(score)}"
    
    st.markdown(
        f"""
        <span style="
            display: inline-block;
            background-color: {color};
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 0.9em;
        ">{score_str}</span>
        """,
        unsafe_allow_html=True,
    )
