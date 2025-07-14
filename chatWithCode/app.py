import os, shutil
from pathlib import Path
import streamlit as st
from generate import build_chain
from embedding import chroma, PERSIST_DIR, ingest_folder_stream

st.set_page_config(page_title="Ask My Docs", page_icon="🤖")
st.title("Ask My Docs  🤖")

for role, content in st.session_state.get("chat", []):
    with st.chat_message(role):
        st.markdown(content)


# --- bootstrap -------------------------------------------------------------
if "chain" not in st.session_state: st.session_state["chain"] = build_chain()
if "chat"  not in st.session_state: st.session_state["chat"]  = []

# --- reset -----------------------------------------------------------------
if st.button("🗑️  Reset corpus", type="secondary"):
    chroma._client.delete_collection("company_corpus")
    shutil.rmtree(PERSIST_DIR, ignore_errors=True); PERSIST_DIR.mkdir(exist_ok=True)
    st.session_state.clear(); st.session_state["chain"] = build_chain(); st.session_state["chat"] = []
    st.toast("Corpus wiped. Ingest a folder to begin.", icon="✅")

# --- ingest ----------------------------------------------------------------
folder = st.text_input("Path to repository", "")
if st.button("📂 Ingest") and folder:
    est = sum(len(f) for _,_,f in os.walk(folder))
    bar, status = st.progress(0.0), st.empty()
    for idx, (fname, chunks) in enumerate(ingest_folder_stream(folder), 1):
        bar.progress(idx / max(est, 1), text=f"Embedding {Path(fname).name}")
    st.session_state["chain"] = build_chain()
    bar.empty(); st.success(f"Ingest complete. {chroma._collection.count()} chunks in store.")

# --- chat ------------------------------------------------------------------
def stream_answer(q):
    acc = ""
    for chunk in st.session_state["chain"].stream({"input": q}):
        token = chunk if isinstance(chunk, str) else str(chunk)
        acc += token
        yield token
    return acc  # final text

query = st.chat_input("Ask anything…")
if query:
    st.session_state["chat"].append(("user", query))
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        answer_box = st.empty()
        acc = ""
        for token in stream_answer(query):
            acc += token
            answer_box.markdown(acc)
    st.session_state["chat"].append(("assistant", acc))
