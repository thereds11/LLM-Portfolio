# ingestion.py
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

_SPLITTER = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)

def _loader_for(path: Path):
    if path.suffix.lower() == ".pdf":
        return PyPDFLoader(str(path))
    if path.suffix.lower() == ".docx":
        return Docx2txtLoader(str(path))
    return TextLoader(str(path), encoding="utf-8")

def load_and_split(path: str):
    raw_docs = _loader_for(Path(path)).load()          # → List[Document]
    texts    = [d.page_content for d in raw_docs]
    metas    = [d.metadata      for d in raw_docs]
    return _SPLITTER.create_documents(texts, metas)    # now type-safe
