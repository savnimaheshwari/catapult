import React, { useState } from 'react';

const DisasterOverlay = ({ alert, onClose }) => {
    const [viewMode, setViewMode] = useState('pre'); // 'pre' or 'post'
    const [showBuildingOverlay, setShowBuildingOverlay] = useState(false);
    const [showHeatmap, setShowHeatmap] = useState(false);

    if (!alert) return null;

    // We simulate the xBD bounding boxes using basic CSS styling over the image for hackathon purposes
    return (
        <div style={{
            position: 'absolute',
            top: 20, right: 20, bottom: 20,
            width: '500px',
            background: 'rgba(11, 15, 25, 0.85)',
            backdropFilter: 'blur(16px)',
            WebkitBackdropFilter: 'blur(16px)',
            border: '1px solid rgba(255, 255, 255, 0.15)',
            borderRadius: '24px',
            boxShadow: '0 20px 40px rgba(0,0,0,0.5)',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            color: '#fff',
            zIndex: 100,
            animation: 'slideIn 0.4s cubic-bezier(0.16, 1, 0.3, 1)'
        }}>
            <style>
                {`
                @keyframes slideIn {
                    from { transform: translateX(120%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                .toggle-btn {
                    flex: 1; padding: 12px; border: none; cursor: pointer;
                    font-weight: 600; transition: 0.2s; font-size: 14px;
                }
                .active-toggle { background: #00ffcc; color: #000; }
                .inactive-toggle { background: rgba(255,255,255,0.1); color: #fff; }
                .filter-check { margin-right: 10px; cursor: pointer; }
                .filter-label { display: flex; alignItems: center; margin-bottom: 12px; cursor: pointer; font-size: 14px; }
                `}
            </style>

            <div style={{ padding: '24px', borderBottom: '1px solid rgba(255,255,255,0.1)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h2 style={{ margin: 0, fontSize: '24px', fontWeight: 'bold' }}>{alert.title}</h2>
                    <p style={{ margin: '4px 0 0 0', opacity: 0.7, fontSize: '14px' }}>xBD Imagery Analysis Dashboard</p>
                </div>
                <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#fff', fontSize: '28px', cursor: 'pointer', opacity: 0.7 }}>×</button>
            </div>

            <div style={{ flex: 1, position: 'relative', background: '#000' }}>
                <img 
                    src={viewMode === 'pre' ? alert.images.pre : alert.images.post} 
                    alt="Satellite View" 
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
                
                {/* Simulated Solaris Building Overlays */}
                {showBuildingOverlay && (
                    <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none' }}>
                        <div style={{ position: 'absolute', top: '40%', left: '30%', width: '40px', height: '40px', border: viewMode === 'post' ? '2px solid #ff0b0b' : '2px solid #00ffcc', backgroundColor: viewMode === 'post' ? 'rgba(255,11,11,0.3)' : 'rgba(0,255,204,0.3)' }}></div>
                        <div style={{ position: 'absolute', top: '60%', left: '50%', width: '35px', height: '25px', border: viewMode === 'post' ? '2px solid #ff0b0b' : '2px solid #00ffcc', backgroundColor: viewMode === 'post' ? 'rgba(255,11,11,0.3)' : 'rgba(0,255,204,0.3)' }}></div>
                        <div style={{ position: 'absolute', top: '20%', left: '60%', width: '50px', height: '45px', border: viewMode === 'post' ? '2px solid #ffaa00' : '2px solid #00ffcc', backgroundColor: viewMode === 'post' ? 'rgba(255,170,0,0.3)' : 'rgba(0,255,204,0.3)' }}></div>
                    </div>
                )}

                {/* Simulated Heatmap Overlay */}
                {showHeatmap && viewMode === 'post' && (
                    <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none', background: 'radial-gradient(circle at 45% 55%, rgba(255,0,0,0.4) 0%, rgba(255,0,0,0) 40%)' }}></div>
                )}
            </div>

            <div style={{ padding: '24px' }}>
                <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', borderRadius: '8px', overflow: 'hidden' }}>
                    <button className={`toggle-btn ${viewMode === 'pre' ? 'active-toggle' : 'inactive-toggle'}`} onClick={() => setViewMode('pre')}>
                        PRE-DISASTER
                    </button>
                    <button className={`toggle-btn ${viewMode === 'post' ? 'active-toggle' : 'inactive-toggle'}`} onClick={() => setViewMode('post')}>
                        POST-DISASTER
                    </button>
                </div>

                <div style={{ background: 'rgba(255,255,255,0.05)', padding: '16px', borderRadius: '12px' }}>
                    <h4 style={{ margin: '0 0 12px 0', opacity: 0.8 }}>ML Visualization Filters</h4>
                    <label className="filter-label">
                        <input type="checkbox" className="filter-check" checked={showBuildingOverlay} onChange={e => setShowBuildingOverlay(e.target.checked)} />
                        Show Solaris Building Overlays
                    </label>
                    <label className="filter-label" style={{ marginBottom: 0 }}>
                        <input type="checkbox" className="filter-check" checked={showHeatmap} onChange={e => setShowHeatmap(e.target.checked)} />
                        Show Damage Density Heatmap
                    </label>
                </div>
            </div>
        </div>
    );
};

export default DisasterOverlay;
