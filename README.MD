# Real-Time Multimodal Speech and Sign Language Translation System with Semantic and Intent Analysis Using YOLOv5

## Overview

The Real-Time Multimodal Speech and Sign Language Translation System is an AI-powered assistive communication platform designed to bridge communication gaps between hearing-impaired, speech-impaired, and non-disabled individuals.

The system combines two major communication modules:

1. Sign Language Recognition to Speech Conversion
2. Speech-to-Text-to-Speech with Semantic and Intent Analysis

The project utilizes Computer Vision, Deep Learning, Natural Language Processing (NLP), and Speech Processing techniques to enable seamless real-time multimodal interaction.

---

# Objectives

- Enable real-time sign language communication
- Convert speech into meaningful textual responses
- Perform semantic and intent analysis on speech input
- Provide accessible communication support
- Develop a fully offline-capable assistive AI system

---

# Key Features

## Module 1 — Sign Language Recognition System

- Real-time hand gesture detection
- YOLOv5-based gesture recognition
- Camera-based live inference
- Sign-to-text conversion
- Text-to-Speech (TTS) output
- Offline execution support

---

## Module 2 — Speech-to-Text-to-Speech System

- Voice input recognition
- Speech-to-Text conversion
- Intent classification
- Semantic analysis
- AI-generated contextual responses
- Text-to-Speech response generation
- Multi-language speech handling support

---

# Technologies Used

## Programming Languages

- Python

---

## Frameworks & Libraries

- YOLOv5
- PyTorch
- OpenCV
- NumPy
- pyttsx3
- SpeechRecognition
- Transformers
- Scikit-learn
- Torchvision

---

# System Architecture

## Module 1 Workflow

1. Camera captures live hand gestures
2. YOLOv5 model processes image frames
3. Gesture is classified
4. Detected sign converted into text
5. Text converted into speech output

---

## Module 2 Workflow

1. Microphone captures speech input
2. Speech converted into text
3. NLP-based semantic analysis performed
4. Intent detection executed
5. Response generated
6. Text converted into speech

---

# Project Structure

```bash
MP-SLG/
│
├── classify/
├── models/
├── utils/
│
├── best.pt
├── detect.py
├── export.py
├── speech_controller.py
├── run.py
├── capture_image.py
│
├── requirements.txt
├── pyproject.toml
├── README.md
└── .gitignore
```

---

# Installation

## Step 1 — Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
```

---

## Step 2 — Navigate to Project Folder

```bash
cd YOUR_REPOSITORY
```

---

## Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Running the Project

## Run Sign Language Detection Module

```bash
python detect.py --weights best.pt --source 0
```

---

## Run Speech Processing Module

```bash
python speech_controller.py
```

---

# Model Information

## Sign Language Detection Model

- Model: YOLOv5
- Framework: PyTorch
- Task: Real-Time Gesture Detection
- Type: Custom Trained Object Detection Model

---

# Applications

- Assistive Communication Systems
- Accessibility Platforms
- Smart Education Systems
- Human-Computer Interaction
- Inclusive AI Systems
- Healthcare Assistance

---

# Advantages

- Real-time communication
- Offline functionality
- Lightweight deployment
- Fast inference speed
- Accessible interface
- Multimodal interaction support

---

# Limitations

- Accuracy affected by lighting conditions
- Requires proper hand visibility
- Limited gesture vocabulary
- Background noise may affect speech recognition
- Camera dependency

---

# Future Scope

- Dynamic sentence generation
- Mobile application deployment
- Cloud synchronization
- Advanced multilingual support
- Improved NLP integration
- Continuous gesture recognition
- Emotion and sentiment analysis

---

# Dataset

The project uses custom-trained datasets for:
- Sign language gesture recognition
- Speech intent classification

---

# Research Domains

- Computer Vision
- Deep Learning
- Natural Language Processing
- Human-Computer Interaction
- Assistive Artificial Intelligence

---

# Authors

Final Year Engineering Major Project

---

# License

This project is developed for educational and research purposes only.