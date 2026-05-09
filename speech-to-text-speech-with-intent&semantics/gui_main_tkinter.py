import threading
import queue
import time
import sys
from collections import Counter
import traceback

import json
import random

import numpy as np
import sounddevice as sd  # type: ignore[reportMissingModuleSource]
from faster_whisper import WhisperModel

import tkinter as tk
from tkinter import scrolledtext

import win32com.client  # type: ignore[reportMissingModuleSource]
import pythoncom  # type: ignore[reportMissingModuleSource]

# =======================
# Load from JSON
# =======================
with open("intents.json") as f:
    INTENT_KEYWORDS = json.load(f)

with open("responses.json") as f:
    AUDIO_RESPONSES = json.load(f)


# =======================
# Configuration (same as main.py)
# =======================
samplerate = 16000
block_duration = 0.5
chunk_duration = 5
channels = 1

frames_per_block = int(samplerate * block_duration)
frames_per_chunk = int(samplerate * chunk_duration)


# =======================
# Globals (mirroring main.py backend)
# =======================
running = False
intent_counter = Counter()

audio_queue: "queue.Queue[np.ndarray]" = queue.Queue()
audio_buffer: list[np.ndarray] = []

tts_queue: "queue.Queue[str | None]" = queue.Queue()


# =======================
# Models (same config as main.py)
# =======================
print("Loading Whisper model (small, int8, CPU)...", file=sys.stderr)
whisper_model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8",
)
print("Whisper model loaded.", file=sys.stderr)

print("Loading sentiment analyzer...", file=sys.stderr)
from nltk.sentiment import SentimentIntensityAnalyzer

sentiment_analyzer = SentimentIntensityAnalyzer()
print("Sentiment analyzer ready.", file=sys.stderr)



# =======================
# Utilities (same logic as main.py)
# =======================
def detect_intent(text: str) -> str:
    text_l = text.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw in text_l:
                return intent
    return "Statement"


def get_sentiment_with_confidence(text: str):
    scores = sentiment_analyzer.polarity_scores(text)
    compound = scores["compound"]
    if compound >= 0.05:
        sentiment = "Positive"
    elif compound <= -0.05:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    confidence = round(abs(compound) * 100, 2)
    return sentiment, confidence


def select_audio_response(intent, sentiment):
    # Intent priority
    if intent in AUDIO_RESPONSES:
        return random.choice(AUDIO_RESPONSES[intent])

    # Sentiment fallback
    if sentiment in AUDIO_RESPONSES:
        return random.choice(AUDIO_RESPONSES[sentiment])

    return random.choice(AUDIO_RESPONSES["Neutral"])

# =======================
# TTS worker (same pattern as main.py)
# =======================
def tts_worker():
    pythoncom.CoInitialize()
    try:
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        while True:
            text = tts_queue.get()
            if text is None:
                break
            try:
                speaker.Speak(text)
            except Exception:
                traceback.print_exc()
            tts_queue.task_done()
    finally:
        pythoncom.CoUninitialize()


def speak_response(text: str):
    tts_queue.put(text)


# =======================
# Audio callback & recorder (same logic)
# =======================
def audio_callback(indata, frames, time_info, status):
    if status:
        print(f"[Audio Status] {status}")
    audio_queue.put(indata.copy())


def recorder_loop():
    with sd.InputStream(
        samplerate=samplerate,
        channels=channels,
        callback=audio_callback,
        blocksize=frames_per_block,
    ):
        while running:
            sd.sleep(100)


