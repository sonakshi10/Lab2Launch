import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SQLITE_DB_PATH = os.path.join(BASE_DIR, "data", "ideahack.db")

CHROMA_RESEARCHERS = os.path.join(BASE_DIR, "data", "chroma_researchers")
CHROMA_INVESTORS = os.path.join(BASE_DIR, "data", "chroma_investors")
CHROMA_PAPERS = os.path.join(BASE_DIR, "data", "chroma_papers")

EMBEDDING_MODEL = "intfloat/multilingual-e5-base"