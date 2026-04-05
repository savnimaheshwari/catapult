# 🌍 ProjectSendHelp

Welcome to **ProjectSendHelp**! This document provides an overview of what the platform is, what it does, and how it will be demonstrated to judges.

---

## 🚀 What is ProjectSendHelp?
**"Infrastructure-as-a-Service for FEMA to reduce the 48-hour assessment window to 48 seconds."**

ProjectSendHelp is a modern, full-stack disaster relief platform. It consists of a React-based frontend that renders a highly detailed, 3D cinematic Mapbox globe, and a Python FastAPI backend that functions as the "brain". 

The core goal of the project is to map out disaster zones (e.g., floods, earthquakes, hurricanes) rapidly and find optimal rescue routes using artificial intelligence and pathfinding algorithms. 

To prevent spam and ensure the data's integrity, users verifying damages or requesting aid are gated by a sybil-resistant **Proof-of-Human** model powered by World ID.

## 🛠️ What Does It Actually Do?

When you run this project, you will demonstrate a "mock" end-to-end flow:
1. **The User Verification:** 
   A user accesses the dashboard and is prompted to verify they are human using the **World ID** SDK. This uses Worldcoin's IDKit to protect emergency infrastructure from bot networks.
2. **The Damage Assessment (YOLOv8 ML):** 
   Once verified, the user clicks anywhere on the 3D Globe to simulate a disaster event. The backend `ml_engine.py` script intercepts this coordinate. In a final production build, you can inject a custom YOLO base trained on the **xBD Dataset** (the industry standard for satellite building damage). For this demo, it rapidly plots "Damaged" areas mathematically.
3. **The Detour Calculation (NetworkX):** 
   Knowing where the buildings are destroyed, emergency responders need to get from Point A to Point B. The backend `pathfinder.py` maps the entire area as a giant coordinate grid graph, labels the damaged nodes with "infinite weight", and instantly computes an **A* optimal detour route** avoiding all hazards.
4. **The Cinematic Response:** 
   The frontend consumes the NetworkX output and immediately plots a sleek neon line bypassing all the orange/red hazard heatmaps. 

---

## ⚡ Integration Guide (Adding your Custom Model)
If you decide to deploy the actual YOLO object detection model:

1. Open `backend/ml_engine.py`.
2. Locate the massive `🧠 MODEL INJECTION POINT` comment block.
3. Provide your `.pt` inference architecture.
4. Hook up a local image stream (or hardcode static satellite images) to detect building damage.

## 🏃 Running The Project

Make sure you've populated your `.env` tokens in the frontend (`REACT_APP_MAPBOX_TOKEN`, etc.).

**Terminal 1 (Backend)**
```bash
cd backend
conda activate base # (or your environment)
pip install -r requirements.txt
uvicorn main:app --reload
```

**Terminal 2 (Frontend)**
```bash
cd frontend
npm install
npm start
```
