# Speech to Text Conversion WITH Sentiment + Intent Detection

import sounddevice as sd
import numpy as np
import queue
import threading
import signal
import sys
import nltk

from faster_whisper import WhisperModel
from nltk.sentiment import SentimentIntensityAnalyzer

# =======================
# Globals
# =======================
running: bool = True
whisper_model: WhisperModel

# =======================
# Configuration
# =======================
samplerate = 16000
block_duration = 0.5
chunk_duration = 5
channels = 1

frames_per_block = int(samplerate * block_duration)
frames_per_chunk = int(samplerate * chunk_duration)

audio_queue = queue.Queue()
audio_buffer = []

# =======================
# Models
# =======================
whisper_model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)

sentiment_analyzer = SentimentIntensityAnalyzer()

# =======================
# Intent Keywords
# =======================
INTENT_KEYWORDS = {
    "Help_Request": ["help", "assist", "support", "emergency", "please help"],
    "Question": ["what", "why", "how", "when", "where", "who"],
    "Command": ["turn", "open", "close", "start", "stop", "call"],
    "Greeting": ["hello", "hi", "good morning", "good evening"],
    "Gratitude": ["thank you", "thanks"]
}

# =======================
# Utilities
# =======================
def get_sentiment(text: str) -> str:
    scores = sentiment_analyzer.polarity_scores(text)
    compound = scores["compound"]

    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    else:
        return "Neutral"


def detect_intent(text: str) -> str:
    text = text.lower()

    for intent, keywords in INTENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return intent

    return "Statement"

# =======================
# Signal Handling
# =======================
def signal_handler(sig, frame):
    global running
    print("\nStopping transcription...")
    running = False
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# =======================
# Audio Callback
# =======================
def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    audio_queue.put(indata.copy())

# =======================
# Recorder Thread
# =======================
def recorder():
    global running
    with sd.InputStream(
        samplerate=samplerate,
        channels=channels,
        callback=audio_callback,
        blocksize=frames_per_block
    ):
        print("Listening... Press Ctrl+C to stop.")
        while running:
            sd.sleep(100)

# =======================
# Transcriber Loop
# =======================
def transcriber():
    global audio_buffer, whisper_model, running

    while running:
        block = audio_queue.get()
        audio_buffer.append(block)

        total_frames = sum(len(b) for b in audio_buffer)
        if total_frames < frames_per_chunk:
            continue

        audio_data = np.concatenate(audio_buffer)[:frames_per_chunk]
        audio_buffer = []

        audio_data = audio_data.flatten().astype(np.float32)

        segments, _ = whisper_model.transcribe(
            audio_data,
            language="en",
            beam_size=5
        )

        for segment in segments:
            text = segment.text.strip()
            if len(text.split()) < 3:
                continue

            intent = detect_intent(text)
            sentiment = get_sentiment(text)

            print("\n-----------------------------")
            print(f"Text      : {text}")
            print(f"Intent    : {intent}")
            print(f"Sentiment : {sentiment}")

# =======================
# Start
# =======================
threading.Thread(target=recorder, daemon=True).start()
transcriber()