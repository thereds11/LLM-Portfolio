from __future__ import annotations
from pathlib import Path
import os, subprocess
from typing import List, Iterable
from langchain_community.document_loaders import TextLoader
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

_SPLITTER = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)

_EXCLUDE_DIRS = {
    "node_modules", ".git", ".hg", ".svn", ".idea", ".vscode", ".erb",
    "venv", ".venv", "__pycache__", ".next", "dist", "build",
    "release", "patch"
}

_EXTS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".java", ".rb",
    ".rs", ".c", ".cpp", ".cs", ".php", ".html", ".css", ".json",
    ".yaml", ".yml", ".md", ".txt"
}

def _dir_docs(root: Path) -> Iterable[Document]:
    """Yield one summary doc per directory (RAPTOR bottom-up layer)."""
    for dr, dnames, files in os.walk(root):
        dnames[:] = [d for d in dnames if d not in _EXCLUDE_DIRS]
        if files:
            summary = (f"## Folder: {Path(dr).relative_to(root)}\n"
                       f"Files: {', '.join(files[:20])}")
            yield Document(page_content=summary,
                           metadata={"type": "dir", "path": str(dr)})

import platform, subprocess

def _repo_doc(root: Path) -> Document:
    if platform.system() == "Windows":
        cmd = "tree /F /A"
        tree_txt = subprocess.check_output(cmd, cwd=str(root), text=True, shell=True)
    else:
        tree_txt = subprocess.check_output(["tree", "-L", "2", str(root)], text=True)

    readme = (root / "README.md").read_text(errors="ignore") if (root / "README.md").exists() else ""
    return Document(page_content=tree_txt + "\n\n" + readme,
                    metadata={"type": "repo", "path": str(root)})


def file_chunks(root: Path) -> List[Document]:
    docs: List[Document] = []
    for r, dnames, fnames in os.walk(root):
        dnames[:] = [d for d in dnames if d not in _EXCLUDE_DIRS]
        for fn in fnames:
            fp = Path(r) / fn
            if fp.suffix.lower() not in _EXTS or fp.stat().st_size > 200_000:
                continue                                    # skip big / binary
            try:
                raw = TextLoader(str(fp), encoding="utf-8").load()
            except Exception:
                continue
            docs.extend(
                _SPLITTER.create_documents(
                    [d.page_content for d in raw],
                    [{**d.metadata, "rel_path": str(fp.relative_to(root)),
                      "type": "file"} for d in raw],
                )
            )
    return docs

def iterate_repo(root: Path) -> List[Document]:
    root = root.expanduser().resolve()
    return [*_dir_docs(root), _repo_doc(root), *file_chunks(root)]
