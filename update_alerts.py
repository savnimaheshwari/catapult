import json
import os

alerts = [
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
            "target_azimuth_deg": 64.90,
            "image_dimensions_px": "1024 \u00d7 1024",
            "total_buildings": 160,
            "coordinate_system": "WGS84",
            "lng_range": [-122.750, -122.740],
            "lat_range": [38.467, 38.477],
            "location": "Santa Rosa, California",
            "catalog_id": "105001000A632800"
        }
    }
]

main_path = "backend/main.py"
with open(main_path, "r") as f:
    content = f.read()

alerts_str = json.dumps(alerts, indent=4)

start_idx = content.find("alerts_data = [")
end_search_str = "    for alert in alerts_data:"
end_idx = content.find(end_search_str)

if start_idx != -1 and end_idx != -1:
    new_content = content[:start_idx] + "alerts_data = " + alerts_str + "\n\n" + content[end_idx:]
    with open(main_path, "w") as f:
        f.write(new_content)
    print("Done - replaced alerts_data in main.py")
else:
    print("ERROR: Could not find alerts_data block")
