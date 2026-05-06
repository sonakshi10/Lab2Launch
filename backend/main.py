from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from db.profile_repository import init_db
from services.researcher import (
    find_relevant_projects,
    find_researchers,
    find_similar_researchers,
    save_paper,
    search_papers,
)
from services.industry import (
    delete_project,
    find_researcher_matches,
    find_researchers_for_project,
    list_investors,
    save_business,
    save_project,
)
from services.investor import (
    find_project_matches,
    find_projects_for_investor,
    investor_portfolio,
    save_investor_record,
)
from services.auth import signup, login
from fastapi import Request
from config import BASE_DIR

app = FastAPI()

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def root():
    return {"message": "Backend running"}

@app.post("/researcher")
def researcher_api(query: str):
    return find_researchers(query)

@app.post("/researcher/relevant-projects")
async def researcher_relevant_projects_api(request: Request):
    data = await request.json()
    return find_relevant_projects(data.get("query", ""), data.get("n_results", 10))

@app.post("/researcher/similar-researchers")
async def researcher_similar_researchers_api(request: Request):
    data = await request.json()
    return find_similar_researchers(data.get("query", ""), data.get("n_results", 10))

@app.post("/researcher/papers/search")
async def researcher_search_papers_api(request: Request):
    data = await request.json()
    return search_papers(data.get("query", ""), data.get("n_results", 10))

@app.post("/researcher/papers/upload")
async def researcher_upload_paper_api(
    user_id: str = Form(""),
    researcher_id: str = Form(""),
    paper_id: str = Form(...),
    title: str = Form(...),
    year: int = Form(0),
    venue: str = Form(""),
    impact_score: int = Form(0),
    citations: int = Form(0),
    pages: int = Form(0),
    keywords: str = Form(""),
    abstract: str = Form(""),
    paper_type: str = Form("Uploaded"),
    file: UploadFile | None = File(None),
):
    pdf_link = ""
    if file and file.filename:
        upload_dir = Path(BASE_DIR) / "data" / "uploads" / "papers"
        upload_dir.mkdir(parents=True, exist_ok=True)
        safe_name = Path(file.filename).name
        target = upload_dir / f"{paper_id}_{safe_name}"
        target.write_bytes(await file.read())
        pdf_link = str(target)

    summary = abstract
    return save_paper({
        "user_id": user_id,
        "researcher_id": researcher_id,
        "paper_id": paper_id,
        "title": title,
        "pdf_link": pdf_link,
        "year": year,
        "paper_type": paper_type,
        "venue": venue,
        "impact_score": impact_score,
        "citations": citations,
        "abstract": abstract,
        "keywords": keywords,
        "summary": summary,
        "pages": pages,
        "collaborations": "",
    })

@app.post("/industry")
def industry_api(project_description: str):
    return find_researchers_for_project(project_description)

@app.post("/industry/researcher-matches")
async def industry_researcher_matches_api(request: Request):
    data = await request.json()
    return find_researcher_matches(data.get("query", ""), data.get("n_results", 10))

@app.post("/industry/business/save")
async def industry_business_save_api(request: Request):
    data = await request.json()
    return save_business(data)

@app.post("/industry/project/save")
async def industry_project_save_api(request: Request):
    data = await request.json()
    return save_project(data)

@app.post("/industry/project/delete")
async def industry_project_delete_api(request: Request):
    data = await request.json()
    return delete_project(data.get("project_id", ""))

@app.post("/industry/investors")
async def industry_investors_api(request: Request):
    data = await request.json()
    return list_investors(data.get("query", ""), data.get("n_results", 20))

@app.post("/investor")
def investor_api(query: str):
    return find_projects_for_investor(query)

@app.post("/investor/projects/search")
async def investor_projects_search_api(request: Request):
    data = await request.json()
    return find_project_matches(data.get("query", ""), data.get("n_results", 10))

@app.post("/investor/profile/save")
async def investor_profile_save_api(request: Request):
    data = await request.json()
    return save_investor_record(data)

@app.post("/investor/portfolio")
async def investor_portfolio_api(request: Request):
    data = await request.json()
    return investor_portfolio(data.get("investor_id", ""))

@app.post("/signup")
async def signup_api(request: Request):
    data = await request.json()
    return signup(data["email"], data["password"], data["role"])

@app.post("/login")
async def login_api(request: Request):
    data = await request.json()
    return login(data["email"], data["password"])
