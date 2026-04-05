import React, { useState, useEffect } from 'react';
import axios from 'axios';

const SocialFeedPanel = ({ alert }) => {
    const [feed, setFeed] = useState([]);
    const [loading, setLoading] = useState(false);
    const [isMinimized, setIsMinimized] = useState(false);

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
            bottom: 30,
            left: 30,
            width: isMinimized ? '280px' : '380px',
            height: isMinimized ? '58px' : 'calc(100vh - 160px)',
            transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
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
                padding: '16px 20px', 
                borderBottom: isMinimized ? 'none' : '1px solid rgba(255, 255, 255, 0.1)',
                background: 'rgba(255, 255, 255, 0.02)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                cursor: 'pointer'
            }} onClick={() => setIsMinimized(!isMinimized)}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: '600', margin: 0, color: '#fff', whiteSpace: 'nowrap' }}>
                    Live News Updates
                </h3>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <div style={{ fontSize: '0.8rem', color: '#ff6b6b', display: 'flex', alignItems: 'center', gap: '6px', fontWeight: '500' }}>
                        <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#ff6b6b', animation: 'pulseNews 2s infinite' }}></div>
                        LIVE
                    </div>
                    <span style={{ color: 'rgba(255,255,255,0.6)', fontWeight: 'bold', fontSize: '1.2rem', lineHeight: '1' }}>
                        {isMinimized ? '+' : '−'}
                    </span>
                </div>
            </div>
            
            {!isMinimized && (
                <div className="scrollable-feed" style={{ padding: '20px', overflowY: 'auto', flex: 1 }}>
                {loading ? (
                    <div style={{ textAlign: 'center', opacity: 0.5, padding: '40px 0' }}>Fetching latest news...</div>
                ) : feed.length === 0 ? (
                    <div style={{ textAlign: 'center', opacity: 0.5, padding: '40px 0' }}>No news updates available.</div>
                ) : (
                    feed.map(item => (
                        <div key={item.id} className="feed-card" style={{ padding: '16px' }}>
                            <div style={{ marginBottom: '8px' }}>
                                <span style={{ fontSize: '0.75rem', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#00ffcc', background: 'rgba(0, 255, 204, 0.1)', padding: '2px 8px', borderRadius: '4px' }}>
                                    {item.platform}
                                </span>
                                <span style={{ fontSize: '0.75rem', opacity: 0.5, marginLeft: '8px' }}>
                                    {item.time}
                                </span>
                            </div>
                            <h4 style={{ margin: '0 0 8px 0', fontSize: '1rem', fontWeight: '500', lineHeight: '1.4', color: '#fff' }}>
                                {item.title || item.content}
                            </h4>
                            {item.url && (
                                <a href={item.url} target="_blank" rel="noopener noreferrer" style={{
                                    display: 'inline-block',
                                    fontSize: '0.85rem',
                                    color: '#4fc3f7',
                                    textDecoration: 'none',
                                    marginTop: '4px',
                                    fontWeight: '500'
                                }}>
                                    Read Full Article →
                                </a>
                            )}
                        </div>
                    ))
                )}
            </div>
            )}
        </div>
    );
};

export default SocialFeedPanel;
