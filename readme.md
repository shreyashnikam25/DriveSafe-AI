# DriveSafe – Driver Drowsiness Detection System

A computer vision-based driver monitoring system designed to detect signs of driver drowsiness in real time using facial landmarks and eye movement analysis.

## Overview

DriveSafe uses computer vision and deep learning techniques to monitor driver alertness and identify potential signs of fatigue. The system analyzes facial landmarks and calculates the Eye Aspect Ratio (EAR) to distinguish between alert and drowsy states.

## Features

- **Real-Time Drowsiness Detection:** Monitors eye movements and detects prolonged eye closure.
- **Facial Landmark Analysis:** Uses MediaPipe to track facial landmarks.
- **Eye Aspect Ratio (EAR):** Applies EAR-based thresholding to identify potential drowsiness.
- **Consecutive-Frame Analysis:** Reduces false alerts by considering eye closure across multiple frames.
- **Computer Vision Integration:** Uses OpenCV for video capture and frame processing.
- **YOLOv8 Integration:** Supports object detection for driver and road monitoring applications.
- **Web Interface:** Includes a Next.js-based frontend for system interaction.

## Tech Stack

- **Programming Language:** Python
- **Computer Vision:** OpenCV, MediaPipe
- **Object Detection:** YOLOv8
- **Deep Learning:** PyTorch
- **Frontend:** Next.js, Tailwind CSS

## How It Works

1. **Video Input:** Captures video frames from the camera.
2. **Facial Landmark Detection:** Identifies relevant facial landmarks.
3. **EAR Calculation:** Calculates the Eye Aspect Ratio using eye landmark coordinates.
4. **Drowsiness Classification:** Compares the EAR against a configured threshold.
5. **Alert Detection:** Uses consecutive low-EAR frames to identify prolonged eye closure.
6. **Output:** Displays the detected driver state through the application interface.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/shreyashnikam25/DriveSafe-AI.git
cd DriveSafe-AI
```

### 2. Set Up the Python Environment

```bash
python -m venv venv
```

Activate the environment on Windows:

```bash
venv\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### 3. Run the Application

Run the Python detection script using the entry-point filename configured in your repository.

```bash
python your_script.py
```

Replace `your_script.py` with the actual Python script name. Follow the frontend setup instructions in the repository if you want to launch the web interface.

## Project Structure

```text
DriveSafe-AI/
├── frontend/          # Next.js frontend
├── models/            # Model files, if included
├── requirements.txt   # Python dependencies
├── README.md
└── ...
```

*The directory structure may vary depending on the current implementation.*

## Future Improvements

- Integrate additional driver-monitoring signals such as head pose.
- Improve robustness under varying lighting conditions.
- Expand road-scene monitoring with lane detection and object detection.
- Evaluate performance across different drivers and real-world conditions.

## Disclaimer

DriveSafe is an educational and development project intended for driver-monitoring research and experimentation. It is not a substitute for certified automotive safety systems and should not be relied upon as the sole means of preventing accidents.
