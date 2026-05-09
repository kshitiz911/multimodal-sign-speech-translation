# Sign Language Recognition System (SLRS)

## Overview

The Sign Language Recognition System (SLRS) is a real-time AI-based communication platform designed to bridge the communication gap between hearing-impaired and non-sign-language users.

The system detects hand gestures using computer vision and deep learning techniques and converts recognized sign language gestures into speech output. The project also integrates speech-based interaction modules to create a more inclusive and accessible communication environment.

---

# Features

- Real-time Sign Language Detection
- Text-to-Speech (TTS) Output
- Speech Interaction Support
- YOLOv5-based Gesture Recognition
- Offline Execution Support
- Camera-based Live Detection
- Deep Learning Model Integration
- Lightweight and Fast Inference

---

# Technologies Used

- Python
- YOLOv5
- PyTorch
- OpenCV
- NumPy
- pyttsx3
- SpeechRecognition

---

# Project Structure

```bash
MP-SLG/
│
├── classify/
├── models/
│
├── best.pt
├── detect.py
├── export.py
├── speech_controller.py
│
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

# System Architecture

1. Camera captures hand gestures.
2. YOLOv5 model processes image frames.
3. Detected sign language gesture is classified.
4. Predicted label is converted into text.
5. Text is converted into speech output.

---

# Installation

## Step 1: Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
```

---

## Step 2: Open Project Folder

```bash
cd YOUR_REPOSITORY
```

---

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Running the Project

## Run Detection System

```bash
python detect.py --weights best.pt --source 0
```

---

# Model Information

- Model: YOLOv5
- Framework: PyTorch
- Task: Real-time Sign Language Recognition
- Training Type: Custom Dataset Training

---

# Dataset

The model was trained on a custom sign language gesture dataset consisting of labeled hand gesture images.

---

# Applications

- Communication Assistance
- Accessibility Systems
- Smart Education Platforms
- Human-Computer Interaction
- Assistive AI Systems

---

# Future Scope

- Sentence Formation
- Multi-language Speech Output
- Mobile Application Deployment
- Cloud Integration
- Advanced NLP Integration
- Dynamic Gesture Recognition

---

# Advantages

- Real-time Performance
- Offline Functionality
- Low Latency
- User Friendly
- Assistive Technology Support

---

# Limitations

- Requires Proper Lighting
- Accuracy Depends on Hand Visibility
- Limited Gesture Vocabulary
- Camera Dependency

---

# Authors

Final Year Engineering Major Project

---

# License

This project is developed for educational and research purposes.