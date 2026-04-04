import React, { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

mapboxgl.accessToken = process.env.REACT_APP_MAPBOX_TOKEN;

const MapGlobe = () => {
    const mapContainer = useRef(null);
    const map = useRef(null);

    useEffect(() => {
        if (map.current) return; // initialize map only once

        map.current = new mapboxgl.Map({
            container: mapContainer.current,
            style: 'mapbox://styles/mapbox/dark-v11', // High-stakes professional dark mode
            center: [-90, 40], // Default center
            zoom: 2,
            projection: 'globe' // The 1-line Globe Config
        });

        map.current.on('style.load', () => {
            // The "Wow" Factor: Cinematic atmospheric fog
            map.current.setFog({
                'color': 'rgb(24, 24, 28)', 
                'high-color': 'rgb(36, 36, 36)', 
                'horizon-blend': 0.2, 
                'space-color': 'rgb(11, 11, 15)', 
                'star-intensity': 0.15 
            });
        });

        // Example click handler to trigger backend analysis
        map.current.on('click', async (e) => {
            const { lng, lat } = e.lngLat;
            
            // Call FastAPI Backend
            try {
                const response = await fetch('http://localhost:8000/analyze-disaster', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ lat, lng })
                });
                const data = await response.json();
                
                if (data.status === 'success') {
                    console.log("Optimal Route GeoJSON:", data.route);
                    // Add Mapbox layer rendering logic here for data.route
                }
            } catch (error) {
                console.error("Error connecting to TerraForm API:", error);
            }
        });
    });

    return (
        <div ref={mapContainer} style={{ width: '100vw', height: '100vh' }} />
    );
};

export default MapGlobe;