# =======================
# GUI Application built on top of same backend logic
# =======================
class SpeechAssistantGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Real-Time Speech Assistant (main.py backend)")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Backend control
        self.recorder_thread: threading.Thread | None = None
        self.transcriber_thread: threading.Thread | None = None
        self.tts_thread: threading.Thread | None = None

        self._build_ui()

    # ---------- UI ----------
    def _build_ui(self):
        status_frame = tk.Frame(self.root)
        status_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(status_frame, text="Status:").pack(side="left")
        self.status_var = tk.StringVar(value="Idle")
        tk.Label(status_frame, textvariable=self.status_var, fg="blue").pack(side="left", padx=5)

        intent_frame = tk.Frame(self.root)
        intent_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(intent_frame, text="Intent:").pack(side="left")
        self.intent_var = tk.StringVar(value="N/A")
        tk.Label(intent_frame, textvariable=self.intent_var).pack(side="left", padx=5)

        sentiment_frame = tk.Frame(self.root)
        sentiment_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(sentiment_frame, text="Sentiment:").pack(side="left")
        self.sentiment_var = tk.StringVar(value="N/A")
        tk.Label(sentiment_frame, textvariable=self.sentiment_var).pack(side="left", padx=5)

        user_frame = tk.LabelFrame(self.root, text="User Said")
        user_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.user_text = scrolledtext.ScrolledText(user_frame, height=5, wrap="word", state="disabled")
        self.user_text.pack(fill="both", expand=True, padx=5, pady=5)

        system_frame = tk.LabelFrame(self.root, text="System Said")
        system_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.system_text = scrolledtext.ScrolledText(system_frame, height=5, wrap="word", state="disabled")
        self.system_text.pack(fill="both", expand=True, padx=5, pady=5)

        button_frame = tk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=10)

        tk.Button(button_frame, text="Start", command=self.start, width=10).pack(side="left", padx=5)
        tk.Button(button_frame, text="Stop", command=self.stop, width=10).pack(side="left", padx=5)
        tk.Button(button_frame, text="Restart", command=self.restart, width=10).pack(side="left", padx=5)

    # ---------- Safe UI helpers ----------
    def _set_status(self, text: str):
        self.root.after(0, lambda: self.status_var.set(text))

    def _set_intent(self, text: str):
        self.root.after(0, lambda: self.intent_var.set(text))

    def _set_sentiment(self, text: str):
        self.root.after(0, lambda: self.sentiment_var.set(text))

    def _set_user_said(self, text: str):
        def _u():
            self.user_text.config(state="normal")
            self.user_text.delete("1.0", tk.END)
            self.user_text.insert(tk.END, text)
            self.user_text.config(state="disabled")

        self.root.after(0, _u)

    def _set_system_said(self, text: str):
        def _u():
            self.system_text.config(state="normal")
            self.system_text.delete("1.0", tk.END)
            self.system_text.insert(tk.END, text)
            self.system_text.config(state="disabled")

        self.root.after(0, _u)

    # ---------- Control ----------
    def start(self):
        global running
        if running:
            return

        running = True
        self._set_status("Listening")

        # TTS worker (only start once)
        if self.tts_thread is None or not self.tts_thread.is_alive():
            self.tts_thread = threading.Thread(target=tts_worker, daemon=True)
            self.tts_thread.start()

        # Recorder
        self.recorder_thread = threading.Thread(target=recorder_loop, daemon=True)
        self.recorder_thread.start()

        # Transcriber
        self.transcriber_thread = threading.Thread(target=self._transcriber_loop_gui, daemon=True)
        self.transcriber_thread.start()

    def stop(self):
        global running
        if not running:
            return
        running = False
        self._set_status("Stopping...")

        # signal TTS thread to exit eventually (optional)
        tts_queue.put(None)

        # Join threads in background so GUI doesn't freeze
        def _join():
            for th in [self.recorder_thread, self.transcriber_thread]:
                try:
                    if th is not None:
                        th.join(timeout=2.0)
                except Exception:
                    pass
            self._set_status("Idle")

        threading.Thread(target=_join, daemon=True).start()

    def restart(self):
        self.stop()
        self._set_user_said("")
        self._set_system_said("")
        self._set_intent("N/A")
        self._set_sentiment("N/A")

        def _do_start():
            if not running:
                self.start()
            else:
                self.root.after(200, _do_start)

        self.root.after(300, _do_start)

    # ---------- Transcriber loop (same core logic as main.py, but with UI updates) ----------
    def _transcriber_loop_gui(self):
        global audio_buffer
        while running:
            try:
                block = audio_queue.get(timeout=1)
            except queue.Empty:
                continue

            audio_buffer.append(block)
            total_frames = sum(len(b) for b in audio_buffer)
            if total_frames < frames_per_chunk:
                continue

            full = np.concatenate(audio_buffer)
            chunk = full[:frames_per_chunk]
            remaining = full[frames_per_chunk:]
            audio_buffer = [remaining] if len(remaining) > 0 else []

            audio_data = chunk.flatten().astype(np.float32)

            # Energy check (same as main.py)
            if np.abs(audio_data).mean() < 0.001:
                continue

            self._set_status("Processing")
            try:
                segments, _ = whisper_model.transcribe(
                    audio_data,
                    language="en",
                    beam_size=5,
                )

                for segment in segments:
                    text = segment.text.strip()
                    if len(text.split()) < 3:
                        continue

                    intent = detect_intent(text)
                    sentiment, confidence = get_sentiment_with_confidence(text)
                    intent_counter[intent] += 1

                    # For Command intents, speak the actual command text via TTS.
                    if intent == "Command":
                        system_text = text
                        speak_response(system_text)
                    else:
                        system_text = select_audio_response(intent, sentiment)
                        speak_response(system_text)

                    # Update GUI instead of only printing
                    self._set_user_said(f"\"{text}\"")
                    self._set_intent(intent)
                    self._set_sentiment(f"{sentiment} ({confidence}%)")
                    self._set_system_said(system_text)

            except Exception:
                traceback.print_exc()

            self._set_status("Listening")

    # ---------- Shutdown ----------
    def on_close(self):
        self.stop()
        # Small delay for threads to wind down
        time.sleep(0.5)
        self.root.destroy()


def main():
    root = tk.Tk()
    app = SpeechAssistantGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

