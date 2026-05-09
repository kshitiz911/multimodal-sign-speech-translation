import time
import atexit
import threading
import pythoncom
import win32com.client
from collections import deque
from queue import Empty, Queue

class SpeechController:
    def __init__(self):
        self.last_label = None
        self.cooldown = 10
        self.min_conf = 0.20
        self.last_spoken_time = {}
        self.history = deque(maxlen=5)
        self._speech_queue = Queue()
        self._stop_event = threading.Event()
        self._speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self._speech_thread.start()
        atexit.register(self.shutdown)

        self.label_map = {
    "call": "Call",
    "dislike": "Dislike",
    "hello": "Hello",
    "iloveyou": "I love you",
    "like": "Like",
    "mute": "Mute",
    "ok": "Okay",
    "peace": "Peace",
    "stop": "Stop",
    "yes": "Yes"
        }

    def can_speak(self, label):
        now = time.time()
        if label not in self.last_spoken_time:
            return True
        return (now - self.last_spoken_time[label]) > self.cooldown

    def is_stable(self, label):
        # Reset history if label changes
        if self.last_label != label:
            self.history.clear()

        self.history.append(label)
        self.last_label = label
        
        return self.history.count(label) >= 3    
    

    def speak(self, text):
        self._speech_queue.put(text)

    def _create_voice(self):
        voice = win32com.client.Dispatch("SAPI.SpVoice")
        voice.Rate = 0
        return voice

    def _speech_worker(self):
        pythoncom.CoInitialize()
        voice = self._create_voice()

        try:
            while not self._stop_event.is_set():
                try:
                    text = self._speech_queue.get(timeout=0.1)
                except Empty:
                    continue

                try:
                    voice.Speak(text)
                except Exception as exc:
                    print(f"[TTS ERROR] {exc}")
                    voice = self._create_voice()
                finally:
                    self._speech_queue.task_done()
        finally:
            del voice
            pythoncom.CoUninitialize()

    def shutdown(self):
        if self._stop_event.is_set():
            return

        self._stop_event.set()
        self._speech_thread.join(timeout=1.0)

    def process(self, detections):
        if not detections:
            return
        
        # Step 1: Confidence filter
        detections = [d for d in detections if d[1] >= self.min_conf]
        if not detections:
            return

        # Step 2: Pick best prediction
        label, conf = max(detections, key=lambda x: x[1])

        # Step 3: Stability check
        if not self.is_stable(label):
            return

        # Step 4: Label mapping
        if label not in self.label_map:
            return
        
        # Step 5: Cooldown check
        if self.can_speak(label):
            print(f"[SPEAKING] {label} ({conf:.2f})")
            self.speak(self.label_map[label])
            self.last_spoken_time[label] = time.time()
