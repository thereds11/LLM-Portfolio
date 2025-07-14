# embedding.py
from pathlib import Path
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

BASE_URL = "http://127.0.0.1:11434"      # IPv4 loopback avoids ::1 mismatch
EMBED_MODEL = "mxbai-embed-large"

embeddings = OllamaEmbeddings(
    model=EMBED_MODEL,
    base_url=BASE_URL,
)

PERSIST_DIR = Path("chroma_store")
PERSIST_DIR.mkdir(exist_ok=True)

# Re-open existing collection if it’s there, else start empty
chroma = Chroma(
    collection_name="company_corpus",
    embedding_function=embeddings,
    persist_directory=str(PERSIST_DIR),
)

def ingest(paths: list[str]) -> None:
    """Add new documents and persist the store."""
    from ingestion import load_and_split  # local import to avoid circular refs
    for path in paths:
        docs = load_and_split(path)
        if docs:             # avoid empty chunks
            chroma.add_documents(docs)
