# Lab2Launch

**Research • Connect • Launch**

Lab2Launch is an AI-powered matching platform that helps researchers, businesses, and investors discover high-value collaboration and commercialization opportunities.

Instead of relying on keyword search alone, Lab2Launch combines structured filtering, semantic retrieval, role-based access, explainable ranking metrics, and LLM-generated recommendations to help the right research reach the right market opportunity.

---

## Why Lab2Launch?

Every year, valuable research stays trapped in papers, institutional repositories, and academic databases. At the same time, companies struggle to find the right technical expertise, and investors struggle to identify credible research-backed opportunities.

The problem is not always a lack of innovation. It is often a lack of discoverability.

Lab2Launch closes that gap by translating academic knowledge, business needs, and investor preferences into structured AI-readable profiles, then recommending the most relevant matches with transparent reasoning.

---

## Core Use Cases

### 1. Researchers
Researchers can:
- discover companies and projects aligned with their work
- find similar researchers and possible collaborators
- upload papers and make their expertise searchable
- identify market problems where their research could create impact

### 2. Businesses / Industry Users
Businesses can:
- describe a technical problem in natural language
- find relevant researchers and papers
- create and manage business/project profiles
- discover investor interest after creating project opportunities

### 3. Investors
Investors can:
- search for investable projects
- rank opportunities by domain, budget, maturity, risk, and geography
- save investor preferences
- view project/company opportunities through a portfolio lens

---

## What Makes It Different?

Lab2Launch is not just a search tool.

It combines:

- **Structured filtering** for exact constraints such as country, budget, role, risk appetite, and project stage
- **Semantic retrieval** using embeddings to understand meaning beyond keywords
- **Role-based routing** so users only search the entities relevant to their role
- **Explainable ranking metrics** so recommendations are transparent and defensible
- **LLM explanation layer** to turn scores into human-readable reasoning
- **Research-to-market workflows** across researchers, companies, projects, and investors

---

## System Architecture

```text
User Query
   ↓
Role-Based Routing
   ↓
Structured Filtering
SQLite filters by domain, country, budget, stage, risk, collaboration type
   ↓
Semantic Retrieval
ChromaDB retrieves top matches using multilingual embeddings
   ↓
Ranking Engine
Candidates are re-ranked using semantic similarity + structured signals
   ↓
LLM Explanation
The LLM explains why the top matches are relevant
   ↓
Ranked Results
Users see recommendations, scores, reasons, and next steps
```

### Hybrid RAG Approach

Lab2Launch uses a hybrid RAG pipeline:

```text
SQL filtering + vector search + LLM explanation
```

The system does not send the full database to the LLM. It first filters, retrieves, and ranks candidates, then uses the LLM only to explain the top matches.

---

## Tech Stack

### Frontend
- Streamlit
- Python
- Custom CSS styling
- Role-based dashboards

### Backend
- FastAPI
- Python
- SQLite
- ChromaDB
- Sentence Transformers

### AI / Retrieval
- ChromaDB persistent collections
- Sentence-transformer embeddings
- Semantic search over papers, researcher expertise, projects, and investor/project summaries
- LLM explanation layer

### Data
- SQLite for structured metadata
- ChromaDB for embeddings
- Uploaded paper files stored locally under the data directory

---

## Repository Structure

