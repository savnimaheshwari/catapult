from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import networkx as nx
import os
from ml_engine import simulate_xbd_analysis
from pathfinder import calculate_safe_route

app = FastAPI(title="TerraForm Response API")

sample_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../sample_data"))
if os.path.exists(sample_data_dir):
    app.mount("/images", StaticFiles(directory=sample_data_dir), name="images")

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

@app.post("/verify-human")
async def verify_human(payload: ProofPayload):
    """
    Placeholder for World ID verification logic.
    In production, you send this payload to the Worldcoin Developer API.
    """
    # Simulate verification
    is_valid = True 
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid proof of human.")
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