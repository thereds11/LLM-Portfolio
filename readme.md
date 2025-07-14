# LLM Engineer Portfolio

This repository contains a collection of projects built as part of my journey to become an LLM Engineer, following the roadmap provided by [Towards AI](https://pub.towardsai.net/build-your-llm-engineer-portfolio-a-3-month-roadmap-19826e39c185). Each project demonstrates different aspects of Large Language Model (LLM) engineering, from local LLM deployment to RAG systems and multimodal applications.

## Projects

*   **Project 1: Local LLM Chat** - A Streamlit-based chat application enabling interaction with locally hosted LLMs (Llama3, Phi3, Mistral) via Ollama.
*   **Project 2: Document Summarization** - A Python script leveraging Hugging Face's `transformers` library for efficient document summarization.
*   **Project 3: Global News Tracker** - An application that scrapes news, extracts keywords using a local LLM, and clusters articles for trend analysis, presented through a Streamlit interface.
*   **Project 4: Multimodal Applications** - Demonstrates the multimodal capabilities of LLMs by generating descriptions for images using OpenAI's GPT-4o.
*   **Project 5: Meeting Note Taker** - A Streamlit application that transcribes audio meetings using OpenAI Whisper and summarizes discussions, extracting action items with GPT-4.
*   **Project 6: Custom Chatbot** - A Retrieval Augmented Generation (RAG) chatbot built with Streamlit, LangChain, and ChromaDB, allowing users to chat with their own documents using local LLMs.

Each project directory contains a dedicated `readme.md` with more detailed information on its purpose, how to run it, the techniques used, and potential issues.

## Setup and Installation

To run these projects, you will generally need:

*   Python 3.9+
*   `pip` for package management
*   `git` for cloning the repository

**General Steps:**

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/AI_Portfolio.git
    cd AI_Portfolio
    ```
2.  **Navigate to a project directory:**
    ```bash
    cd project1_localllmChat # or any other project
    ```
3.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```
4.  **Install dependencies:**
    Each project has its own `requirements.txt` (or dependencies can be inferred from `app.py`).
    ```bash
    pip install -r requirements.txt # if available
    ```
5.  **Follow project-specific instructions** in their respective `readme.md` files.

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

## License

This project is open-source and available under the [MIT License](LICENSE).