# generate.py
from langchain_community.chat_models import ChatOllama
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import PromptTemplate
from langchain import hub           # LangChain prompt hub
from embedding import chroma, BASE_URL

# --- LLM -------------------------------------------------------------------
llm = ChatOllama(
    model="llama3:latest",
    base_url=BASE_URL,
    temperature=0.4,
    timeout=120,
)

# --- Retriever -------------------------------------------------------------
retriever = chroma.as_retriever(search_kwargs={"k": 4})

# --- Prompt & combine chain (no more MapRerank) ----------------------------
prompt = hub.pull("langchain-ai/retrieval-qa-chat")  # 4-line, RAG-ready prompt :contentReference[oaicite:3]{index=3}
# If you want to keep your own template, substitute PromptTemplate.from_template(...)

combine_chain = create_stuff_documents_chain(
    llm=llm,
    prompt=prompt,
    document_variable_name="context",    # matches create_retrieval_chain default
)

# --- RAG pipeline ----------------------------------------------------------
RAG_CHAIN = create_retrieval_chain(retriever, combine_chain)

# Optional CLI self-test (won’t execute inside Streamlit)
if __name__ == "__main__":
    print(RAG_CHAIN.invoke({"input": "self-test question"})["answer"])
