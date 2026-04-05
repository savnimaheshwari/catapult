# 🌍 TerraForm Response

> **"Reducing the 48-hour disaster assessment window to 48 seconds."**

TerraForm Response is a full-stack disaster intelligence platform that combines real-time satellite imagery, deep learning building segmentation, and A\* pathfinding to give first responders actionable situational awareness within seconds of a disaster event.

---

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Features](#features)
- [ML Pipeline](#ml-pipeline)
- [API Reference](#api-reference)
- [Frontend Components](#frontend-components)
- [Dataset](#dataset)
- [Setup & Running](#setup--running)
- [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)

---

## Overview

TerraForm Response is built for FEMA and emergency-response agencies. When a disaster occurs — a hurricane, wildfire, or flood — satellite tasking is triggered and the resulting post-event imagery is processed through a multi-model deep learning pipeline that:

1. **Classifies** the type of disaster from satellite imagery
2. **Segments** all buildings in the scene using a trained U-Net model
3. **Renders** the annotated scene on a cinematic 3D Mapbox globe in near real-time
4. **Routes** emergency vehicles around damaged infrastructure using graph pathfinding
5. **Verifies** users are human via Worldcoin World ID before granting access to the system

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          User Browser                               │
│                                                                     │
│   ┌──────────────┐    ┌──────────────────┐    ┌─────────────────┐  │
│   │  MapGlobe.js │    │ DisasterOverlay  │    │ SocialFeedPanel │  │
│   │  (Mapbox GL) │    │   (Satellite +   │    │ (Google News    │  │
│   │  3D Globe    │◄──►│   SVG Overlay)   │    │  RSS Feed)      │  │
│   └──────┬───────┘    └──────────────────┘    └─────────────────┘  │
│          │                                                          │
└──────────┼──────────────────────────────────────────────────────────┘
           │ REST API (localhost:8000)
┌──────────▼──────────────────────────────────────────────────────────┐
│                        FastAPI Backend                              │
│                                                                     │
│   ┌─────────────────┐    ┌──────────────────┐    ┌──────────────┐  │
│   │   ml_engine.py  │    │  pathfinder.py   │    │  World ID    │  │
│   │                 │    │                  │    │  Verifier    │  │
│   │ ┌─────────────┐ │    │  NetworkX A*     │    │  /verify-    │  │
│   │ │disaster_type│ │    │  Grid Pathfind   │    │  human       │  │
│   │ │  _model.h5  │ │    │  Safe Route Calc │    └──────────────┘  │
│   │ └─────────────┘ │    └──────────────────┘                      │
│   │ ┌─────────────┐ │                                               │
│   │ │  building_  │ │                                               │
│   │ │segmentation │ │                                               │
│   │ │   .h5       │ │                                               │
│   │ └─────────────┘ │                                               │
│   └─────────────────┘                                               │
│                                                                     │
│   Static File Server: /test_images → test/images/                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Features

### 🔴 Live Disaster Hotspots
Three active disaster events are rendered as pulsing red beacons on the 3D globe, sourced from real xBD dataset satellite imagery:

| Event | Location | Sensor | Buildings |
|---|---|---|---|
| Hurricane Harvey | Houston, TX | GeoEye-1 | 197 |
| Hurricane Florence | Jacksonville, NC | GeoEye-1 | 12 |
| Santa Rosa Wildfire (Tubbs) | Santa Rosa, CA | GeoEye-1 | 160 |

Clicking any marker zooms the globe to street level and opens the intelligence panel.

### 🛰️ Satellite Intelligence Panel
- Displays the **post-disaster** GeoEye-1/WorldView satellite image at full resolution
- Shows rich sensor metadata: GSD, off-nadir angle, sun azimuth/elevation, catalog ID
- **AI Building Segmentation toggle**: overlays the model's predicted building footprints as translucent red SVG polygons

### 🧠 ML Building Segmentation Overlay
When the "AI Building Segmentation Mask" checkbox is enabled, the `building_segmentation.h5` model runs inference on the satellite image and renders detected building polygons directly on top of the imagery. Polygons are extracted using OpenCV contour tracing and rendered at 1024×1024 coordinate precision.

### 🗺️ A* Emergency Routing
Clicking "Plot Emergency Route" triggers the `pathfinder.py` module, which:
1. Builds a 30×30 grid graph over the disaster area using NetworkX
2. Adds diagonal edges for smoother, more realistic paths
3. Marks damaged nodes with infinite weight
4. Computes shortest safe path using `nx.shortest_path`
5. Renders the route as a neon line on the Mapbox globe

### 📰 Live News Feed
Each disaster hotspot pulls real-time news from Google News RSS, displaying the top 5 articles relevant to the event (e.g., "Hurricane Harvey Houston flooding").

### 🔒 World ID Human Verification
Access to the disaster intelligence system requires Proof-of-Human verification via [Worldcoin's World ID](https://worldcoin.org/world-id). This prevents bot networks from flooding the emergency infrastructure. The backend generates and validates HMAC-signed RP signatures.

### 📡 Social Feed Panel
A minimizable capsule widget in the bottom-left corner shows a curated live social feed of posts related to the active disaster, simulating what a real-world keyword-monitoring pipeline would surface from Twitter/X Firehose and USGS feeds.

---

## ML Pipeline

The `ml_pipeline/` directory contains four trained Keras models and their corresponding training notebooks.

### Models

| File | Input Size | Purpose |
|---|---|---|
| `disaster_type_model.h5` | 224×224 RGB | Classifies disaster type into 6 classes |
| `building_segmentation.h5` | 256×256 RGB | Outputs per-pixel building probability mask |
| `damage_classifier.h5` | Variable | Classifies building damage severity |
| `pre_post_classifier.h5` | Variable | Distinguishes pre vs. post disaster imagery |

### Disaster Type Classes
`Volcano`, `Flooding`, `Earthquake`, `Fire`, `Wind`, `Tsunami`

### Building Segmentation Details (`ml_engine.py`)

```python
def segment_buildings(image_path: str) -> list[str]:
    """
    Runs building segmentation using the building_segmentation.h5 model.
    The model expects raw 0-255 RGB values at 256x256 resolution and outputs
    a per-pixel probability mask. Contours above the 0.2 confidence threshold
    are extracted and scaled to the 1024x1024 image coordinate space.
    """
```

**Preprocessing:**
- Image is loaded and resized to 256×256
- Passed to the model as raw `float32` values (0–255 range) — **no normalization**
- Model outputs a `(256, 256)` probability mask

**Post-processing:**
- Threshold: `> 0.2` (tuned to model's output distribution, max activation ~0.72)
- `cv2.MORPH_CLOSE` kernel applied to bridge adjacent building pixels
- Contours extracted with `cv2.CHAIN_APPROX_SIMPLE`
- Each contour simplified with `cv2.approxPolyDP(epsilon=1.5)`
- Coordinates scaled 4× (256→1024) to match the SVG viewport

**Typical output:** 60–200 polygon strings per image, rendered as SVG `<polygon>` elements over the satellite image.

### Training Notebooks

| Notebook | Description |
|---|---|
| `Model_1_Pre_Post_Classification.ipynb` | Binary classification: pre vs. post disaster |
| `Model_2_Building_Detection.ipynb` | U-Net building segmentation training |
| `Model_3_Damage_Classification.ipynb` | Multi-class damage severity assessment |
| `Model_4_Disaster_Type_Classification.ipynb` | 6-class disaster type CNN |

---

## API Reference

Base URL: `http://localhost:8000`

### `GET /global-alerts`
Returns the 3 active disaster hotspots with satellite image URLs, sensor metadata, and ML-generated building bounds.

**Response:**
```json
{
  "status": "success",
  "alerts": [
    {
      "id": "harvey",
      "title": "Hurricane Harvey",
      "lat": 29.747,
      "lng": -95.537,
      "images": {
        "pre": "http://localhost:8000/test_images/hurricane-harvey_00000483_pre_disaster.png",
        "post": "http://localhost:8000/test_images/hurricane-harvey_00000483_post_disaster.png"
      },
      "metadata": {
        "sensor": "GEOEYE01",
        "disaster_type": "Flooding",
        "total_buildings": 197,
        "building_bounds": ["x1,y1 x2,y2 ...", "..."],
        "gsd_m": 2.2,
        "coordinate_system": "WGS84"
      }
    }
  ]
}
```

> Building bounds are populated by running `building_segmentation.h5` inference on the post-disaster image at server startup.

---

### `GET /social-feed/{alert_id}`
Fetches top 5 live news articles from Google News RSS for the given disaster event.

**Path params:** `alert_id` — one of `harvey`, `florence`, `santarosa`

**Response:**
```json
{
  "status": "success",
  "feed": [
    {
      "id": "news_1",
      "platform": "CNN",
      "title": "Harvey death toll rises as floodwaters recede",
      "url": "https://...",
      "time": "Mon, 04 Sep 2017 14:00:00 GMT"
    }
  ]
}
```

---

### `POST /analyze-disaster`
Triggers damage heatmap generation and A* route calculation for a given coordinate pair.

**Request body:**
```json
{
  "lat": 29.747,
  "lng": -95.537,
  "dest_lat": 29.797,
  "dest_lng": -95.587
}
```

**Response:**
```json
{
  "status": "success",
  "damage_heatmap": {
    "type": "FeatureCollection",
    "features": [...]
  },
  "route": {
    "type": "Feature",
    "geometry": { "type": "LineString", "coordinates": [[lng, lat], ...] }
  }
}
```

---

### `POST /auth/world-id/prepare`
Generates an HMAC-signed RP context for World ID verification.

**Request body:**
```json
{ "action": "disaster-access" }
```

---

### `POST /verify-human`
Validates a World ID ZKP proof against the Worldcoin Developer Portal.

**Request body:**
```json
{
  "proof": {...},
  "merkle_root": "0x...",
  "nullifier_hash": "0x...",
  "action": "disaster-access"
}
```

---

## Frontend Components

| Component | Description |
|---|---|
| `MapGlobe.js` | Main container — initializes Mapbox GL globe, places pulse markers, orchestrates all overlays |
| `DisasterOverlay.js` | Right-side intelligence panel — satellite image, SVG building segmentation, metadata drawer |
| `SocialFeedPanel.js` | Minimizable bottom-left capsule — live news ticker and social feed |
| `LocalNewsPanel.js` | Inline news display panel for per-disaster news articles |
| `AuthWidget.js` | World ID verification gate UI |
| `WorldIDAuth.js` | IDKit integration component |

### Globe Configuration (Mapbox)
- **Projection:** `globe` (true 3D sphere)
- **Style:** `mapbox://styles/mapbox/satellite-streets-v12` (photorealistic earth)
- **Fog:** Deep space atmosphere (`rgb(11, 11, 25)`) with 0.6 star intensity
- **Marker animation:** CSS `@keyframes MapPulse` with expanding red ring

---

## Dataset

This project uses the **[xBD Dataset](https://xview2.org/)** — the industry standard for satellite building damage assessment, created by DIU (Defense Innovation Unit) and used in the xView2 competition.

### Dataset Structure
```
test/
├── images/          # Post-disaster satellite PNGs (1024×1024)
└── labels/          # JSON label files with polygon annotations

train/
├── images/
└── labels/
```

### Label JSON Format
Each label file contains per-building polygon annotations in WKT format:
```json
{
  "metadata": {
    "sensor": "GEOEYE01",
    "disaster_type": "flooding",
    "capture_date": "2017-08-31T17:38:50.685Z",
    "gsd": 2.2
  },
  "features": {
    "lng_lat": [
      { "wkt": "POLYGON ((-95.537 29.747, ...))", "properties": { "subtype": "destroyed" } }
    ],
    "xy": [
      { "wkt": "POLYGON ((512 300, 520 300, ...))" }
    ]
  }
}
```

---

## Setup & Running

### Prerequisites
- Python 3.10+ with `conda` or `venv`
- Node.js 18+
- Mapbox API token
- Worldcoin Developer Portal credentials (optional — for World ID)

### Backend

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt
pip install tensorflow opencv-python python-dotenv

# Start the API server
uvicorn main:app --reload
```

The server starts on `http://localhost:8000`. On startup, a daemon thread pre-loads both `.h5` models into memory so inference is instant on first request.

### Frontend

```bash
cd frontend

# Install Node dependencies
npm install

# Start the dev server
npm start
```

The app opens at `http://localhost:3000`.

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description |
|---|---|
| `RP_ID` | Worldcoin Relying Party ID |
| `WORLD_RP_SIGNING_KEY` | HMAC signing key for World ID RP context |

### Frontend (`frontend/.env`)

| Variable | Description |
|---|---|
| `REACT_APP_MAPBOX_TOKEN` | Mapbox GL JS public access token |
| `REACT_APP_WLD_APP_ID` | Worldcoin App ID (from Developer Portal) |

---

## Project Structure

```
Catapult/
├── backend/
│   ├── main.py               # FastAPI app, all API endpoints
│   ├── ml_engine.py          # TF model loading & inference (classify + segment)
│   ├── pathfinder.py         # NetworkX A* safe route calculation
│   └── requirements.txt      # Python dependencies
│
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── MapGlobe.js          # 3D Mapbox globe + marker orchestration
│       │   ├── DisasterOverlay.js   # Intelligence panel + SVG building masks
│       │   ├── SocialFeedPanel.js   # Live news capsule widget
│       │   ├── LocalNewsPanel.js    # Per-disaster news panel
│       │   ├── AuthWidget.js        # World ID gate UI
│       │   └── WorldIDAuth.js       # IDKit integration
│       └── App.js
│
├── ml_pipeline/
│   ├── building_segmentation.h5      # U-Net building segmentation (~88 MB)
│   ├── disaster_type_model.h5        # Disaster classifier (~10 MB)
│   ├── damage_classifier.h5          # Damage severity model (~49 MB)
│   ├── pre_post_classifier.h5        # Pre/post binary classifier (~25 MB)
│   ├── Model_1_Pre_Post_Classification.ipynb
│   ├── Model_2_Building_Detection.ipynb
│   ├── Model_3_Damage_Classification.ipynb
│   └── Model_4_Disaster_Type_Classification.ipynb
│
├── test/
│   ├── images/    # xBD test set satellite images
│   └── labels/    # xBD test set JSON annotations
│
├── train/
│   ├── images/    # xBD training set satellite images
│   └── labels/    # xBD training set JSON annotations
│
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, Mapbox GL JS, CSS animations |
| **Backend** | FastAPI, Uvicorn, Python 3.10 |
| **ML Inference** | TensorFlow / Keras (`.h5` models) |
| **Computer Vision** | OpenCV (`cv2`) — contour extraction, morphological ops |
| **Graph Pathfinding** | NetworkX — A\* on 30×30 grid with diagonal edges |
| **Human Verification** | Worldcoin World ID (IDKit v4, HMAC-signed RP) |
| **Satellite Imagery** | xBD Dataset — GeoEye-1, WorldView-2/3 imagery |
| **Map Rendering** | Mapbox GL JS — satellite-streets v12, globe projection |
| **News Feed** | Google News RSS (real-time, per-disaster queries) |
