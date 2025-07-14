# Project 3: Global News Tracker

This project is a comprehensive news tracking and analysis application. It scrapes news headlines and snippets from Google News, extracts relevant keywords using a local LLM (Llama3 via Ollama), and then clusters the news articles to identify trending topics. The results are presented through an interactive Streamlit dashboard.

## Purpose

The aim of this project is to demonstrate an end-to-end pipeline for news aggregation, natural language processing (NLP) with local LLMs, and data visualization. It provides insights into current events by grouping similar news articles and highlighting key themes.

## How to Run

1.  **Install Ollama:**
    Download and install Ollama from [ollama.com](https://ollama.com/).
2.  **Download LLM Model:**
    Pull the `llama3` model for keyword extraction and summarization:
    ```bash
    ollama pull llama3
    ```
3.  **Navigate to the project directory:**
    ```bash
    cd D:/Sirius/projects/AI_Portfolio/project3_globalnewtracker
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
    pip install requests beautifulsoup4 pandas ollama scikit-learn sentence-transformers streamlit
    ```
    *(Note: A `requirements.txt` is not provided in this specific project, so these are the core dependencies based on `app.py` and `streamlit_app.py`)*
6.  **Fetch News Data:**
    Run the `app.py` script to scrape news and generate `news_data.csv`. This step uses Ollama for keyword extraction.
    ```bash
    python app.py
    ```
    *(You might need to modify the `getNewsData` call at the end of `app.py` to specify a query, e.g., `getNewsData("AI")`)*
7.  **Run the Streamlit application:**
    ```bash
    streamlit run streamlit_app.py
    ```
    This will open the interactive news dashboard in your web browser.

## Techniques Used

*   **Web Scraping:** `requests` and `BeautifulSoup4` are used to extract news information from Google News.
*   **Local LLM (Ollama):** `llama3` is used via Ollama for extracting relevant keywords from news headlines and snippets.
*   **Sentence Embeddings:** `SentenceTransformer` (`all-MiniLM-L6-v2`) is used to convert news article text into numerical vectors.
*   **Clustering:** `KMeans` algorithm from `scikit-learn` is applied to group similar news articles based on their embeddings.
*   **Streamlit:** Provides an intuitive and interactive user interface for displaying clustered news and allowing users to fetch new data.
*   **Caching:** Streamlit's `@st.cache_resource` and `@st.cache_data` are used to optimize performance by caching model loading and data processing.

## Issues and Considerations

*   **Google News Rate Limiting:** Frequent scraping might lead to temporary blocks from Google News.
*   **Ollama Setup:** Ensure Ollama is running and the `llama3` model is pulled before running the scripts.
*   **Keyword Extraction Quality:** The quality of extracted keywords depends on the LLM's performance and the prompt engineering.
*   **Clustering Quality:** The effectiveness of clustering depends on the embedding model and the chosen number of clusters (`k`).
*   **Data Persistence:** News data is saved to `news_data.csv`. If you want to fetch new data, you need to run `app.py` again or use the "Fetch Latest News" button in the Streamlit app.

## Contributions

Feel free to contribute to this project by opening issues or submitting pull requests.
