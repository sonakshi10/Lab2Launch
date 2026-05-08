import sqlite3
import pandas as pd
from config import SQLITE_DB_PATH, CHROMA_RESEARCHERS
from config import CHROMA_INVESTORS, CHROMA_PAPERS
from services.embeddings import load_embedding_model, get_chroma_client, get_collection
from services.metrics import calculate_researcher_metrics

def find_researchers(query, preferred_country="", preferred_language="English", min_h_index=None, min_grants=None):

    conn = sqlite3.connect(SQLITE_DB_PATH)

    # ---------------- FILTERING ----------------
    conditions = []

    if preferred_country:
        conditions.append(f"\"Affiliated country\" LIKE '%{preferred_country}%'")

    if preferred_language:
        conditions.append(f"\"Primary language\" LIKE '%{preferred_language}%'")

    if min_h_index:
        conditions.append(f"\"h index\" >= {min_h_index}")

    if min_grants:
        conditions.append(f"\"Number of grants\" >= {min_grants}")

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    researchers = pd.read_sql(f"""
        SELECT * FROM researcher_attributes
        {where_clause}
    """, conn)

    papers = pd.read_sql("SELECT * FROM paper_attributes", conn)
    conn.close()

    # ---------------- EMBEDDINGS ----------------
    model = load_embedding_model()
    client = get_chroma_client(CHROMA_RESEARCHERS)
    collection = get_collection(client, "researcher_paper_expertise_e5")

    query_embedding = model.encode("query: " + query).tolist()

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


def _query_collection(path, collection_name, query, n_results=10, prefix="query: "):
    model = load_embedding_model()
    client = get_chroma_client(path)
    collection = get_collection(client, collection_name)

    query_embedding = model.encode(prefix + query).tolist()
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "distances", "metadatas"],
    )


