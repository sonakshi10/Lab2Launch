import chromadb
from config import CHROMA_PAPERS, CHROMA_INVESTORS, CHROMA_RESEARCHERS

def check_collection(path, name):
    client = chromadb.PersistentClient(path=path)
    collection = client.get_or_create_collection(name=name)
    print(f"{name}: {collection.count()} embeddings")

print("\nChecking Chroma collections:\n")

check_collection(CHROMA_PAPERS, "paper_embeddings")
check_collection(CHROMA_INVESTORS, "investor_business_project_summaries_e5")
check_collection(CHROMA_RESEARCHERS, "researcher_paper_expertise_e5")