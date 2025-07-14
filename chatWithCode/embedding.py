from pathlib import Path
import os
from typing import Generator, Tuple
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from ingestion import iterate_repo, _EXCLUDE_DIRS, _EXTS
from langchain.schema import Document

BASE_URL = "http://127.0.0.1:11434"
EMBED_MODEL = "mxbai-embed-large"

embeddings = OllamaEmbeddings(model=EMBED_MODEL, base_url=BASE_URL)

PERSIST_DIR = Path("chroma_store"); PERSIST_DIR.mkdir(exist_ok=True)

chroma = Chroma(
    collection_name="company_corpus",
    embedding_function=embeddings,
    persist_directory=str(PERSIST_DIR),
)

def ingest_folder_stream(folder: str) -> Generator[Tuple[str, int], None, None]:
    """Embed whole repo (structure + files) yielding progress."""
    docs = iterate_repo(Path(folder))
    total = len(docs)
    for i, doc in enumerate(docs, 1):
        chroma.add_documents([doc])
        yield doc.metadata.get("path", "chunk"), i
    # Chroma auto-persists → nothing else to call
