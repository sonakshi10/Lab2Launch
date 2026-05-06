import sqlite3
import pandas as pd
from config import SQLITE_DB_PATH, CHROMA_PAPERS
from config import CHROMA_INVESTORS
from services.embeddings import load_embedding_model, get_chroma_client, get_collection

def find_researchers_for_project(
    project_description,
    preferred_country="",
    preferred_domain="",
    preferred_language="English",
    min_experience_years=None
):

    conn = sqlite3.connect(SQLITE_DB_PATH)

    # ---------------- FILTERING ----------------
    conditions = []

    if preferred_country:
        conditions.append(f"\"Affiliated country\" = '{preferred_country}'")

    if preferred_domain:
        conditions.append(f"\"Domain\" LIKE '%{preferred_domain}%'")

    if preferred_language:
        conditions.append(f"\"Primary language\" LIKE '%{preferred_language}%'")

    if min_experience_years:
        conditions.append(f"\"Years of experience\" >= {min_experience_years}")

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    researchers = pd.read_sql(f"""
        SELECT * FROM researcher_attributes
        {where_clause}
    """, conn)

    papers = pd.read_sql("SELECT * FROM paper_attributes", conn)
    conn.close()

    # ---------------- EMBEDDINGS ----------------
    model = load_embedding_model()
    client = get_chroma_client(CHROMA_PAPERS)
    collection = get_collection(client, "paper_embeddings")

    project_embedding = model.encode(project_description).tolist()

    results = collection.query(
        query_embeddings=[project_embedding],
        n_results=10,
        include=["documents", "distances", "metadatas"]
    )

    return results


def _rows_by_id(table_name, id_column, ids):
    if not ids:
        return {}

    placeholders = ",".join(["?"] * len(ids))
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        f'SELECT * FROM "{table_name}" WHERE "{id_column}" IN ({placeholders})',
        ids,
    ).fetchall()
    conn.close()
    return {str(row[id_column]): dict(row) for row in rows}


def _project_text(project):
    return "\n".join([
        f"Problem tackled: {project.get('problem', '')}",
        f"Domain(s): {project.get('domains', '')}",
        f"Targets: {project.get('targets', '')}",
        f"Company name: {project.get('company_name', '')}",
        f"Current status: {project.get('status', '')}",
    ])


