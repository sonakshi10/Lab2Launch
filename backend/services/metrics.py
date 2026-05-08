"""
Metrics module for computing and returning recommendation quality scores.
Supports different metric types for different personas (Researcher, Industry, Investor).
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


# ============================================================
# Data Models
# ============================================================

@dataclass
class ResearcherMetrics:
    """Metrics for Researcher → Company/Project recommendations"""
    domain_fit: float  # 0-100: how well domain matches
    research_strength: float  # 0-100: researcher quality/impact
    commercialization_fit: float  # 0-100: project commercialization alignment
    collaboration_fit: float  # 0-100: collaboration type match
    geography_fit: float  # 0-100: geographic alignment
    text_fit: float  # 0-100: semantic similarity
    overall_score: float  # 0-100: weighted average
    
    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


@dataclass
class IndustryMetrics:
    """Metrics for Industry/Company → Researcher recommendations"""
    domain_fit: float  # 0-100: domain overlap
    text_fit: float  # 0-100: semantic similarity
    research_strength: float  # 0-100: researcher impact
    commercialization_fit: float  # 0-100: commercialization potential
    collaboration_fit: float  # 0-100: collaboration readiness
    geography_fit: float  # 0-100: geographic proximity
    overall_score: float  # 0-100: weighted average
    
    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


@dataclass
class InvestorMetrics:
    """Metrics for Investor → Project recommendations"""
    domain_fit: float  # 0-100: investment domain focus
    budget_fit: float  # 0-100: budget alignment
    risk_fit: float  # 0-100: risk appetite alignment
    project_maturity: float  # 0-100: project readiness
    company_readiness: float  # 0-100: company execution capability
    commercial_potential: float  # 0-100: revenue/exit potential
    geography_fit: float  # 0-100: geographic preference alignment
    overall_score: float  # 0-100: weighted average
    
    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


# ============================================================
# Metric Weights (can be tuned for different strategies)
# ============================================================

RESEARCHER_WEIGHTS = {
    "domain_fit": 0.25,
    "research_strength": 0.20,
    "commercialization_fit": 0.20,
    "collaboration_fit": 0.15,
    "geography_fit": 0.10,
    "text_fit": 0.10,
}

INDUSTRY_WEIGHTS = {
    "domain_fit": 0.25,
    "text_fit": 0.25,
    "research_strength": 0.20,
    "commercialization_fit": 0.15,
    "collaboration_fit": 0.10,
    "geography_fit": 0.05,
}

INVESTOR_WEIGHTS = {
    "domain_fit": 0.20,
    "budget_fit": 0.20,
    "risk_fit": 0.15,
    "project_maturity": 0.15,
    "company_readiness": 0.10,
    "commercial_potential": 0.15,
    "geography_fit": 0.05,
}


# ============================================================
# Metric Calculation Functions
# ============================================================

def normalize_score(value: Optional[float], min_val: float = 0.0, max_val: float = 100.0) -> float:
    """
    Normalize a score to 0-100 range.
    """
    if value is None:
        return 40.0  # neutral default
    try:
        val = float(value)
        return max(min_val, min(max_val, val))
    except (TypeError, ValueError):
        return 40.0


def distance_to_fit(distance: Optional[float], max_distance: float = 2.0) -> float:
    """
    Convert embedding distance to fit score (0-100).
    Lower distance = higher fit.
    """
    if distance is None:
        return 40.0
    try:
        dist = float(distance)
        # Invert: closer = higher score
        score = 100 * (1 - min(dist / max_distance, 1.0))
        return max(0.0, min(100.0, score))
    except (TypeError, ValueError):
        return 40.0


def calculate_researcher_metrics(
    distance: Optional[float],
    researcher_h_index: Optional[float],
    researcher_i10_index: Optional[float],
    researcher_grants: Optional[float],
    project_domain: str,
    researcher_domain: str,
    project_country: str,
    researcher_country: str,
    collaboration_match: float = 0.5,
) -> ResearcherMetrics:
    """
    Calculate metrics for researcher → project recommendation.
    """
    # Semantic match from distance
    text_fit = distance_to_fit(distance, max_distance=2.0)
    
    # Research strength from h-index and grants
    h_index_norm = normalize_score(researcher_h_index, 0, 100)
    grants_norm = normalize_score(researcher_grants, 0, 100)
    research_strength = (h_index_norm * 0.6 + grants_norm * 0.4)
    
    # Domain fit (simplified)
    domain_fit = 80.0 if project_domain.lower() in researcher_domain.lower() else 50.0
    
    # Geography fit
    geography_fit = 100.0 if project_country.lower() == researcher_country.lower() else 70.0
    
    # Commercialization fit (placeholder)
    commercialization_fit = normalize_score(65.0, 0, 100)
    
    # Collaboration fit
    collaboration_fit = normalize_score(collaboration_match * 100, 0, 100)
    
    # Calculate weighted overall score
    weights = RESEARCHER_WEIGHTS
    overall_score = (
        domain_fit * weights["domain_fit"] +
        research_strength * weights["research_strength"] +
        commercialization_fit * weights["commercialization_fit"] +
        collaboration_fit * weights["collaboration_fit"] +
        geography_fit * weights["geography_fit"] +
        text_fit * weights["text_fit"]
    )
    
    return ResearcherMetrics(
        domain_fit=round(domain_fit, 2),
        research_strength=round(research_strength, 2),
        commercialization_fit=round(commercialization_fit, 2),
        collaboration_fit=round(collaboration_fit, 2),
        geography_fit=round(geography_fit, 2),
        text_fit=round(text_fit, 2),
        overall_score=round(overall_score, 2),
    )


def calculate_industry_metrics(
    distance: Optional[float],
    researcher_h_index: Optional[float],
    researcher_patents: Optional[float],
    researcher_grants: Optional[float],
    company_domain: str,
    researcher_domain: str,
    company_country: str,
    researcher_country: str,
    project_status: str = "in-progress",
) -> IndustryMetrics:
    """
    Calculate metrics for company → researcher recommendation.
    """
    # Semantic match
    text_fit = distance_to_fit(distance, max_distance=2.0)
    
    # Research strength from h-index, patents, grants
    h_index_norm = normalize_score(researcher_h_index, 0, 100)
    patents_norm = normalize_score(researcher_patents, 0, 100)
    grants_norm = normalize_score(researcher_grants, 0, 100)
    research_strength = (h_index_norm * 0.5 + patents_norm * 0.25 + grants_norm * 0.25)
    
    # Domain fit
    domain_fit = 85.0 if company_domain.lower() in researcher_domain.lower() else 55.0
    
    # Geography fit
    geography_fit = 100.0 if company_country.lower() == researcher_country.lower() else 75.0
    
    # Commercialization fit (based on researcher having patents)
    commercialization_fit = 80.0 if researcher_patents and int(researcher_patents) > 0 else 50.0
    
    # Collaboration fit (simplified)
    collaboration_fit = normalize_score(65.0, 0, 100)
    
    # Calculate weighted overall score
    weights = INDUSTRY_WEIGHTS
    overall_score = (
        domain_fit * weights["domain_fit"] +
        text_fit * weights["text_fit"] +
        research_strength * weights["research_strength"] +
        commercialization_fit * weights["commercialization_fit"] +
        collaboration_fit * weights["collaboration_fit"] +
        geography_fit * weights["geography_fit"]
    )
    
    return IndustryMetrics(
        domain_fit=round(domain_fit, 2),
        text_fit=round(text_fit, 2),
        research_strength=round(research_strength, 2),
        commercialization_fit=round(commercialization_fit, 2),
        collaboration_fit=round(collaboration_fit, 2),
        geography_fit=round(geography_fit, 2),
        overall_score=round(overall_score, 2),
    )


def calculate_investor_metrics(
    distance: Optional[float],
    project_budget: Optional[float],
    investor_budget: Optional[float],
    project_risk: str,
    investor_risk: str,
    project_domain: str,
    investor_domain: str,
    project_country: str,
    investor_country: str,
    project_stage: str = "early-stage",
    company_maturity: str = "startup",
) -> InvestorMetrics:
    """
    Calculate metrics for investor → project recommendation.
    """
    # Semantic match from distance
    domain_fit = distance_to_fit(distance, max_distance=2.0)
    
    # Budget fit - project budget vs investor budget
    budget_fit = 50.0  # Default neutral
    if investor_budget and investor_budget > 0:
        try:
            proj_budget = float(project_budget) if project_budget else 0
            inv_budget = float(investor_budget)
            ratio = proj_budget / inv_budget if inv_budget > 0 else 0
            if 0.05 <= ratio <= 0.50:
                budget_fit = 100.0
            elif 0.01 <= ratio <= 0.75:
                budget_fit = 80.0
            elif ratio > 0.75:
                budget_fit = 60.0
            else:
                budget_fit = 40.0
        except (TypeError, ValueError):
            pass
    
    # Risk fit - project risk vs investor risk appetite
    risk_fit = 50.0
    risk_map = {
        ("Low", "Low"): 100,
        ("Low", "Medium"): 70,
        ("Low", "High"): 40,
        ("Medium", "Low"): 70,
        ("Medium", "Medium"): 100,
        ("Medium", "High"): 80,
        ("High", "Low"): 40,
        ("High", "Medium"): 80,
        ("High", "High"): 100,
    }
    risk_key = (project_risk, investor_risk)
    risk_fit = float(risk_map.get(risk_key, 50.0))
    
    # Project maturity based on stage
    stage_scores = {
        "seed": 40,
        "early-stage": 60,
        "growth": 75,
        "expansion": 85,
        "mature": 100,
    }
    project_maturity = float(stage_scores.get(project_stage.lower(), 50.0))
    
    # Company readiness
    company_readiness = 50.0
    readiness_map = {
        "startup": 50,
        "early": 60,
        "growth": 75,
        "established": 90,
        "enterprise": 100,
    }
    company_readiness = float(readiness_map.get(company_maturity.lower(), 50.0))
    
    # Commercial potential (placeholder)
    commercial_potential = normalize_score(70.0, 0, 100)
    
    # Geography fit
    geography_fit = 100.0 if project_country.lower() == investor_country.lower() else 70.0
    
    # Domain match
    domain_fit_adj = 80.0 if project_domain.lower() in investor_domain.lower() else 50.0
    
    # Calculate weighted overall score
    weights = INVESTOR_WEIGHTS
    overall_score = (
        domain_fit_adj * weights["domain_fit"] +
        budget_fit * weights["budget_fit"] +
        risk_fit * weights["risk_fit"] +
        project_maturity * weights["project_maturity"] +
        company_readiness * weights["company_readiness"] +
        commercial_potential * weights["commercial_potential"] +
        geography_fit * weights["geography_fit"]
    )
    
    return InvestorMetrics(
        domain_fit=round(domain_fit_adj, 2),
        budget_fit=round(budget_fit, 2),
        risk_fit=round(risk_fit, 2),
        project_maturity=round(project_maturity, 2),
        company_readiness=round(company_readiness, 2),
        commercial_potential=round(commercial_potential, 2),
        geography_fit=round(geography_fit, 2),
        overall_score=round(overall_score, 2),
    )


def add_metrics_to_results(
    results: List[Dict[str, Any]],
    metrics_list: List[dict],
) -> List[Dict[str, Any]]:
    """
    Attach metrics to recommendation results.
    """
    for result, metrics in zip(results, metrics_list):
        result["metrics"] = metrics
    return results
