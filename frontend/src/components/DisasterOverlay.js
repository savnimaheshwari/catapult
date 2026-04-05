import React, { useState } from 'react';

const DisasterOverlay = ({ alert, onClose }) => {
    const [showBuildingOverlay, setShowBuildingOverlay] = useState(false);
    const [isMetadataOpen, setIsMetadataOpen] = useState(true);

    if (!alert) return null;

    const disasterTypeColor = {
        'Flooding': '#4fc3f7',
        'Wildfire (Fire)': '#ff7043',
        'Wildfire': '#ff7043',
        'Fire': '#ff7043',
    };
    const severityColor = disasterTypeColor[alert.metadata?.disaster_type] || '#00ffcc';

    return (
        <div style={{
            position: 'absolute',
            top: 20, right: 20, bottom: 20,
            width: '480px',
            background: 'rgba(8, 12, 22, 0.92)',
            backdropFilter: 'blur(20px)',
            WebkitBackdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.12)',
            borderRadius: '24px',
            boxShadow: '0 24px 60px rgba(0,0,0,0.6)',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            color: '#fff',
            zIndex: 100,
            animation: 'slideIn 0.4s cubic-bezier(0.16, 1, 0.3, 1)'
        }}>
            <style>{`
                @keyframes slideIn {
                    from { transform: translateX(120%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                .toggle-btn {
                    flex: 1; padding: 10px 0; border: none; cursor: pointer;
                    font-weight: 700; font-size: 11px; letter-spacing: 0.1em;
                    text-transform: uppercase; transition: all 0.2s;
                }
                .active-toggle {
                    background: #00ffcc; color: #000;
                }
                .inactive-toggle {
                    background: rgba(255,255,255,0.06); color: rgba(255,255,255,0.5);
                }
                .inactive-toggle:hover { background: rgba(255,255,255,0.1); color: #fff; }
                .meta-pill {
                    display: flex; flex-direction: column; gap: 2px;
                    background: rgba(255,255,255,0.04);
                    border: 1px solid rgba(255,255,255,0.08);
                    border-radius: 10px; padding: 10px 12px;
                }
                .meta-label { font-size: 10px; text-transform: uppercase; letter-spacing: 0.08em; opacity: 0.45; }
                .meta-value { font-size: 13px; font-weight: 600; color: #fff; }
                .filter-label { display: flex; align-items: center; gap: 10px; font-size: 13px; cursor: pointer; padding: 6px 0; opacity: 0.8; }
                .filter-label:hover { opacity: 1; }
            `}</style>

            {/* ── Header ── */}
            <div style={{ padding: '20px 24px 16px', borderBottom: '1px solid rgba(255,255,255,0.08)', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
                        <span style={{
                            background: severityColor, color: '#000',
                            fontSize: '10px', fontWeight: 800, letterSpacing: '0.1em',
                            padding: '3px 9px', borderRadius: '20px', textTransform: 'uppercase'
                        }}>
                            {alert.metadata?.disaster_type || 'DISASTER'}
                        </span>

                    </div>
                    <h2 style={{ margin: 0, fontSize: '22px', fontWeight: 700, lineHeight: 1.2 }}>{alert.title}</h2>
                    {alert.metadata?.location && (
                        <p style={{ margin: '4px 0 0 0', opacity: 0.5, fontSize: '13px' }}>
                            📍 {alert.metadata.location}
                        </p>
                    )}
                </div>
                <button onClick={onClose} style={{
                    background: 'rgba(255,255,255,0.08)', border: 'none', color: '#fff',
                    width: '32px', height: '32px', borderRadius: '50%', cursor: 'pointer',
                    fontSize: '18px', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    flexShrink: 0
                }}>×</button>
            </div>

            {/* ── Satellite Image (dynamic flex height) ── */}
            <div style={{ position: 'relative', width: '100%', aspectRatio: '1/1', background: '#000', overflow: 'hidden' }}>
                <img
                    key="post"
                    src={alert.images?.post}
                    alt={`post disaster satellite view`}
                    style={{ width: '100%', height: '100%', objectFit: 'contain', display: 'block' }}
                    onError={e => { e.target.style.display = 'none'; }}
                />

                {/* Building overlays */}
                {showBuildingOverlay && alert.metadata.building_bounds && (
                    <svg viewBox="0 0 1024 1024" style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none' }}>
                        {alert.metadata.building_bounds.map((polyString, idx) => (
                            <polygon key={idx} points={polyString} fill="rgba(255,77,77,0.2)" stroke="#ff4d4d" strokeWidth="1.5" />
                        ))}
                    </svg>
                )}

                {/* Image label badge */}
                <div style={{
                    position: 'absolute', bottom: '10px', left: '10px',
                    background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(6px)',
                    border: '1px solid rgba(255,255,255,0.15)',
                    borderRadius: '8px', padding: '4px 10px',
                    fontSize: '11px', fontWeight: 600, letterSpacing: '0.06em',
                    color: '#ff7043'
                }}>
                    ● LIVE SATELLITE FEED
                </div>
            </div>

            {/* ── Scrollable Bottom Section ── */}
            <div style={{ flexShrink: 0, overflowY: 'auto', padding: '16px 20px 20px' }}>

                {/* ML Filters */}
                <div style={{ marginBottom: '16px', background: 'rgba(255,255,255,0.04)', borderRadius: '12px', padding: '12px 16px' }}>
                    <div style={{ fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.1em', opacity: 0.4, marginBottom: '10px' }}>ML Visualization Filters</div>
                    <label className="filter-label" style={{ marginBottom: 0 }}>
                        <input type="checkbox" checked={showBuildingOverlay} onChange={e => setShowBuildingOverlay(e.target.checked)} style={{ accentColor: '#ff4d4d' }} />
                        AI Building Segmentation Mask
                    </label>
                </div>

                {/* First-Responder Metadata */}
                {alert.metadata && (
                    <div>
                        <div 
                            onClick={() => setIsMetadataOpen(!isMetadataOpen)}
                            style={{ 
                                fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.1em', opacity: 0.8, 
                                marginBottom: '10px', display: 'flex', justifyContent: 'space-between', 
                                alignItems: 'center', cursor: 'pointer', padding: '4px 0'
                            }}
                        >
                            <span>Metadata</span>
                            <span style={{ transform: isMetadataOpen ? 'rotate(180deg)' : 'none', transition: 'transform 0.3s ease' }}>
                                ▼
                            </span>
                        </div>
                        <div style={{ 
                            display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px',
                            maxHeight: isMetadataOpen ? '500px' : '0',
                            overflow: 'hidden',
                            transition: 'max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.4s ease',
                            opacity: isMetadataOpen ? 1 : 0
                        }}>
                            <div className="meta-pill" style={{ gridColumn: '1 / -1' }}>
                                <span className="meta-label">Capture Date</span>
                                <span className="meta-value">🗓 {alert.metadata.capture_date}</span>
                            </div>
                            <div className="meta-pill">
                                <span className="meta-label">Sensor</span>
                                <span className="meta-value">🛰 {alert.metadata.sensor}</span>
                            </div>
                            <div className="meta-pill">
                                <span className="meta-label">Structures Detected</span>
                                <span className="meta-value" style={{ color: severityColor }}>🏠 {alert.metadata.total_buildings}+</span>
                            </div>
                            <div className="meta-pill">
                                <span className="meta-label">Ground Resolution</span>
                                <span className="meta-value">{alert.metadata.gsd_m} m/px</span>
                            </div>
                            <div className="meta-pill">
                                <span className="meta-label">Image Coverage</span>
                                <span className="meta-value">{alert.metadata.image_dimensions_px}</span>
                            </div>
                            {alert.metadata.lng_range && alert.metadata.lat_range && (
                                <div className="meta-pill" style={{ gridColumn: '1 / -1' }}>
                                    <span className="meta-label">Area of Interest</span>
                                    <span className="meta-value" style={{ fontSize: '12px' }}>
                                        {alert.metadata.lat_range[0]}°N – {alert.metadata.lat_range[1]}°N &nbsp;|&nbsp; {alert.metadata.lng_range[0]}° – {alert.metadata.lng_range[1]}°
                                    </span>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default DisasterOverlay;