```text
Lab2Launch/
├── backend/
│   ├── main.py
│   ├── db/
│   ├── services/
│   └── scripts/
│       ├── ingest.py
│       ├── check_chroma.py
│       ├── check_sqlite.py
│       ├── init_auth.py
│       └── reset_users.py
│
├── frontend/
│   ├── app.py
│   ├── auth/
│   ├── components/
│   └── pages/
│
├── data/
├── main.py
├── requirements.txt
├── app.db
└── README.md
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd Lab2Launch
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS / Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Initialize the Database

Create the authentication table:

```bash
python backend/scripts/init_auth.py
```

Load workbook data into SQLite and create ChromaDB embeddings:

```bash
python backend/scripts/ingest.py
```

Verify the SQLite database:

```bash
python backend/scripts/check_sqlite.py
```

Verify ChromaDB collections:

```bash
python backend/scripts/check_chroma.py
```

Clear local demo users if needed:

```bash
python backend/scripts/reset_users.py
```

---

## Running the Application

### Start the backend

From the project root:

```bash
uvicorn main:app --reload
```

The backend will run at:

```text
http://127.0.0.1:8000
```

### Start the frontend

In a second terminal:

```bash
streamlit run frontend/app.py
```

The Streamlit app will open in the browser.

---

## API Overview

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | `/signup` | Create a user account |
| POST | `/login` | Log in and return user role |

### Researcher APIs
| Method | Endpoint | Description |
|---|---|---|
| POST | `/researcher` | Search researchers |
| POST | `/researcher/relevant-projects` | Find projects relevant to a researcher |
| POST | `/researcher/similar-researchers` | Find similar researchers |
| POST | `/researcher/papers/search` | Search papers |
| POST | `/researcher/papers/upload` | Upload and save a paper |

### Industry APIs
| Method | Endpoint | Description |
|---|---|---|
| POST | `/industry` | Find researchers for a project description |
| POST | `/industry/researcher-matches` | Get ranked researcher matches |
| POST | `/industry/business/save` | Save business profile |
| POST | `/industry/project/save` | Save project |
| POST | `/industry/project/delete` | Delete project |
| POST | `/industry/investors` | List relevant investors |

### Investor APIs
| Method | Endpoint | Description |
|---|---|---|
| POST | `/investor` | Find projects for an investor query |
| POST | `/investor/projects/search` | Search ranked project matches |
| POST | `/investor/profile/save` | Save investor profile |
| POST | `/investor/portfolio` | View investor portfolio opportunities |

---

## Matching Metrics

Lab2Launch calculates a match score using normalized fit signals.

### Researcher → Company
The system considers:
- domain fit
- commercialization fit
- company readiness
- funding fit
- collaboration fit
- geography fit

### Company → Researcher
The system considers:
- domain fit
- research strength
- commercialization fit
- collaboration fit
- geography fit

### Investor → Project
The system considers:
- domain fit
- budget fit
- risk fit
- project maturity
- company readiness
- commercial potential
- geography fit

### Investor → Company
Company-level investment opportunity is derived from project-level scores:

```text
InvestorCompanyScore =
0.70 × best_project_score
+ 0.30 × average_top_project_score
```

This rewards companies with one strong investable project while still considering the overall quality of their project pipeline.

---

## Scoring Philosophy

All fit scores are normalized to a common scale:

```text
0 = poor fit
100 = excellent fit
```

The final match score is a weighted combination of normalized fit scores.

The confidence score is tracked separately to show how reliable the recommendation is based on available evidence.

```text
match_score = weighted average of fit scores

ranking_score = match_score × (0.85 + 0.15 × confidence_score)
```

This ensures the platform can explain not only *who* is recommended, but *why* the recommendation is trustworthy.

---

## Example Workflow

A business enters:

```text
We need computer vision research for detecting crop disease using drone images.
```

Lab2Launch:
1. identifies the user role as business
2. selects papers and researchers as the allowed search pool
3. applies structured filters such as domain, language, region, and research stage
4. retrieves relevant papers and researchers using semantic embeddings
5. joins retrieved results with metadata such as h-index, patents, grants, and citations
6. computes fit scores
7. ranks the top candidates
8. generates a human-readable explanation

Example output:

```text
Dr. X is a strong match because their work focuses on drone-based crop disease imaging,
they have relevant applied research experience, strong citation impact, and prior grant-backed work.
```

---

## Current Prototype Status

Implemented:
- role-based login flow
- researcher, industry, and investor dashboards
- SQLite-backed structured data storage
- ChromaDB-backed semantic retrieval
- paper upload flow
- business and project profile saving
- investor profile saving
- ranked researcher/project search endpoints
- helper scripts for ingestion and database checks

In progress / next improvements:
- production-grade authentication
- richer LLM explanations
- improved UI responsiveness
- deployment configuration
- expanded multilingual dataset ingestion
- feedback-based ranking personalization

---

## Roadmap

### Phase 1: Pilot Launch
- onboard initial universities, SMEs, and investors
- curate verified research/project datasets
- improve match explanations
- validate ranking quality with user feedback

### Phase 2: Production Readiness
- deploy with managed cloud infrastructure
- add monitoring and audit logs
- improve role-based access control
- support document-level permissioning

### Phase 3: Scale
- integrate institutional repositories
- add patent and funding database integrations
- enable collaboration rooms
- support multi-language discovery at scale
- introduce adaptive user-controlled weights

---

## Vision

Lab2Launch aims to become the AI matching layer between academia, industry, and capital.

Because the world cannot afford for good research to stay unread.

---

## License

Add your project license here.

---

## Team

| Name | Role | Location |
|---|---|---|
| **Prajit Rajendran** | AI Engineer | France |
| **Preeti Verma** | NLP Lead | Spain |
| **Priyanshi Rastogi** | Data Scientist | United Kingdom |
| **Sonakshi Agarwal** | Backend Developer | United Kingdom |
| **Swastik Bhattacharya** | Statistician | United Kingdom |

Together, Team Lab2Launch brings expertise across AI engineering, NLP, data science, backend development, and statistics to build an explainable AI matching platform for research commercialization.

