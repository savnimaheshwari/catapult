# 🌍 ProjectSendHelp

> **"Making a first response the fastest response."**

ProjectSendHelp is a disaster intelligence platform built for FEMA and emergency-response agencies. It processes real-time post-disaster satellite imagery through deep learning models to give first responders instant situational awareness — identifying disaster types, mapping affected buildings, and surfacing live news — all from a straightforward and easy-to-use interface.

---

## Features

### Live Disaster Hotspots
Active disaster zones are rendered as pulsing red beacons on a realistic 3D globe. The current hotspots are sourced from real xBD-dataset satellite imagery:

| Event | Location | Buildings Detected |
|---|---|---|
| Hurricane Harvey | Houston, TX | 197 |
| Hurricane Florence | Jacksonville, NC | 12 |
| Santa Rosa Wildfire (Tubbs Fire) | Santa Rosa, CA | 160 |

In production, this would be connected to a live satellite through an AWS clust

Clicking a marker smoothly zooms the globe to street level and opens the intelligence panel.

### Satellite Intelligence Panel
Each hotspot displays its post-disaster GeoEye-1 or WorldView satellite image alongside key sensor metadata — capture date, ground resolution (GSD), off-nadir angle, sun azimuth, and geographic coverage.

### AI Building Segmentation
Toggling the "AI Building Segmentation Mask" checkbox overlays the predictions of a trained deep learning model directly on the satellite image. The model identifies building footprints as translucent red polygons, letting responders instantly see which structures exist in the affected zone.

### Live News Feed
Each disaster zone is linked to a real-time news feed pulled dynamically from Google News, surfacing the latest relevant articles for that specific event.

### Social Feed Panel
A minimizable capsule in the bottom-left corner simulates a live social intelligence feed — aggregating keyword signals the way a real system would monitor Twitter/X Firehose, USGS feeds, and emergency scanner data.

### Proof-of-Human Verification
Access to the platform is gated by **World ID** (by Worldcoin), a sybil-resistant Proof-of-Human protocol. This ensures only verified humans — not bots — can interact with the emergency infrastructure.

---

## Dataset

All models were trained and evaluated on the **[xBD Dataset](https://xview2.org/)** (xView2 Building Damage), the industry-standard benchmark for satellite-based disaster damage assessment. xBD contains over 850,000 building annotations across 19 different disaster events worldwide, captured via GeoEye-1 and WorldView-2/3 satellites.

---

## Models Developed

Four deep learning models were built and trained as part of this project:

| Model | What it does | Accuracy |
|---|---|---|
| Pre/Post Classifier | Determines whether a satellite image was captured before or after a disaster event | **86.8%** (AUC 0.95) |
| Building Segmentation (U-Net) | Identifies and segments individual building footprints in a satellite scene | **93.4%** |
| Damage Classifier | Classifies each overall image into one of four damage levels: No Damage, Minor, Major, or Destroyed | **80.9%** |
| Disaster Type Classifier | Identifies the category of disaster (flooding, fire, earthquake, volcano, tsunami, wind) from the image | **73.8%** |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Mapbox GL JS |
| Backend | FastAPI (Python) |
| ML Models | TensorFlow / Keras |
| Satellite Data | xBD Dataset (GeoEye-1, WorldView-2/3) |
| Human Verification | Worldcoin World ID |
| News | Google News RSS |
