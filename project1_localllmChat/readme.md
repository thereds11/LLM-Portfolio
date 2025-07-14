# Project 1: Local LLM Chat

This project implements a simple chat application using Streamlit, allowing users to interact with various locally hosted Large Language Models (LLMs) via Ollama. It demonstrates how to integrate local LLMs into a user-friendly interface for conversational AI.

## Purpose

The primary goal of this project is to provide a straightforward way to experiment with and utilize local LLMs without relying on external API services. It showcases the capabilities of Ollama for serving models like Llama3, Phi3, and Mistral, and how to build a basic chat interface around them.

## How to Run

1.  **Install Ollama:**
    Download and install Ollama from [ollama.com](https://ollama.com/).
2.  **Download LLM Models:**
    Pull the desired models using Ollama. For example:
    ```bash
    ollama pull llama3
    ollama pull phi3
    ollama pull mistral
    ```
3.  **Navigate to the project directory:**
    ```bash
    cd D:/Sirius/projects/AI_Portfolio/project1_localllmChat
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
    pip install streamlit llama-index-llms-ollama
    ```
    *(Note: A `requirements.txt` is not provided in this specific project, so these are the core dependencies based on `app.py`)*
6.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```
    This will open the application in your web browser.

## Techniques Used

*   **Streamlit:** Used for building the interactive web-based user interface.
*   **Ollama:** Serves as the local LLM runtime, providing an API to interact with various open-source models.
*   **LlamaIndex:** Utilized for its `Ollama` LLM integration and `ChatMessage` handling for conversational turns.
*   **Streaming Responses:** The application streams responses from the LLM for a better user experience.

## Issues and Considerations

*   **Performance:** The performance of the chat application is highly dependent on your local hardware (CPU, RAM) and the size/complexity of the chosen LLM.
*   **Ollama Setup:** Ensure Ollama is running and the required models are pulled before starting the application.
*   **Model Availability:** The list of models in the sidebar (`llama3`, `phi3`, `mistral`) assumes these models are available via your Ollama instance.

## Contributions

Feel free to contribute to this project by opening issues or submitting pull requests.
