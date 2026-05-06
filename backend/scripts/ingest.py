import os
import sqlite3
import pandas as pd
import sqlalchemy
import chromadb
from sentence_transformers import SentenceTransformer
from config import (
    SQLITE_DB_PATH,
    CHROMA_PAPERS,
    CHROMA_INVESTORS,
    CHROMA_RESEARCHERS,
    EMBEDDING_MODEL
)


# -------------------------------
# STEP 1: LOAD GOOGLE SHEETS → SQLITE
# -------------------------------
def load_data(google_sheets_url):

    spreadsheet_id = google_sheets_url.split("/d/")[1].split("/")[0]
    export_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=xlsx"

    all_sheets = pd.read_excel(export_url, sheet_name=None)

    engine = sqlalchemy.create_engine(f"sqlite:///{SQLITE_DB_PATH}")

    for sheet_name, df in all_sheets.items():
        if sheet_name != "Rules":
            df.to_sql(sheet_name, engine, index=False, if_exists="replace")

    print("Data loaded into SQLite")


# -------------------------------
# STEP 2: LOAD TABLES
# -------------------------------
def load_tables():
    conn = sqlite3.connect(SQLITE_DB_PATH)

    researcher_df = pd.read_sql("SELECT * FROM researcher_attributes", conn)
    paper_df = pd.read_sql("SELECT * FROM paper_attributes", conn)
    project_df = pd.read_sql("SELECT * FROM project_attributes", conn)

    conn.close()

    return researcher_df, paper_df, project_df


# -------------------------------
# STEP 3: INIT CHROMA
# -------------------------------
def init_chroma(path, collection_name):
    os.makedirs(path, exist_ok=True)
    client = chromadb.PersistentClient(path=path)
    collection = client.get_or_create_collection(name=collection_name)
    return collection


# -------------------------------
# STEP 4: INGEST PAPERS (INDUSTRY)
# -------------------------------
def ingest_papers(paper_df, model):

    collection = init_chroma(CHROMA_PAPERS, "paper_embeddings")

    existing_ids = set(collection.get(limit=None)["ids"]) if collection.count() > 0 else set()
    batch_ids = set()

    paper_content_col = None
    for col in ["Summary", "Abstract", "Name / Title", "Content"]:
        if col in paper_df.columns:
            paper_content_col = col
            break

    papers_to_add = []

    for _, row in paper_df.iterrows():
        paper_id = str(row["Paper ID"])

        if paper_id in existing_ids or paper_id in batch_ids:
            continue

        content = str(row.get(paper_content_col, ""))

        if content and content.strip() and content != "nan":

            papers_to_add.append({
                "id": paper_id,
                "document": content,
                "embedding": model.encode(content).tolist(),
                "metadata": {
                    "researcher_id": str(row.get("Researcher ID", "")),
                    "paper_title": row.get("Name / Title", "")
                }
            })

            batch_ids.add(paper_id)

    if papers_to_add:
        collection.add(
            ids=[p["id"] for p in papers_to_add],
            documents=[p["document"] for p in papers_to_add],
            embeddings=[p["embedding"] for p in papers_to_add],
            metadatas=[p["metadata"] for p in papers_to_add]
        )

    print(f"Papers ingested: {len(papers_to_add)}")


# -------------------------------
# STEP 5: INGEST PROJECTS (INVESTOR)
# -------------------------------
def ingest_projects(project_df, model):

    collection = init_chroma(CHROMA_INVESTORS, "investor_business_project_summaries_e5")

    existing_ids = set(collection.get(limit=None)["ids"]) if collection.count() > 0 else set()
    batch_ids = set()

    content_cols = [
        "Problem tackled",
        "Domain(s)",
        "Targets",
        "Company name",
        "Current status"
    ]

    projects_to_add = []

    for _, row in project_df.iterrows():
        project_id = str(row["Project ID"])

        if project_id in existing_ids or project_id in batch_ids:
            continue

        content = "\n".join([
            f"{col}: {row.get(col, '')}"
            for col in content_cols if col in project_df.columns
        ])

        if content.strip():
            text = "passage: " + content

            projects_to_add.append({
                "id": project_id,
                "document": text,
                "embedding": model.encode(text).tolist(),
                "metadata": {
                    "company_name": str(row.get("Company name", "")),
                    "domain": str(row.get("Domain(s)", "")),
                    "risk": str(row.get("Risk appetite", ""))
                }
            })

            batch_ids.add(project_id)

    if projects_to_add:
        collection.add(
            ids=[p["id"] for p in projects_to_add],
            documents=[p["document"] for p in projects_to_add],
            embeddings=[p["embedding"] for p in projects_to_add],
            metadatas=[p["metadata"] for p in projects_to_add]
        )

    print(f"Projects ingested: {len(projects_to_add)}")


# -------------------------------
# STEP 6: INGEST RESEARCHER PAPERS
# -------------------------------
def ingest_researchers(paper_df, model):

    collection = init_chroma(CHROMA_RESEARCHERS, "researcher_paper_expertise_e5")

    existing_ids = set(collection.get(limit=None)["ids"]) if collection.count() > 0 else set()
    batch_ids = set()

    content_cols = ["Name / Title", "Abstract", "Keywords", "Summary"]

    papers_to_add = []

    for _, row in paper_df.iterrows():
        paper_id = str(row["Paper ID"])

        if paper_id in existing_ids or paper_id in batch_ids:
            continue

        content = "\n".join([
            f"{col}: {row.get(col, '')}"
            for col in content_cols if col in paper_df.columns
        ])

        if content.strip():
            text = "passage: " + content

            papers_to_add.append({
                "id": paper_id,
                "document": text,
                "embedding": model.encode(text).tolist(),
                "metadata": {
                    "researcher_id": str(row.get("Researcher ID", "")),
                    "paper_title": str(row.get("Name / Title", "")),
                    "keywords": str(row.get("Keywords", ""))
                }
            })

            batch_ids.add(paper_id)

    if papers_to_add:
        collection.add(
            ids=[p["id"] for p in papers_to_add],
            documents=[p["document"] for p in papers_to_add],
            embeddings=[p["embedding"] for p in papers_to_add],
            metadatas=[p["metadata"] for p in papers_to_add]
        )

    print(f"Researcher expertise ingested: {len(papers_to_add)}")


# -------------------------------
# MAIN PIPELINE
# -------------------------------
def run_pipeline():

    GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/1UMJpc7RCEr9J1BOU_sVYn_CCYlE6pAPOrLkqJTEKI9c/edit?usp=drive_link"

    print("Starting ingestion pipeline")

    load_data(GOOGLE_SHEET)

    researcher_df, paper_df, project_df = load_tables()

    model = SentenceTransformer(EMBEDDING_MODEL)

    ingest_papers(paper_df, model)
    ingest_projects(project_df, model)
    ingest_researchers(paper_df, model)

    print("Ingestion complete")


if __name__ == "__main__":
    run_pipeline()