import os
import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import OllamaEmbeddingFunction

OLLAMA_HOST = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DB_DIR =os.getenv("DATA_DIR", "../data")

ollama_em= OllamaEmbeddingFunction(
    url = f"{OLLAMA_HOST}/api/embeddings",
    model_name="nomic-embed-text"
)
def get_chroma_client():
    client = chromadb.PersistentClient(path = os.path.join(DB_DIR, "chroma_db"))
    return client
def get_anomaly_collection():
    client = get_chroma_client()

    collection = client.get_or_create_collection(
        name = "anomalies",
        embedding_function=ollama_em
    )
    return collection