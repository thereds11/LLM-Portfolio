import streamlit as st
import sounddevice as sd
import numpy as np
import queue
import threading
import tempfile
from faster_whisper import WhisperModel

st.set_page_config(page_title="Live Transcription", layout="wide")
st.title("🎙️ Live Meeting Transcription")

q = queue.Queue()

model = WhisperModel("medium", compute_type="float32")

transcript_lines = []

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

def run_recorder():
    with sd.InputStream(samplerate=16000, channels=1, callback=audio_callback):
        while st.session_state["listening"]:
            if not q.empty():
                chink = q.get()
                temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                np.save(temp_wav, chink)
                temp_wav.close()
                segments, _ = model.transcribe(temp_wav.name, beam_size=5)
                for segment in segments:
                    text = segment.text.strip()
                    if text:
                        transcript_lines.append(f"You: {text}")
                        st.session_state["transcritp"] = transcript_lines

# UI
if "listening" not in st.session_state:
    st.session_state["listening"] = False
    st.session_state["transcript"] = []

if st.button("🎤 Start Listening"):
    st.session_state["listening"] = True
    thread = threading.Thread(target=run_recorder)
    thread.start()

if st.button("⏹️ Stop Listening"):
    st.session_state["listening"] = False

# Display transcript
st.subheader("Transcript")
for line in st.session_state["transcript"]:
    st.markdown(f"• {line}")