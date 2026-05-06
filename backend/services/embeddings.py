from functools import lru_cache

from sentence_transformers import SentenceTransformer
import chromadb
from config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def load_embedding_model():
    return SentenceTransformer(EMBEDDING_MODEL)

def get_chroma_client(path):
    return chromadb.PersistentClient(path=path)

def get_collection(client, name):
    return client.get_or_create_collection(name=name)
