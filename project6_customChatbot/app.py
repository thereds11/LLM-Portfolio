import tempfile
from pathlib import Path
import streamlit as st
from generate import RAG_CHAIN
from embedding import ingest, chroma, PERSIST_DIR
import shutil

st.title("Ask My Docs 🤖")

if "chain" not in st.session_state:
    st.session_state["chain"] = RAG_CHAIN

# -------- Upload & ingest ---------------------------------------------------
uploaded = st.file_uploader("Add docs", accept_multiple_files=True, type=["pdf", "docx", "txt"])
if uploaded:
    temp_root = Path(tempfile.gettempdir()) / "rag_uploads"
    temp_root.mkdir(exist_ok=True)
    tmp_paths = []
    for file in uploaded:
        safe_name = file.name.replace(" ", "_")
        tmp_path = temp_root / safe_name

        # Skip re-write if the exact file is already there
        if not tmp_path.exists():
            with tmp_path.open("wb") as f:
                f.write(file.getbuffer())

        tmp_paths.append(str(tmp_path))

    ingest(tmp_paths)
    st.success(f"Ingested {len(tmp_paths)} document(s). Current corpus size: {chroma._collection.count()}")

# -------- Chat --------------------------------------------------------------
question = st.chat_input("Ask anything about your docs…")
if question:
    if chroma._collection.count() == 0:
        st.warning("No documents ingested yet — upload something first.")
    else:
        with st.spinner("Thinking…"):
            res = st.session_state["chain"].invoke({"input": question})
        st.write(res["answer"])
        with st.expander("Sources"):
            for doc in res["context"]:
                st.markdown(f"- {doc.metadata.get('source', 'inline')}")

# ---------- Reset corpus ----------------------------------------------------
if st.button("🔄 Reset corpus", type="secondary"):
    # 1. Delete Chroma collection  (removes all vectors)
    chroma._client.delete_collection("company_corpus")   # low-level API

    # 2. Kill on-disk files so the directory starts clean
    shutil.rmtree(PERSIST_DIR, ignore_errors=True)       # safe even if missing
    PERSIST_DIR.mkdir(exist_ok=True)

    # 3. Clear Streamlit session + rebuild empty resources
    st.session_state.clear()                             # nuke all keys
    st.session_state["chain"] = RAG_CHAIN               # fresh pipeline

    st.toast("Corpus, cache & session reset — start uploading again!", icon="🗑️")