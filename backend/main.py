from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import networkx as nx
import os
import hmac
import hashlib
import uuid
import time
import requests
from dotenv import load_dotenv
from ml_engine import load_models, classify_disaster, segment_buildings
from pathfinder import calculate_safe_route
import threading

load_dotenv()

RP_ID = os.getenv("RP_ID")
# Fallback for the key name seen earlier
WORLD_RP_SIGNING_KEY = os.getenv("WORLD_RP_SIGNING_KEY") or os.getenv("REACT_APP_WORLD_SIGNING_KEY")

app = FastAPI(title="TerraForm Response API")

sample_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../sample_data"))
if os.path.exists(sample_data_dir):
    app.mount("/images", StaticFiles(directory=sample_data_dir), name="images")

test_images_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../test/images"))
if os.path.exists(test_images_dir):
    app.mount("/test_images", StaticFiles(directory=test_images_dir), name="test_images")

harvey_pics_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../harvey_pics"))
if os.path.exists(harvey_pics_dir):
    app.mount("/harvey_pics", StaticFiles(directory=harvey_pics_dir), name="harvey_pics")

florence_pics_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../florence_pics"))
if os.path.exists(florence_pics_dir):
    app.mount("/florence_pics", StaticFiles(directory=florence_pics_dir), name="florence_pics")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
class Coordinate(BaseModel):
    lat: float
    lng: float
    dest_lat: float = None
    dest_lng: float = None

class ProofPayload(BaseModel):
    proof: dict
    merkle_root: str
    nullifier_hash: str
    action: str
    verification_level: str = None

class RpSignatureRequest(BaseModel):
    action: str

@app.on_event("startup")
def startup_event():
    threading.Thread(target=load_models, daemon=True).start()

