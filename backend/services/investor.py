import sqlite3
import pandas as pd
from config import SQLITE_DB_PATH, CHROMA_INVESTORS
from services.embeddings import load_embedding_model, get_chroma_client, get_collection

def find_projects_for_investor(
    investor_query,
    preferred_domain="",
    preferred_stage="",
    preferred_risk="",
):

    conn = sqlite3.connect(SQLITE_DB_PATH)

    # ---------------- FILTERING ----------------
    conditions = []

    if preferred_domain:
        conditions.append(f"\"Domain(s)\" LIKE '%{preferred_domain}%'")

    if preferred_stage:
        conditions.append(f"\"Preferred collaboration type\" LIKE '%{preferred_stage}%'")

    if preferred_risk:
        conditions.append(f"\"Risk appetite\" LIKE '%{preferred_risk}%'")

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    projects = pd.read_sql(f"""
        SELECT * FROM project_attributes
        {where_clause}
    """, conn)

    conn.close()

    # ---------------- EMBEDDINGS ----------------
    model = load_embedding_model()
    client = get_chroma_client(CHROMA_INVESTORS)
    collection = get_collection(client, "investor_business_project_summaries_e5")

    query_embedding = model.encode("query: " + investor_query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
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


def find_project_matches(query, n_results=10):
    model = load_embedding_model()
    collection = get_collection(get_chroma_client(CHROMA_INVESTORS), "investor_business_project_summaries_e5")
    embedding = model.encode("query: " + query).tolist()
    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results,
        include=["documents", "distances", "metadatas"],
    )

    ids = [str(item) for item in results.get("ids", [[]])[0]]
    rows = _rows_by_id("project_attributes", "Project ID", ids)
    distances = results.get("distances", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    projects = []
    for index, project_id in enumerate(ids):
        row = rows.get(project_id, {})
        projects.append({
            "project_id": project_id,
            "company_id": row.get("Company ID", ""),
            "company_name": row.get("Company name") or metadatas[index].get("company_name", ""),
            "status": row.get("Current status", ""),
            "problem": row.get("Problem tackled") or documents[index],
            "budget": row.get("Budget", ""),
            "domain": row.get("Domain(s)") or metadatas[index].get("domain", ""),
            "team_size": row.get("Team size", ""),
            "timeline": row.get("Timeline", ""),
            "targets": row.get("Targets", ""),
            "risk": row.get("Risk appetite") or metadatas[index].get("risk", ""),
            "collaboration_type": row.get("Preferred collaboration type", ""),
            "funded_by": row.get("Funded by (Investor ID)", ""),
            "distance": distances[index] if index < len(distances) else None,
        })

    return {"status": "success", "results": projects}


def save_investor_record(investor):
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.execute(
        """
        INSERT OR REPLACE INTO investor_attributes (
            "Investor ID",
            "Name",
            "Budget",
            "Domains of interest",
            "Number of projects funded",
            "Previous projects",
            "Investor Type",
            "Risk Appetite",
            "Geographic Focus",
            "Portfolio Success Rate"
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            investor.get("investor_id", ""),
            investor.get("name", ""),
            investor.get("budget", ""),
            investor.get("domains", ""),
            investor.get("projects_funded", 0),
            investor.get("previous_projects", ""),
            investor.get("investor_type", ""),
            investor.get("risk", ""),
            investor.get("geo", ""),
            investor.get("success_rate", 0),
        ),
    )
    conn.commit()
    conn.close()
    return {"status": "success", "investor_id": investor.get("investor_id", "")}


def investor_portfolio(investor_id):
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        'SELECT * FROM project_attributes WHERE "Funded by (Investor ID)"=?',
        (investor_id,),
    ).fetchall()
    conn.close()

    projects = []
    for row in rows:
        item = dict(row)
        projects.append({
            "project_id": item.get("Project ID", ""),
            "company_name": item.get("Company name", ""),
            "status": item.get("Current status", ""),
            "problem": item.get("Problem tackled", ""),
            "budget": item.get("Budget", ""),
            "domain": item.get("Domain(s)", ""),
            "timeline": item.get("Timeline", ""),
            "targets": item.get("Targets", ""),
            "risk": item.get("Risk appetite", ""),
            "collaboration_type": item.get("Preferred collaboration type", ""),
            "outcome": item.get("Project Outcome", ""),
        })

    return {"status": "success", "results": projects}
