# Project 6: Custom Chatbot (RAG System)

This project implements a Retrieval Augmented Generation (RAG) chatbot using Streamlit, LangChain, and ChromaDB. It allows users to upload their own documents (PDF, DOCX, TXT), which are then ingested into a local vector store. The chatbot can then answer questions based on the content of these ingested documents, leveraging a local Large Language Model (LLM) via Ollama.

## Purpose

The main purpose of this project is to demonstrate how to build a custom chatbot that can answer questions over a specific knowledge base (your uploaded documents). This is particularly useful for creating domain-specific chatbots, internal knowledge base assistants, or personalized information retrieval systems without sending sensitive data to external LLM providers.

## How to Run

1.  **Install Ollama:**
    Download and install Ollama from [ollama.com](https://ollama.com/).
2.  **Download LLM and Embedding Models:**
    Pull the required models for the LLM and embeddings:
    ```bash
    ollama pull llama3
    ollama pull mxbai-embed-large
    ```
3.  **Navigate to the project directory:**
    ```bash
    cd D:/Sirius/projects/AI_Portfolio/project6_customChatbot
    ```
4.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```
5.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    The `requirements.txt` file contains all necessary dependencies, including `langchain`, `langchain-community`, `langchain-ollama`, `langchain-chroma`, `streamlit`, `pypdf`, `docx2txt`, etc.
6.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```
    This will open the application in your web browser. You can then upload documents, and once ingested, start asking questions.

## Techniques Used

*   **Streamlit:** Provides the interactive web-based user interface for uploading documents and interacting with the chatbot.
*   **Ollama:** Serves as the local runtime for both the Large Language Model (`llama3`) for generating responses and the embedding model (`mxbai-embed-large`) for creating document embeddings.
*   **LangChain:** A powerful framework for developing applications powered by LLMs. Key LangChain components used include:
    *   **Document Loaders:** `PyPDFLoader`, `Docx2txtLoader`, `TextLoader` for ingesting various document types.
    *   **Text Splitters:** `RecursiveCharacterTextSplitter` for breaking down documents into manageable chunks.
    *   **Embeddings:** `OllamaEmbeddings` for converting text chunks into numerical vector representations.
    *   **Retrievers:** `chroma.as_retriever` for fetching relevant document chunks based on a query.
    *   **Chains:** `create_stuff_documents_chain` and `create_retrieval_chain` to build the RAG pipeline, combining retrieval with LLM generation.
*   **ChromaDB:** A lightweight, open-source vector database used to store and retrieve document embeddings locally. The `chroma_store` directory persists the vector database.
*   **Retrieval Augmented Generation (RAG):** The core architecture where the LLM's response is augmented with retrieved information from your documents, ensuring factual accuracy and reducing hallucinations.

## Issues and Considerations

*   **Ollama Setup:** Ensure Ollama is running and both `llama3` and `mxbai-embed-large` models are pulled before starting the application.
*   **Performance:** The speed of ingestion and response generation depends on your local hardware and the size of the documents/corpus.
*   **Chunking Strategy:** The `RecursiveCharacterTextSplitter` parameters (`chunk_size`, `chunk_overlap`) are crucial for effective retrieval. Experimentation might be needed for optimal performance on different document types.
*   **Context Window:** Even with RAG, the LLM's context window can be a limitation if too many retrieved chunks are passed.
*   **Document Types:** Currently supports PDF, DOCX, and TXT. Extending to other formats would require additional loaders.
*   **Reset Corpus:** The "Reset corpus" button is essential for clearing the vector store and starting fresh with new documents.

## Contributions

Feel free to contribute to this project by opening issues or submitting pull requests.
