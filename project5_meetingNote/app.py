import streamlit as st
import whisper
import openai
import os
from dotenv import load_dotenv
import re

load_dotenv()
"""
For pre-recorded audio files(Start)
"""
# 2. Transcribe audio file into text using whisper
def transcribe_audio(file_path):
    model = whisper.load_model("base")
    result = model.transcribe(file_path)
    return result["text"]

# 3. Clean up redundent words like um, uh, like, you know, so from the transcription
def clean_transcript(text):
    text = re.sub(r"\b(um+|uh+|like|you know|so)\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()

st.title("Meeting Notes & Action Item Extractor")

# 1. Upload audio file to service.
audio_file = st.file_uploader("Upload your meeting audio", type=["mp3", "wav", "m4a"])

if audio_file:
    st.audio(audio_file, format="audio/wav")
    with open("temp_audio.mp3", "wb") as f:
        f.write(audio_file.read())
    st.success("Audio uploaded successfully!")
    transcript = transcribe_audio("temp_audio.mp3")
    transcript = clean_transcript(transcript)
    os.remove("temp_audio.mp3")
    st.subheader("Transcript")
    st.text_area("Full Transcript", transcript, height=300)
"""
For pre-recorded audio files(End)
"""

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_summary_and_action(transcript):
    prompt = f"""You are a smart assistant. Given this meeting transcript, generate:
        1. A brief summary of the discussion.
        2. A bulleted list of clear action items.
        Transcript:
        {transcript}
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content
# 4. Extract action items from the transcript
if st.button("Summarize & Extract Tasks"):
    summary = extract_summary_and_action(transcript)
    st.subheader("Meeting Summary & Action Items")
    st.markdown(summary)