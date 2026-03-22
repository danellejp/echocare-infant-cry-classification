# 🍼 EchoCare - Infant Cry Monitoring System (Backend)
EchoCare is an accessibility-focused system that uses deep learning to detect and classify infant cries in real-time, providing support for deaf and hard-of-hearing parents and caregivers.

- 🎓 Final Year Project: - TU Dublin (TU856)
- 👩‍💻 Student: Danelle Pillay (C22348731)  

## 📖 Project Overview
EchoCare is designed to help deaf or hard-of-hearing parents better understand their baby's needs by detecting and classifying infant cries into categories (Hungry, Pain, Normal) using CNN-based deep learning. The system runs entirely on a Raspberry Pi with no cloud dependency. All processing happens locally for maximum privacy, security and sustainability.

<img width="410" height="585" alt="image" src="https://github.com/user-attachments/assets/8ada6c03-f00a-48b0-b8e0-5f8b7434e349" />

## 📱 Features
- 🧠 Infant Cry Detection and Classification Using Machine Learning
- 📊 Models Trained on Clinically Verified Data
- 🔄 Continuous Monitoring via the Raspberry Pi-Based System
- 📱 Real-Time Notifications with Haptic Feedback
- 💡 LED Visual Indicators for Nighttime Use
- 🌡️ Real-Time Temperature and Humidity Monitoring
- 📈 Analytics Dashboard with Cry Statistics and Pattern Tracking
- 📋 Downloadable Cry Analytics Reports for Sharing Cry Patterns with Healthcare Professionals
- 🔒 Edge Computing Architecture allows for Maximum Privacy, Security and Sustainability

## 🛠️ Tech Stack
- **Hardware**: Raspberry Pi 4, USB Microphone, DHT22 Temperature Sensor, Grove RGB LED
- **ML Framework**: Keras, TensorFlow Lite, CNN
- **Backend**: Python, FastAPI, SQLite
- **Frontend**: Kotlin (Native Android)
- **Communication**: UDP Broadcasting, HTTP REST API

## 🔗 Related Repositories
📱 Frontend (Android App): https://github.com/danellejp/EchoCare-Android/

## 🚀 Setup Instructions

### Prerequisites
- Raspberry Pi 4 (with Raspberry Pi OS)
- USB Microphone
- DHT22 Temperature & Humidity Sensor
- Grove Chainable RGB LED Module
- Python 3.11+
- Android Phone (for EchoCare app)

1) Clone EchoCare Backend onto Raspberry Pi: https://github.com/danellejp/echocare-infant-cry-classification
2) Install necessary dependencies onto Pi: See requirements.txt
3) Clone EchoCare FrontEnd on Laptop: https://github.com/danellejp/EchoCare-Android/
4) Configure Raspberry Pi 4 with necessary hardware: USB Microphone, DHT22 Temperature Sensor, Grove RGB LED
5) Configure Pi as WiFi Access Point so the Android app can communicate directly with the Pi
6) Enable Auto-Start - Configure systemd services so the api_server.py and echocare_system.py start automatically when the Pi is powered on
7) Build and install the Android app onto phone via Android Studio

## ▶️ How to Operate
1) Plug in the Pi's power supply - EchoCare_Network WiFi starts automatically. Both scripts start automatically - API server and monitoring system launch via systemd
2) Connect your phone to the EchoCare_Network WiFi
3) Open the EchoCare app - tap "Start Monitoring" then allow notifications. EchoCare is now monitoring.

## Acknowledgements
- Baby Chillanto Dataset: National Institute of Astrophysics and Optical Electronics, CONACYT, Mexico.
- TU Dublin: Department of Computer Science
- Project Supervisor: Stephen O'Sullivan