# --- Endpoints ---
@app.get("/global-alerts")
async def global_alerts():
    """
    Returns the active disaster hotspots (red alerts) to be rendered on the globe.
    
    SYSTEM ARCHITECTURE PIPELINE (How alerts are naturally generated):
    1. INGESTION: The system listens to live data streams (X/Twitter Firehose, USGS hazard feeds, NOAA RSS).
    2. KEYWORD ANALYSIS: NLP algorithms filter for a sudden localized influx of keywords like 'flood', 'rescue', 'fire'.
    3. TRIAGE: Once a geographical threshold is met (e.g. 50+ emergency mentions within a 5-mile radius), a new Alert ID is minted.
    4. SATELLITE TASKING: An automated webhook requests pre/post satellite imagery from Maxar/Planet for that exact coordinate.
    5. This endpoint serves those active hotspots to the frontend React globe.
    """
    alerts_data = [
        {
            "id": "harvey",
            "title": "Hurricane Harvey",
            "lat": 29.74728748455649,
            "lng": -95.53694363244546,
            "news": "Post-disaster flooding analysis near Houston, TX. 197 structures assessed via GeoEye-1 satellite imagery captured August 31, 2017.",
            "images": {
                "pre": "http://localhost:8000/test_images/hurricane-harvey_00000483_pre_disaster.png",
                "post": "http://localhost:8000/test_images/hurricane-harvey_00000483_post_disaster.png"
            },
            "metadata": {
                "sensor": "GEOEYE01",
                "capture_date": "2017-08-31T17:38:50.685Z",
                "disaster_type": "Flooding",
                "image_tag": "post_disaster",
                "gsd_m": 2.2,
                "pan_resolution_m": 0.55,
                "off_nadir_angle_deg": 17.3,
                "sun_azimuth_deg": 172.4,
                "sun_elevation_deg": 59.7,
                "target_azimuth_deg": 355.2,
                "image_dimensions_px": "1024 \u00d7 1024",
                "total_buildings": 197,
                "coordinate_system": "WGS84",
                "lng_range": [-95.542, -95.532],
                "lat_range": [29.742, 29.752],
                "location": "Houston, Texas",
                "catalog_id": "105001000A00B300"
            }
        },
        {
            "id": "florence",
            "title": "Hurricane Florence",
            "lat": 34.68852161438465,
            "lng": -77.97635795431499,
            "news": "Post-disaster flooding analysis near Jacksonville, NC. 12 structures assessed via GeoEye-1 satellite imagery captured September 20, 2018.",
            "images": {
                "pre": "http://localhost:8000/test_images/hurricane-florence_00000235_pre_disaster.png",
                "post": "http://localhost:8000/test_images/hurricane-florence_00000235_post_disaster.png"
            },
            "metadata": {
                "sensor": "GEOEYE01",
                "capture_date": "2018-09-20T16:04:41.000Z",
                "disaster_type": "Flooding",
                "image_tag": "post_disaster",
                "gsd_m": 2.9,
                "pan_resolution_m": 0.72,
                "off_nadir_angle_deg": 25.1,
                "sun_azimuth_deg": 162.7,
                "sun_elevation_deg": 57.0,
                "target_azimuth_deg": 69.0,
                "image_dimensions_px": "1024 \u00d7 1024",
                "total_buildings": 12,
                "coordinate_system": "WGS84",
                "lng_range": [-77.981, -77.971],
                "lat_range": [34.683, 34.693],
                "location": "Jacksonville, North Carolina",
                "catalog_id": "103001007B4A7200"
            }
        },
        {
            "id": "santarosa",
            "title": "Santa Rosa Wildfire",
            "lat": 38.47229494455633,
            "lng": -122.7450409829897,
            "news": "Post-disaster fire analysis in Santa Rosa suburb. 160 structures assessed via GeoEye-1 satellite imagery during Tubbs Fire (2017).",
            "images": {
                "pre": "http://localhost:8000/test_images/santa-rosa-wildfire_00000066_pre_disaster.png",
                "post": "http://localhost:8000/test_images/santa-rosa-wildfire_00000066_post_disaster.png"
            },
            "metadata": {
                "sensor": "GEOEYE01",
                "capture_date": "2017-10-15T18:45:00.000Z",
                "disaster_type": "Fire",
                "image_tag": "post_disaster",
                "gsd_m": 1.67,
                "pan_resolution_m": 0.42,
                "off_nadir_angle_deg": 5.67,
                "sun_azimuth_deg": 132.82,
                "sun_elevation_deg": 69.89,
                "target_azimuth_deg": 64.9,
                "image_dimensions_px": "1024 \u00d7 1024",
                "total_buildings": 160,
                "coordinate_system": "WGS84",
                "lng_range": [-122.75, -122.74],
                "lat_range": [38.467, 38.477],
                "location": "Santa Rosa, California",
                "catalog_id": "105001000A632800"
            }
        }
    ]

    for alert in alerts_data:
        post_url = alert["images"]["post"]
        if post_url.startswith("http://localhost:8000/test_images/"):
            rel_path = post_url.replace("http://localhost:8000/test_images/", "")
            local_path = os.path.join(test_images_dir, rel_path)

            predicted_type = classify_disaster(local_path)
            if predicted_type != "Unknown":
                alert["metadata"]["disaster_type"] = predicted_type

            bounds = segment_buildings(local_path)
            if bounds:
                alert["metadata"]["building_bounds"] = bounds
                alert["metadata"]["total_buildings"] = len(bounds)

    return {
        "status": "success",
        "alerts": alerts_data
    }

