# Project 2: Document Summarization

This project provides a Python script for summarizing long text documents using a pre-trained summarization model from the Hugging Face `transformers` library. Specifically, it utilizes the `facebook/bart-large-cnn` model, which is well-suited for abstractive summarization tasks.

## Purpose

The main purpose of this project is to demonstrate how to leverage state-of-the-art pre-trained models for text summarization. It offers a simple, command-line based tool to quickly generate concise summaries of lengthy articles or documents.

## How to Run

1.  **Navigate to the project directory:**
    ```bash
    cd D:/Sirius/projects/AI_Portfolio/project2_documentSumm
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install transformers torch
    ```
    *(Note: A `requirements.txt` is not provided in this specific project, so these are the core dependencies based on `app.py`)*
4.  **Run the summarization script:**
    ```bash
    python app.py
    ```
    The `app.py` script contains a predefined text for summarization. You can modify the `text` variable within `app.py` to summarize your own content.

## Techniques Used

*   **Hugging Face Transformers:** The core library used for accessing and utilizing pre-trained NLP models.
*   **`pipeline` API:** Simplifies the process of using models for specific tasks like summarization.
*   **`facebook/bart-large-cnn`:** A BART-based model fine-tuned for abstractive summarization on CNN/DailyMail dataset.
*   **CUDA (GPU) Support:** The script includes logic to detect and utilize a CUDA-enabled GPU if available, significantly speeding up inference.

## Issues and Considerations

*   **Model Size:** `bart-large-cnn` is a relatively large model, requiring a decent amount of RAM.
*   **GPU Requirement:** While it runs on CPU, using a GPU is highly recommended for faster summarization, especially for longer texts.
*   **Summarization Quality:** The quality of the summary depends on the input text and the model's training data. Fine-tuning might be necessary for domain-specific summarization.
*   **Input Length:** Transformer models have input token limits. Very long documents might need to be chunked before summarization.

## Contributions

Feel free to contribute to this project by opening issues or submitting pull requests.
