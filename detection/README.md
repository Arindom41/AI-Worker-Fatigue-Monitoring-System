AI Worker Fatigue Monitoring System

A real-time computer vision system for monitoring worker posture, ergonomic risk, and potential fatigue using YOLOv8 Pose, ByteTrack, and the Rapid Entire Body Assessment (REBA) methodology.

The system continuously detects workers from CCTV/live camera feeds, estimates body posture, calculates joint angles, evaluates ergonomic risk using REBA, and generates alerts when unsafe postures are maintained over time.

⸻

Features

* Real-time worker detection
* Multi-person tracking using ByteTrack
* Human pose estimation using YOLOv8 Pose
* Joint angle calculation
* Moving-average angle smoothing
* Official REBA posture assessment
* Time-based fatigue monitoring
* Worker-specific unique IDs
* Real-time ergonomic risk evaluation
* Live dashboard with worker status
* Automatic warning and alert generation
* Flask-based web interface
* Live camera and video file support

⸻

Project Workflow

Video / Live Camera
        │
        ▼
YOLOv8 Person Detection
        │
        ▼
ByteTrack Multi-Object Tracking
        │
        ▼
YOLOv8 Pose Estimation
        │
        ▼
Body Keypoint Extraction
        │
        ▼
Joint Angle Calculation
        │
        ▼
Moving Average Smoothing
        │
        ▼
REBA Scoring
        │
        ▼
Time-Based Activity Analysis
        │
        ▼
Fatigue Detection
        │
        ▼
Live Dashboard & Alerts

⸻

Technologies Used

Programming Language

* Python

Computer Vision

* OpenCV
* Ultralytics YOLOv8
* ByteTrack

Machine Learning

* YOLOv8 Pose

Backend

* Flask

Frontend

* HTML
* CSS
* JavaScript
* Bootstrap

Scientific Method

* Rapid Entire Body Assessment (REBA)

⸻

Folder Structure

worker-fatigue/
│
├── app.py
├── requirements.txt
├── README.md
│
├── detection/
├── ergonomics/
├── features/
├── ml/
├── static/
├── templates/
├── utils/
├── videos/

⸻

Installation

Clone the repository

git clone https://github.com/<YOUR_USERNAME>/AI-Worker-Fatigue-Monitoring-System.git
cd AI-Worker-Fatigue-Monitoring-System

Create a virtual environment

python -m venv venv

Activate the environment

macOS / Linux

source venv/bin/activate

Windows

venv\Scripts\activate

Install dependencies

pip install -r requirements.txt

⸻

Download YOLO Models

This repository does not include pretrained YOLO models.

Download the required models from Ultralytics or let YOLO download them automatically during the first run.

Example:

yolov8m-pose.pt

⸻

Running the Project

Start the Flask application

python app.py

Open your browser

http://127.0.0.1:5000

⸻

Ergonomic Assessment

The project evaluates posture using the Rapid Entire Body Assessment (REBA) methodology.

The implementation includes:

* Trunk scoring
* Neck scoring
* Leg scoring
* Upper arm scoring
* Lower arm scoring
* Official REBA Table A
* Official REBA Table B
* Official REBA Table C
* Time-based activity scoring
* Real-time ergonomic risk estimation

⸻

Fatigue Detection Logic

The system does not classify fatigue from a single frame.

Instead, it follows the workflow below:

1. Detect the worker.
2. Estimate body posture.
3. Calculate body joint angles.
4. Compute the REBA score.
5. Track the worker over time.
6. Monitor sustained unsafe postures.
7. Generate warnings and alerts if unsafe postures persist beyond predefined time thresholds.

This approach reduces false alarms caused by temporary bending or short-duration tasks.

⸻

Current Project Status

Completed

* Person Detection
* Multi-Person Tracking
* Pose Estimation
* Joint Angle Calculation
* Moving Average Filtering
* Official REBA Implementation
* Activity Timer
* Risk Classification
* Flask Integration

In Progress

* Professional Monitoring Dashboard
* Live Worker Status Table
* Alert Management Panel
* Automatic REBA Adjustment Detection

⸻

Future Improvements

* RULA Assessment
* Machine Learning-based Fatigue Prediction
* Shift-wise Worker Analytics
* Historical Ergonomic Reports
* CSV/PDF Report Export
* Database Integration
* Supervisor Dashboard
* Email/SMS Notifications
* Thermal Camera Support
* PPE Detection Integration

⸻

Screenshots

Live Detection

Add screenshot here

Dashboard

Add screenshot here

Worker Status Table

Add screenshot here

⸻

Author

Arindom Pratim Borah

B.Tech – Computer Science & Engineering

Assam Engineering College

⸻

License

This project is intended for academic and research purposes.

If you use this work, please provide appropriate attribution.

⸻

Acknowledgements

* Ultralytics YOLOv8
* OpenCV
* Flask
* ByteTrack
* Rapid Entire Body Assessment (REBA)