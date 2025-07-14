# Project 5: Meeting Note Taker

This project is a Streamlit application designed to assist in meeting management by transcribing audio recordings and then summarizing the discussion and extracting actionable items using advanced Large Language Models.

## Purpose

The primary goal is to automate the tedious process of manually taking meeting notes and identifying key takeaways. It leverages speech-to-text technology and powerful LLMs to provide concise summaries and clear action item lists, improving productivity and record-keeping.

## How to Run

1.  **Obtain an OpenAI API Key:**
    You need an OpenAI API key with access to GPT-4. You can get one from the [OpenAI Platform](https://platform.openai.com/).
2.  **Set your API Key:**
    Create a `.env` file in the project root (`D:/Sirius/projects/AI_Portfolio/project5_meetingNote/.env`) and add your OpenAI API key:
    ```
    OPENAI_API_KEY="your_openai_api_key_here"
    ```
3.  **Navigate to the project directory:**
    ```bash
    cd D:/Sirius/projects/AI_Portfolio/project5_meetingNote
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
    pip install streamlit openai-whisper openai python-dotenv
    ```
    *(Note: A `requirements.txt` is not provided in this specific project, so these are the core dependencies based on `app.py`)*
6.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```
    This will open the application in your web browser. You can then upload an audio file (MP3, WAV, M4A) for transcription and analysis.

## Techniques Used

*   **Streamlit:** Used for building the interactive web-based user interface, allowing easy audio file uploads and display of results.
*   **OpenAI Whisper:** A robust speech-to-text model used for transcribing audio recordings into text. The `base` model is loaded locally.
*   **OpenAI API (GPT-4):** Utilized for its advanced natural language understanding capabilities to:
    *   Summarize the transcribed meeting discussion.
    *   Extract a bulleted list of clear action items from the transcript.
*   **`python-dotenv`:** For securely loading API keys from a `.env` file, preventing them from being hardcoded.
*   **Regular Expressions (`re`):** Used for cleaning up the transcribed text by removing common filler words (e.g., "um", "uh", "like").

## Issues and Considerations

*   **API Key Management:** Ensure your OpenAI API key is kept secure and not exposed in public repositories. Using `.env` is a good practice.
*   **API Costs:** Using OpenAI's GPT-4 and Whisper APIs incurs costs based on usage (token usage for GPT-4, audio duration for Whisper).
*   **Audio File Size:** Large audio files will take longer to transcribe and process. Consider potential limitations of the Whisper model and API.
*   **Transcription Accuracy:** The accuracy of the transcription depends on audio quality, background noise, and speaker clarity.
*   **Summarization Quality:** The quality of the summary and action items depends on the clarity of the meeting discussion and the prompt engineering for GPT-4.
*   **Local Whisper Model:** The `base` Whisper model is downloaded and loaded locally. Larger models (e.g., `large`) offer better accuracy but require more resources.

## Contributions

Feel free to contribute to this project by opening issues or submitting pull requests.
