import React from 'react';

const LocalNewsPanel = ({ alert }) => {
    if (!alert) return null;

    return (
        <div style={{
            position: 'absolute',
            bottom: 30,
            left: 30,
            width: '350px',
            background: 'rgba(15, 20, 30, 0.85)',
            backdropFilter: 'blur(12px)',
            WebkitBackdropFilter: 'blur(12px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '16px',
            padding: '20px',
            color: '#fff',
            zIndex: 90,
            boxShadow: '0 10px 30px rgba(0,0,0,0.5)',
            animation: 'slideUp 0.4s ease-out'
        }}>
            <style>
                {`
                @keyframes slideUp {
                    from { transform: translateY(40px); opacity: 0; }
                    to { transform: translateY(0); opacity: 1; }
                }
                .pulse-dot {
                    width: 8px; height: 8px; background-color: #ff0b0b; border-radius: 50%;
                    animation: pulseNews 1.5s infinite; margin-right: 10px;
                }
                @keyframes pulseNews {
                    0% { box-shadow: 0 0 0 0 rgba(255, 11, 11, 0.7); }
                    70% { box-shadow: 0 0 0 10px rgba(255, 11, 11, 0); }
                    100% { box-shadow: 0 0 0 0 rgba(255, 11, 11, 0); }
                }
                `}
            </style>
            
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
                <div className="pulse-dot"></div>
                <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 'bold', letterSpacing: '1px', textTransform: 'uppercase' }}>Live Local Updates</h3>
            </div>
            
            <div style={{ background: 'rgba(255,255,255,0.05)', padding: '16px', borderRadius: '12px', borderLeft: '4px solid #ff0b0b' }}>
                <p style={{ margin: 0, fontSize: '14px', lineHeight: '1.6', opacity: 0.9 }}>
                    {alert.news}
                </p>
                <div style={{ marginTop: '12px', fontSize: '12px', opacity: 0.5 }}>
                    Source: Regional FEMA Dispatch
                </div>
            </div>
        </div>
    );
};

export default LocalNewsPanel;
