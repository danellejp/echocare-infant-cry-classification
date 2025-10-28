# EchoCare: Infant Cry Detection System

An audio-based system that uses deep learning to detect and classify infant cries in real-time.

**Final Year Project - TU Dublin (TU856)**  
**Student**: Danelle Pillay (C22348731)  

## Project Overview
EchoCare is designed to help first-time parents/caregivers and deaf or hard-of-hearing individuals better understand their baby's needs by classifying infant cries into categories (hungry, discomfort) using CNN-based deep learning.

## Features
- Real-time cry detection and classification
- Raspberry Pi-based monitoring system
- Native Android mobile app with push notifications
- Temperature monitoring via DHT22 sensor
- LED visual indicators for accessibility
- Dashboard with cry statistics and patterns

## Tech Stack
- **Hardware**: Raspberry Pi 4, USB Microphone, DHT22 Temperature Sensor, RGB LED Module
- **ML Framework**: TensorFlow/TensorFlow Lite, CNN
- **Backend**: Python, FastAPI, SQLite
- **Frontend**: Kotlin (Native Android)
- **Communication**: UDP Broadcasting, HTTP REST API

## Project Structure

├── model/             # CNN model training and evaluation
├── raspberry-pi/      # Pi backend, API server, sensors
├── android-app/       # Native Android application
└── datasets/          # Dataset information and preprocessing


## Current Status
🚧 **In Development**

## Setup Instructions
Coming soon...