def find_researcher_matches(project_description, n_results=10):
    model = load_embedding_model()
    collection = get_collection(get_chroma_client(CHROMA_PAPERS), "paper_embeddings")
    embedding = model.encode(project_description).tolist()
    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results,
        include=["documents", "distances", "metadatas"],
    )

    paper_ids = [str(item) for item in results.get("ids", [[]])[0]]
    distances = results.get("distances", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    paper_rows = _rows_by_id("paper_attributes", "Paper ID", paper_ids)

    researcher_ids = []
    for metadata in metadatas:
        researcher_id = str(metadata.get("researcher_id", ""))
        if researcher_id and researcher_id not in researcher_ids:
            researcher_ids.append(researcher_id)

    researcher_rows = _rows_by_id("researcher_attributes", "Researcher ID", researcher_ids)

    matches = []
    seen = set()
    for index, metadata in enumerate(metadatas):
        researcher_id = str(metadata.get("researcher_id", ""))
        if not researcher_id or researcher_id in seen:
            continue

        seen.add(researcher_id)
        paper_id = paper_ids[index] if index < len(paper_ids) else ""
        paper = paper_rows.get(paper_id, {})
        researcher = researcher_rows.get(researcher_id, {})
        matches.append({
            "researcher_id": researcher_id,
            "name": researcher.get("Name", ""),
            "affiliation": researcher.get("Affiliation", ""),
            "country": researcher.get("Affiliated country", ""),
            "language": researcher.get("Primary language", ""),
            "h_index": researcher.get("h index", ""),
            "i10_index": researcher.get("i-10 index", ""),
            "patents": researcher.get("Number of patents", ""),
            "grants": researcher.get("Number of grants", ""),
            "matching_paper_id": paper_id,
            "matching_paper_title": paper.get("Name / Title") or metadata.get("paper_title", ""),
            "keywords": paper.get("Keywords", ""),
            "summary": paper.get("Summary") or paper.get("Abstract", ""),
            "distance": distances[index] if index < len(distances) else None,
        })

    return {"status": "success", "results": matches}


def save_business(business):
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.execute(
        """
        INSERT OR REPLACE INTO business_attributes (
            "Company ID",
            "Company name",
            "Industry / Domain",
            "Location",
            "Number of employees",
            "Company Size",
            "Business Model",
            "Data infra maturity",
            "Annual turnover",
            "Growth Stage"
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            business.get("company_id", ""),
            business.get("company_name", ""),
            business.get("domain", ""),
            business.get("location", ""),
            business.get("employees", 0),
            business.get("size", ""),
            business.get("model", ""),
            business.get("data_maturity", ""),
            business.get("turnover", ""),
            business.get("growth_stage", ""),
        ),
    )
    conn.commit()
    conn.close()
    return {"status": "success", "company_id": business.get("company_id", "")}


def save_project(project):
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.execute(
        """
        INSERT OR REPLACE INTO project_attributes (
            "Project ID",
            "Company ID",
            "Company name",
            "Current status",
            "Problem tackled",
            "Budget",
            "Domain(s)",
            "Team size",
            "Timeline",
            "Targets",
            "Risk appetite",
            "Preferred collaboration type",
            "Funded by (Investor ID)",
            "Project Outcome"
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            project.get("project_id", ""),
            project.get("company_id", ""),
            project.get("company_name", ""),
            project.get("status", "Draft"),
            project.get("problem", ""),
            project.get("budget", ""),
            project.get("domains", ""),
            project.get("team_size", ""),
            project.get("timeline", ""),
            project.get("targets", ""),
            project.get("risk", ""),
            project.get("collaboration_type", ""),
            project.get("funded_by", ""),
            project.get("outcome"),
        ),
    )
    conn.commit()
    conn.close()

    if project.get("public", True):
        _upsert_project_embedding(project)

    return {"status": "success", "project_id": project.get("project_id", "")}


def delete_project(project_id):
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.execute('DELETE FROM project_attributes WHERE "Project ID"=?', (project_id,))
    conn.commit()
    conn.close()

    collection = get_collection(get_chroma_client(CHROMA_INVESTORS), "investor_business_project_summaries_e5")
    try:
        collection.delete(ids=[project_id])
    except Exception:
        pass

    return {"status": "success", "project_id": project_id}


def list_investors(query="", n_results=20):
    terms = [term.strip() for term in query.split() if term.strip()]
    conditions = []
    params = []
    for term in terms:
        like = f"%{term}%"
        conditions.append(
            '("Name" LIKE ? OR "Domains of interest" LIKE ? OR "Investor Type" LIKE ? OR "Geographic Focus" LIKE ?)'
        )
        params.extend([like, like, like, like])

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        f'SELECT * FROM investor_attributes{where_clause} LIMIT ?',
        (*params, n_results),
    ).fetchall()
    conn.close()

    investors = []
    for row in rows:
        item = dict(row)
        investors.append({
            "investor_id": item.get("Investor ID", ""),
            "name": item.get("Name", ""),
            "budget": item.get("Budget", ""),
            "domains": item.get("Domains of interest", ""),
            "projects_funded": item.get("Number of projects funded", ""),
            "previous_projects": item.get("Previous projects", ""),
            "investor_type": item.get("Investor Type", ""),
            "risk": item.get("Risk Appetite", ""),
            "geo": item.get("Geographic Focus", ""),
            "success_rate": item.get("Portfolio Success Rate", ""),
        })

    return {"status": "success", "results": investors}


def _upsert_project_embedding(project):
    model = load_embedding_model()
    project_id = str(project.get("project_id", ""))
    text = "passage: " + _project_text(project)
    collection = get_collection(get_chroma_client(CHROMA_INVESTORS), "investor_business_project_summaries_e5")
    collection.upsert(
        ids=[project_id],
        documents=[text],
        embeddings=[model.encode(text).tolist()],
        metadatas=[{
            "company_name": project.get("company_name", ""),
            "domain": project.get("domains", ""),
            "risk": project.get("risk", ""),
        }],
    )