def find_relevant_projects(query, researcher_country="", researcher_domain="", n_results=10):
    results = _query_collection(
        CHROMA_INVESTORS,
        "investor_business_project_summaries_e5",
        query,
        n_results,
    )

    ids = [str(item) for item in results.get("ids", [[]])[0]]
    rows = _rows_by_id("project_attributes", "Project ID", ids)
    distances = results.get("distances", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    projects = []
    for index, project_id in enumerate(ids):
        row = rows.get(project_id, {})
        
        # Filter: only show projects visible to researchers
        visible = row.get("Visible to researchers", 1)
        if not visible:
            continue
        
        distance = distances[index] if index < len(distances) else None
        
        # Calculate metrics
        metrics = calculate_researcher_metrics(
            distance=distance,
            researcher_h_index=None,  # Not applicable for researcher searching projects
            researcher_i10_index=None,
            researcher_grants=None,
            project_domain=row.get("Domain(s)", "") or metadatas[index].get("domain", ""),
            researcher_domain=researcher_domain,
            project_country=metadatas[index].get("country", ""),
            researcher_country=researcher_country,
            collaboration_match=0.5,
        )
        
        projects.append({
            "project_id": project_id,
            "company_name": row.get("Company name") or metadatas[index].get("company_name", ""),
            "status": row.get("Current status", ""),
            "problem": row.get("Problem tackled") or documents[index],
            "budget": row.get("Budget", ""),
            "domain": row.get("Domain(s)") or metadatas[index].get("domain", ""),
            "timeline": row.get("Timeline", ""),
            "targets": row.get("Targets", ""),
            "risk": row.get("Risk appetite") or metadatas[index].get("risk", ""),
            "collaboration_type": row.get("Preferred collaboration type", ""),
            "distance": distance,
            "metrics": metrics.to_dict(),
        })

    return {"status": "success", "results": projects}


def find_similar_researchers(query, n_results=10):
    results = _query_collection(
        CHROMA_RESEARCHERS,
        "researcher_paper_expertise_e5",
        query,
        n_results,
    )

    paper_ids = [str(item) for item in results.get("ids", [[]])[0]]
    distances = results.get("distances", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    researcher_ids = []
    for metadata in metadatas:
        researcher_id = str(metadata.get("researcher_id", ""))
        if researcher_id and researcher_id not in researcher_ids:
            researcher_ids.append(researcher_id)

    researcher_rows = _rows_by_id("researcher_attributes", "Researcher ID", researcher_ids)

    researchers = []
    seen = set()
    for index, metadata in enumerate(metadatas):
        researcher_id = str(metadata.get("researcher_id", ""))
        if not researcher_id or researcher_id in seen:
            continue

        seen.add(researcher_id)
        row = researcher_rows.get(researcher_id, {})
        researchers.append({
            "researcher_id": researcher_id,
            "name": row.get("Name", ""),
            "affiliation": row.get("Affiliation", ""),
            "country": row.get("Affiliated country", ""),
            "language": row.get("Primary language", ""),
            "h_index": row.get("h index", ""),
            "i10_index": row.get("i-10 index", ""),
            "grants": row.get("Number of grants", ""),
            "matching_paper_id": paper_ids[index] if index < len(paper_ids) else "",
            "matching_paper_title": metadata.get("paper_title", ""),
            "keywords": metadata.get("keywords", ""),
            "distance": distances[index] if index < len(distances) else None,
        })

    return {"status": "success", "results": researchers}


def search_papers(query, n_results=10):
    results = _query_collection(
        CHROMA_PAPERS,
        "paper_embeddings",
        query,
        n_results,
        prefix="",
    )

    ids = [str(item) for item in results.get("ids", [[]])[0]]
    rows = _rows_by_id("paper_attributes", "Paper ID", ids)
    distances = results.get("distances", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    papers = []
    for index, paper_id in enumerate(ids):
        row = rows.get(paper_id, {})
        papers.append({
            "paper_id": paper_id,
            "researcher_id": row.get("Researcher ID") or metadatas[index].get("researcher_id", ""),
            "title": row.get("Name / Title") or metadatas[index].get("paper_title", ""),
            "pdf_link": row.get("Link to PDF", ""),
            "year": row.get("Year of publication", ""),
            "paper_type": row.get("Type of paper", ""),
            "venue": row.get("Venue", ""),
            "impact_score": row.get("Impact Score", ""),
            "citations": row.get("Number of citations", ""),
            "abstract": row.get("Abstract", ""),
            "keywords": row.get("Keywords", ""),
            "summary": row.get("Summary") or documents[index],
            "pages": row.get("Number of pages", ""),
            "collaborations": row.get("Collaborations", ""),
            "distance": distances[index] if index < len(distances) else None,
        })

    return {"status": "success", "results": papers}


def save_paper(paper):
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.execute(
        """
        INSERT OR REPLACE INTO paper_attributes (
            "Paper ID",
            "Researcher ID",
            "Name / Title",
            "Link to PDF",
            "Year of publication",
            "Type of paper",
            "Venue",
            "Impact Score",
            "Number of citations",
            "Abstract",
            "Keywords",
            "Summary",
            "Number of pages",
            "Collaborations"
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            paper["paper_id"],
            paper["researcher_id"],
            paper["title"],
            paper.get("pdf_link", ""),
            paper.get("year"),
            paper.get("paper_type", "Uploaded"),
            paper.get("venue", ""),
            paper.get("impact_score", 0),
            paper.get("citations", 0),
            paper.get("abstract", ""),
            paper.get("keywords", ""),
            paper.get("summary", ""),
            paper.get("pages", 0),
            paper.get("collaborations", ""),
        ),
    )
    conn.commit()
    conn.close()

    _upsert_paper_embeddings(paper)
    return {"status": "success", "paper_id": paper["paper_id"]}


def _upsert_paper_embeddings(paper):
    model = load_embedding_model()
    paper_id = str(paper["paper_id"])
    title = paper.get("title", "")
    abstract = paper.get("abstract", "")
    keywords = paper.get("keywords", "")
    summary = paper.get("summary", "") or abstract
    researcher_id = str(paper.get("researcher_id", ""))

    paper_document = summary or "\n".join([title, abstract, keywords])
    expertise_document = "\n".join([
        f"Name / Title: {title}",
        f"Abstract: {abstract}",
        f"Keywords: {keywords}",
        f"Summary: {summary}",
    ])

    papers = get_collection(get_chroma_client(CHROMA_PAPERS), "paper_embeddings")
    papers.upsert(
        ids=[paper_id],
        documents=[paper_document],
        embeddings=[model.encode(paper_document).tolist()],
        metadatas=[{
            "researcher_id": researcher_id,
            "paper_title": title,
        }],
    )

    researchers = get_collection(get_chroma_client(CHROMA_RESEARCHERS), "researcher_paper_expertise_e5")
    researchers.upsert(
        ids=[paper_id],
        documents=["passage: " + expertise_document],
        embeddings=[model.encode("passage: " + expertise_document).tolist()],
        metadatas=[{
            "researcher_id": researcher_id,
            "paper_title": title,
            "keywords": keywords,
        }],
    )
