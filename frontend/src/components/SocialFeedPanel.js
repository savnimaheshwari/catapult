import React, { useState, useEffect } from 'react';
import axios from 'axios';

const SocialFeedPanel = ({ alert }) => {
    const [feed, setFeed] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!alert) {
            setFeed([]);
            return;
        }

        const fetchSocialFeed = async () => {
            setLoading(true);
            try {
                // Clean API call to our backend which aggregates social intel
                const response = await axios.get(`http://localhost:8000/social-feed/${alert.id}`);
                if (response.data.status === 'success') {
                    setFeed(response.data.feed);
                }
            } catch (err) {
                console.error("Failed to fetch social feed", err);
            } finally {
                setLoading(false);
            }
        };

        fetchSocialFeed();
    }, [alert]);

    if (!alert) return null;

    return (
        <div className="clean-panel" style={{
            position: 'absolute',
            top: 130,
            left: 30,
            bottom: 30,
            width: '380px',
            background: 'rgba(20, 25, 35, 0.95)',
            backdropFilter: 'blur(10px)',
            WebkitBackdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '16px',
            display: 'flex',
            flexDirection: 'column',
            color: '#fff',
            zIndex: 90,
            boxShadow: '0 10px 30px rgba(0,0,0,0.4)',
            animation: 'slideRight 0.3s ease-out',
            overflow: 'hidden'
        }}>
            <style>
                {`
                @keyframes slideRight {
                    from { transform: translateX(-30px); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                .scrollable-feed::-webkit-scrollbar {
                    width: 6px;
                }
                .scrollable-feed::-webkit-scrollbar-track {
                    background: rgba(0, 0, 0, 0.1);
                    border-radius: 10px;
                }
                .scrollable-feed::-webkit-scrollbar-thumb {
                    background: rgba(255, 255, 255, 0.2);
                    border-radius: 10px;
                }
                .feed-card {
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.05);
                    border-radius: 12px;
                    padding: 16px;
                    margin-bottom: 16px;
                    transition: border-color 0.2s, background 0.2s;
                }
                .feed-card:hover {
                    background: rgba(255, 255, 255, 0.08);
                    border-color: rgba(255, 255, 255, 0.15);
                }
                `}
            </style>
            
            <div style={{
                padding: '20px 24px', 
                borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
                background: 'rgba(255, 255, 255, 0.02)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
            }}>
                <h3 style={{ fontSize: '1.2rem', fontWeight: '600', margin: 0, color: '#fff' }}>
                    Social Media Updates
                </h3>
                <div style={{ fontSize: '0.8rem', color: '#ff6b6b', display: 'flex', alignItems: 'center', gap: '6px', fontWeight: '500' }}>
                    <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#ff6b6b', animation: 'pulseNews 2s infinite' }}></div>
                    LIVE
                </div>
            </div>
            
            <div className="scrollable-feed" style={{ padding: alert && (alert.id === 'harvey' || alert.id === 'florence') ? '12px' : '20px', overflowY: 'auto', flex: 1 }}>
                {loading ? (
                    <div style={{ textAlign: 'center', opacity: 0.5, padding: '40px 0' }}>Decrypting streams...</div>
                ) : feed.length === 0 ? (
                    <div style={{ textAlign: 'center', opacity: 0.5, padding: '40px 0' }}>No local intel available.</div>
                ) : alert && (alert.id === 'harvey' || alert.id === 'florence') ? (
                    // Harvey / Florence: show only full-width images, no text
                    feed.filter(item => item.image).map(item => (
                        <div key={item.id} style={{ marginBottom: '12px', borderRadius: '12px', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.1)' }}>
                            <img
                                src={item.image}
                                alt="Disaster imagery"
                                style={{ width: '100%', height: 'auto', display: 'block' }}
                            />
                        </div>
                    ))
                ) : (
                    feed.map(item => (
                        <div key={item.id} className="feed-card">
                            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
                                <img 
                                    src={item.avatar} 
                                    alt={item.author}
                                    style={{ width: '36px', height: '36px', borderRadius: '50%', objectFit: 'cover', border: '1px solid rgba(255,255,255,0.1)' }}
                                />
                                <div style={{ marginLeft: '12px' }}>
                                    <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: '600' }}>{item.author}</h4>
                                    <div style={{ fontSize: '0.75rem', opacity: 0.5, marginTop: '2px' }}>
                                        {item.platform} • {item.time}
                                    </div>
                                </div>
                            </div>
                            
                            <p style={{ margin: '0 0 12px 0', fontSize: '0.95rem', lineHeight: '1.5', color: 'rgba(255,255,255,0.9)' }}>
                                {item.content}
                            </p>
                            
                            {item.image && (
                                <div style={{ 
                                    width: '100%', 
                                    height: '160px', 
                                    borderRadius: '12px', 
                                    overflow: 'hidden',
                                    border: '1px solid rgba(255,255,255,0.1)'
                                }}>
                                    <img 
                                        src={item.image} 
                                        alt="Intel visual" 
                                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                    />
                                </div>
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default SocialFeedPanel;
