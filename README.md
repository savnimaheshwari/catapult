# 🌍 TerraForm Response

> **"Reducing the 48-hour disaster assessment window to 48 seconds."**

TerraForm Response is a disaster intelligence platform built for FEMA and emergency-response agencies. It processes real-time post-disaster satellite imagery through deep learning models to give first responders instant situational awareness — identifying disaster types, mapping affected buildings, and surfacing live news — all from a cinematic 3D globe interface.

---

## Features

### 🔴 Live Disaster Hotspots
Active disaster zones are rendered as pulsing red beacons on a photorealistic 3D globe. The current hotspots are sourced from real xBD-dataset satellite imagery:

| Event | Location | Buildings Detected |
|---|---|---|
| Hurricane Harvey | Houston, TX | 197 |
| Hurricane Florence | Jacksonville, NC | 12 |
| Santa Rosa Wildfire (Tubbs Fire) | Santa Rosa, CA | 160 |

Clicking a marker smoothly zooms the globe to street level and opens the intelligence panel.

### 🛰️ Satellite Intelligence Panel
Each hotspot displays its post-disaster GeoEye-1 or WorldView satellite image alongside key sensor metadata — capture date, ground resolution (GSD), off-nadir angle, sun azimuth, and geographic coverage.

### 🧠 AI Building Segmentation
Toggling the "AI Building Segmentation Mask" checkbox overlays the predictions of a trained deep learning model directly on the satellite image. The model identifies building footprints as translucent red polygons, letting responders instantly see which structures exist in the affected zone.

### 📰 Live News Feed
Each disaster zone is linked to a real-time news feed pulled dynamically from Google News, surfacing the latest relevant articles for that specific event.

### 📡 Social Feed Panel
A minimizable capsule in the bottom-left corner simulates a live social intelligence feed — aggregating keyword signals the way a real system would monitor Twitter/X Firehose, USGS feeds, and emergency scanner data.

### 🔒 Proof-of-Human Verification
Access to the platform is gated by **World ID** (by Worldcoin), a sybil-resistant Proof-of-Human protocol. This ensures only verified humans — not bots — can interact with the emergency infrastructure.

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
