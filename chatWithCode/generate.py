from langchain_community.chat_models import ChatOllama
from langchain.chains.retrieval import create_retrieval_chain
from langchain.retrievers.document_compressors import EmbeddingsFilter
from langchain.retrievers import ContextualCompressionRetriever
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain import hub
from embedding import chroma, BASE_URL, embeddings
from langchain_core.runnables import Runnable

llm = ChatOllama(model="deepseek-r1:8b", base_url=BASE_URL,
                 temperature=0.4)

def build_chain() -> Runnable:
    filter_ = EmbeddingsFilter(embeddings=embeddings,
                               similarity_threshold=0.5)   # .5 is plenty
    hier = ContextualCompressionRetriever(
        base_retriever=chroma.as_retriever(search_k=8),
        base_compressor=filter_,
    )
    prompt  = hub.pull("langchain-ai/retrieval-qa-chat")
    combine = create_stuff_documents_chain(llm, prompt,
                                           document_variable_name="context")
    return (create_retrieval_chain(hier, combine) |
            (lambda d: d["answer"]))

# hierarchical retriever
filter_ = EmbeddingsFilter(embeddings=embeddings, similarity_threshold=0.85)  # :contentReference[oaicite:2]{index=2}
hier    = ContextualCompressionRetriever(base_retriever=chroma.as_retriever(),
                                         base_compressor=filter_)              # :contentReference[oaicite:3]{index=3}

prompt  = hub.pull("langchain-ai/retrieval-qa-chat")

combine = create_stuff_documents_chain(llm, prompt, document_variable_name="context")

# pipe to return **only** the answer string
RAG_CHAIN = (create_retrieval_chain(hier, combine) |
             (lambda d: d["answer"]))
