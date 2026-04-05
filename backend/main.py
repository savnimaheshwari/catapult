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
from ml_engine import simulate_xbd_analysis
from pathfinder import calculate_safe_route

load_dotenv()

RP_ID = os.getenv("RP_ID")
# Fallback for the key name seen earlier
WORLD_RP_SIGNING_KEY = os.getenv("WORLD_RP_SIGNING_KEY") or os.getenv("REACT_APP_WORLD_SIGNING_KEY")

app = FastAPI(title="TerraForm Response API")

sample_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../sample_data"))
if os.path.exists(sample_data_dir):
    app.mount("/images", StaticFiles(directory=sample_data_dir), name="images")

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

# --- Endpoints ---
@app.get("/global-alerts")
async def global_alerts():
    return {
        "status": "success",
        "alerts": [
            {
                "id": "harvey",
                "title": "Hurricane Harvey",
                "lat": 29.7604,
                "lng": -95.3698,
                "news": "Catastrophic flooding underway in Houston region. Heavy rains expected to persist for 48 hours.",
                "images": {
                    "pre": "http://localhost:8000/images/hurrican_harvey_pre/hurricane-harvey_00000078_pre_disaster.png",
                    "post": "http://localhost:8000/images/hurricance_harvey_post/hurricane-harvey_00000078_post_disaster.png"
                }
            },
            {
                "id": "florence",
                "title": "Hurricane Florence",
                "lat": 34.2257,
                "lng": -77.9447,
                "news": "Storm surge warnings issued across entire Carolina coast. FEMA coordinating response.",
                "images": {
                    "pre": "http://localhost:8000/images/hurricane_florence_pre/hurricane-florence_00000004_pre_disaster.png",
                    "post": "http://localhost:8000/images/hurrican_florence_post/hurricane-florence_00000004_post_disaster.png"
                }
            },
            {
                "id": "santarosa",
                "title": "Tubbs Wildfire",
                "lat": 38.4404,
                "lng": -122.7141,
                "news": "Evacuation orders mandatory for Santa Rosa suburbs. Multiple homes structurally compromised.",
                "images": {
                    "pre": "http://localhost:8000/images/santa_rosa_wildfire_pre/santa-rosa-wildfire_00000066_pre_disaster.png",
                    "post": "http://localhost:8000/images/santa_rosa_wildfire_post/santa-rosa-wildfire_00000066_post_disaster.png"
                }
            }
        ]
    }

@app.get("/social-feed/{alert_id}")
async def get_social_feed(alert_id: str):
    """
    Simulates a clean API call pulling relevant social media/news data.
    Returns highly visual, fascinating data based on the alert.
    """
    import random
    
    # Mock databases with real-world-like feeds
    feeds = {
        "harvey": [
            {
                "id": "t1",
                "platform": "Twitter",
                "author": "@sparklingLily (Historical)",
                "avatar": "https://images.unsplash.com/photo-1542909168-82c3e7fdca5c?w=100&h=100&fit=crop",
                "time": "Aug 28, 2017",
                "content": "#harveyrescue (retweet this!!) Amanda 8327696449 2 adults 5 kids (2 are babies) and a puppy 12606 Ellenview Dr Houston Texas",
                "image": "http://localhost:8000/harvey_pics/harvey3.png"
            },
            {
                "id": "t2",
                "platform": "Twitter",
                "author": "@RabbiJill (Historical)",
                "avatar": "https://images.unsplash.com/photo-1517849845537-4d257902454a?w=100&h=100&fit=crop",
                "time": "Aug 28, 2017",
                "content": "There's a woman with a 3 mo old baby who needs rescue now 8614 valley meadow Houston,Tx 77078 #harveyrescue please spread word",
                "image": "http://localhost:8000/harvey_pics/hurriace_harvey3.png"
            },
            {
                "id": "t3",
                "platform": "Twitter",
                "author": "@JoeyBadeyez (Historical)",
                "avatar": "https://images.unsplash.com/photo-1598257006458-087169a1f08d?w=100&h=100&fit=crop",
                "time": "Aug 28, 2017",
                "content": "Little girl on a ventilator needs rescue NOW! - 8305 Talton Houston - #harveyrescue #harveysos #rescue #sendhelpnow",
                "image": "http://localhost:8000/harvey_pics/hurricane_harvey2.png"
            }
        ],
        "florence": [
            {
                "id": "f1",
                "platform": "Twitter",
                "author": "@NewBernResident (Historical)",
                "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop",
                "time": "Sep 14, 2018",
                "content": "Trapped in our attic with rising floodwaters in New Bern, NC. Family of 4. We need immediate rescue! #HurricaneFlorence",
                "image": "http://localhost:8000/florence_pics/florence.png"
            },
            {
                "id": "f2",
                "platform": "CrowdSource Rescue",
                "author": "Wilmington Coord (Historical)",
                "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop",
                "time": "Sep 15, 2018",
                "content": "We have 150+ open tickets for water rescues in the Wilmington area. Need high water vehicles immediately. Routes 40 and 17 are completely submerged.",
                "image": "http://localhost:8000/florence_pics/hurricane_florence.png"
            }
        ],
        "santarosa": [
            {
                "id": "s1",
                "platform": "Twitter",
                "author": "@NorCalEvac (Historical)",
                "avatar": "https://images.unsplash.com/photo-1563298723-dcfebaa392e3?w=100&h=100&fit=crop",
                "time": "Oct 9, 2017 · 2:31 AM",
                "content": "Fountaingrove is completely engulfed. We had 5 minutes to leave. Please pray for Santa Rosa. The glow over the hills is terrifying. #TubbsFire #SantaRosaFire",
                "image": "http://localhost:8000/images/santa_rosa_wildfire_post/santa-rosa-wildfire_00000066_post_disaster.png"
            },
            {
                "id": "s2",
                "platform": "Twitter",
                "author": "@SonomaOES (Historical)",
                "avatar": "https://images.unsplash.com/photo-1527980965255-d3b416303d12?w=100&h=100&fit=crop",
                "time": "Oct 9, 2017 · 3:14 AM",
                "content": "MANDATORY EVACUATION orders in effect for: Coffey Park, Larkfield-Wikiup, Fountaingrove. Do NOT shelter in place. Leave NOW. Zero visibility on Hwy 101. #TubbsFire",
                "image": "http://localhost:8000/images/santa_rosa_wildfire_post/santa-rosa-wildfire_00000284_post_disaster.png"
            },
            {
                "id": "s3",
                "platform": "Facebook Group",
                "author": "Sonoma County Updates (Historical)",
                "avatar": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop",
                "time": "Oct 9, 2017 · 4:02 AM",
                "content": "Coffey Park neighborhood is gone. Devastating loss tonight. Kaiser hospital is evacuating patients now. Satellite imagery confirms multiple block radius destroyed. #TubbsFire",
                "image": "http://localhost:8000/images/santa_rosa_wildfire_post/santa-rosa-wildfire_00000366_post_disaster.png"
            },
            {
                "id": "s4",
                "platform": "Twitter",
                "author": "@CAL_FIRE (Historical)",
                "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop",
                "time": "Oct 9, 2017 · 5:45 AM",
                "content": "Update: #TubbsFire has burned approx 25,000 acres with 0% containment. 17 structures confirmed destroyed. Wind gusts up to 79mph reported. All available air resources deployed at first light.",
                "image": None
            }
        ]
    }
    
    # Generic mock for unknown alerts
    generic_feed = [
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
        "feed": feeds.get(alert_id, generic_feed)
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