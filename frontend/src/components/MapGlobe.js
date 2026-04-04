import React, { useRef, useEffect, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import DisasterOverlay from './DisasterOverlay';
import LocalNewsPanel from './LocalNewsPanel';

// Note: Ensure mapbox token is set in .env as REACT_APP_MAPBOX_TOKEN
mapboxgl.accessToken = process.env.REACT_APP_MAPBOX_TOKEN || 'pk.ey...'; // Placeholder

const MapGlobe = () => {
    const mapContainer = useRef(null);
    const map = useRef(null);
    

    
    const [globalAlerts, setGlobalAlerts] = useState([]);
    const [selectedAlert, setSelectedAlert] = useState(null);

    // Fetch initial global alerts on mount
    useEffect(() => {
        const fetchAlerts = async () => {
            try {
                const res = await fetch('http://localhost:8000/global-alerts');
                const data = await res.json();
                if (data.status === 'success') {
                    setGlobalAlerts(data.alerts);
                }
            } catch (err) {
                console.error("Failed to fetch global alerts:", err);
            }
        };
        fetchAlerts();
    }, []);

    useEffect(() => {
        if (map.current) return; // initialize map only once
        
        map.current = new mapboxgl.Map({
            container: mapContainer.current,
            style: 'mapbox://styles/mapbox/satellite-streets-v12', // Realistic blue/green earth visual
            center: [-95.3698, 38.0], // Center somewhat around US
            zoom: 1,
            projection: 'globe' // Enable 3D Globe
        });

        map.current.on('style.load', () => {
            // Add Fog cinematic effect
            map.current.setFog({
                'color': 'rgb(20, 25, 35)',
                'high-color': 'rgb(20, 25, 35)',
                'horizon-blend': 0.05,
                'space-color': 'rgb(11, 11, 25)',
                'star-intensity': 0.6
            });
            // Keeping 3D buildings disabled as user requested top-down view for xBD images
        });
    }, []);

    // Generate pulse markers when globalAlerts arrive
    useEffect(() => {
        if (!map.current || globalAlerts.length === 0) return;

        globalAlerts.forEach(alert => {
            const el = document.createElement('div');
            el.className = 'beautiful-pulse-marker';
            
            el.addEventListener('click', () => {
                setSelectedAlert(alert);
                map.current.flyTo({
                    center: [alert.lng, alert.lat],
                    zoom: 16,
                    pitch: 0,
                    bearing: 0,
                    essential: true,
                    duration: 3000
                });
            });

            new mapboxgl.Marker(el)
                .setLngLat([alert.lng, alert.lat])
                .addTo(map.current);
        });
    }, [globalAlerts]);

    const closeOverlay = () => {
        setSelectedAlert(null);
        map.current.flyTo({
            zoom: 1.5,
            pitch: 0,
            essential: true,
            duration: 2500
        });
    };

    return (
        <div style={{ position: 'relative', width: '100%', height: '100vh', overflow: 'hidden' }}>
            <style>
                {`
                .beautiful-pulse-marker {
                    width: 20px;
                    height: 20px;
                    background-color: #ff0b0b;
                    border-radius: 50%;
                    cursor: pointer;
                    border: 3px solid #ffffff;
                    box-shadow: 0 0 0 0 rgba(255, 11, 11, 0.7);
                    animation: MapPulse 2s infinite cubic-bezier(0.66, 0, 0, 1);
                }
                @keyframes MapPulse {
                    to {
                        box-shadow: 0 0 0 45px rgba(255, 11, 11, 0);
                    }
                }
                `}
            </style>
            <div 
                ref={mapContainer} 
                style={{ width: '100%', height: '100%' }} 
            />
            
            {/* Base Header (always visible) */}
            <div style={{
                position: 'absolute',
                top: 20, left: 30,
                background: 'rgba(15, 20, 30, 0.75)',
                backdropFilter: 'blur(12px)',
                WebkitBackdropFilter: 'blur(12px)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                padding: '20px 30px',
                borderRadius: '16px',
                zIndex: 10,
                color: '#fff',
                boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
                pointerEvents: 'none' // Let clicks pass through if map is under
            }}>
                <h1 style={{ margin: '0', fontSize: '28px', fontWeight: 'bold', letterSpacing: '-0.5px' }}>
                    🌍 TerraForm <span style={{color: '#ff0b0b'}}>Alerts</span>
                </h1>
                <p style={{ margin: '8px 0 0 0', opacity: 0.8, fontSize: '15px' }}>
                    {selectedAlert ? "Viewing Satellite Intel" : "Select an active global disaster region to view xBD intelligence."}
                </p>
            </div>

            {/* Overlays rendered dynamically */}
            <LocalNewsPanel alert={selectedAlert} />
            <DisasterOverlay alert={selectedAlert} onClose={closeOverlay} />
            
        </div>
    );
};

export default MapGlobe;