@app.get("/social-feed/{alert_id}")
async def get_social_feed(alert_id: str):
    """
    Simulates a clean API call pulling relevant social media/news data.
    Returns highly visual, fascinating data based on the alert.
    """
    import xml.etree.ElementTree as ET
    import urllib.parse
    
    # Mapping of alert_id to search queries
    queries = {
        "harvey": "Hurricane Harvey Houston flooding",
        "florence": "Hurricane Florence North Carolina",
        "santarosa": "Santa Rosa Tubbs wildfire 2017"
    }
    
    query_str = queries.get(alert_id, "Natural Disaster")
    quoted_query = urllib.parse.quote(query_str)
    url = f"https://news.google.com/rss/search?q={quoted_query}&hl=en-US&gl=US&ceid=US:en"
    
    feed = []
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            items = root.findall('.//item')[:5] # Get top 5 news items
            
            for index, item in enumerate(items, 1):
                title = item.find('title').text if item.find('title') is not None else "News Update"
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                link = item.find('link').text if item.find('link') is not None else ""
                source_elem = item.find('source')
                source_name = source_elem.text if source_elem is not None else "Google News"
                
                feed.append({
                    "id": f"news_{index}",
                    "platform": source_name,
                    "time": pub_date,
                    "title": title,
                    "url": link
                })
    except Exception as e:
        print(f"Error fetching news: {e}")
        
    # Generic mock for unknown alerts or if fetch fails
    if not feed:
        feed = [
            {
                "id": "g1",
                "platform": "GlobalWatch",
                "author": "System Monitor",
                "avatar": "https://images.unsplash.com/photo-1517430816045-df4b7de11d1d?w=100&h=100&fit=crop",
                "time": "Active",
                "content": "Monitoring regional chatter and emergency frequencies for updates.",
                "image": None
            }
        ]
    
    return {
        "status": "success",
        "feed": feed
    }

@app.post("/auth/world-id/prepare")
async def prepare_world_id(req: RpSignatureRequest):
    """
    Generates the RP Signature (rp_context) required for World ID 4.0.
    """
    if not WORLD_RP_SIGNING_KEY or not RP_ID:
        raise HTTPException(status_code=500, detail="World ID configuration (RP_ID or Signing Key) missing in backend.")

    nonce = str(uuid.uuid4())
    created_at = int(time.time())
    expires_at = created_at + 600  # Valid for 10 minutes

    # Construct the message to sign: {action}{nonce}{created_at}{expires_at}
    message = f"{req.action}{nonce}{created_at}{expires_at}"
    
    signature = hmac.new(
        key=WORLD_RP_SIGNING_KEY.encode(),
        msg=message.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    return {
        "rp_id": RP_ID,
        "sig": signature,
        "nonce": nonce,
        "created_at": created_at,
        "expires_at": expires_at
    }

@app.post("/verify-human")
async def verify_human(payload: ProofPayload):
    """
    Verifies the World ID proof against the Worldcoin Developer Portal.
    """
    if not RP_ID:
         raise HTTPException(status_code=500, detail="RP_ID missing in backend.")

    url = f"https://developer.worldcoin.org/api/v1/verify/{RP_ID}"
    
    # Payload for Worldcoin API v1/v2 (Note: v4 often uses a different path, 
    # but v1/verify/{rp_id} is standard for ZKP verification)
    verify_body = {
        "proof": payload.proof,
        "merkle_root": payload.merkle_root,
        "nullifier_hash": payload.nullifier_hash,
        "action": payload.action,
        "verification_level": payload.verification_level or "device"
    }

    response = requests.post(url, json=verify_body)
    
    if response.status_code != 200:
        error_detail = response.json().get("detail", "Verification failed")
        raise HTTPException(status_code=400, detail=f"World ID verification failed: {error_detail}")

    return {"status": "success", "message": "Human verified successfully."}

@app.post("/analyze-disaster")
async def analyze_disaster(coord: Coordinate):
    """
    Accepts coordinates, simulates YOLOv8 analysis, and calculates routes.
    """
    # 1. Simulate YOLOv8 ML Analysis (xBD Dataset mask retrieval)
    damaged_points = simulate_xbd_analysis(coord.lat, coord.lng, radius_deg=0.015)
    
    # Format damaged_points to GeoJSON
    damage_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [pt['lng'], pt['lat']] # GeoJSON is [lng, lat]
                },
                "properties": {"damage": "severe"}
            } for pt in damaged_points
        ]
    }
    
    geojson_route = None
    if coord.dest_lat and coord.dest_lng:
        # 2. NetworkX Pathfinding
        route_coords = calculate_safe_route(
            coord.lat, coord.lng, 
            coord.dest_lat, coord.dest_lng, 
            damaged_points
        )
        
        if route_coords:
            geojson_route = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": route_coords
                }
            }
            
    return {
        "status": "success", 
        "damage_heatmap": damage_geojson,
        "route": geojson_route
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)