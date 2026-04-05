import React, { useState, useEffect } from 'react';
import { IDKitRequestWidget, deviceLegacy } from '@worldcoin/idkit';
import axios from 'axios';
import './WorldIDAuth.css';

/**
 * WorldIDAuth Component
 * Gated authentication layer using World ID 4.0.
 */
const WorldIDAuth = ({ children }) => {
    const [isVerified, setIsVerified] = useState(false);
    const [open, setOpen] = useState(false);
    const [rpContext, setRpContext] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Fetch the signed RP context from our backend on mount
    useEffect(() => {
        const fetchSignature = async () => {
            try {
                const response = await axios.post('http://localhost:8000/auth/world-id/prepare', {
                    action: 'verify-disaster-access'
                });
                
                // Construct the rp_context object for World ID 4.0
                setRpContext({
                    rp_id: response.data.rp_id,
                    nonce: response.data.nonce,
                    created_at: response.data.created_at,
                    expires_at: response.data.expires_at,
                    signature: response.data.sig
                });
                setLoading(false);
            } catch (err) {
                console.error('Failed to fetch RP signature:', err);
                setError('Authentication service unavailable. Please check backend.');
                setLoading(false);
            }
        };

        fetchSignature();
    }, []);

    const handleVerify = async (proof) => {
        try {
            const response = await axios.post('http://localhost:8000/verify-human', {
                ...proof,
                action: 'verify-disaster-access',
                verification_level: 'device' 
            });

            if (response.data.status === 'success') {
                console.log('Proof verified successfully!');
            } else {
                throw new Error('Verification failed on server');
            }
        } catch (err) {
            console.error('Verification error:', err);
            throw new Error(err.response?.data?.detail || 'Identity verification failed.');
        }
    };

    const onSuccess = (result) => {
        setIsVerified(true);
    };

    const simulateVerification = () => {
        setLoading(true);
        setTimeout(() => {
            setIsVerified(true);
            setLoading(false);
        }, 800); // Small delay to simulate processing
    };

    if (isVerified) {
        return children;
    }

    return (
        <div className="auth-overlay">
            <div className="auth-card">
                <div className="auth-logo">🌍</div>
                <h1>ProjectSendHelp</h1>
                <p>Emergency infrastructure gated by <strong>Proof-of-Human</strong>.</p>
                <p className="auth-subtext">Verification prevents bot spam and ensures authentic damage reporting.</p>
                
                {loading ? (
                    <div className="loader">Initializing Secure Session...</div>
                ) : error ? (
                    <div className="error-box">{error}</div>
                ) : (
                    <>
                        <IDKitRequestWidget
                            open={open}
                            onOpenChange={setOpen}
                            app_id={process.env.REACT_APP_APP_ID}
                            action="verify-disaster-access"
                            onSuccess={onSuccess}
                            handleVerify={handleVerify}
                            preset={deviceLegacy()}
                            rp_context={rpContext}
                        />
                        <button className="verify-btn" onClick={() => setOpen(true)}>
                            Verify with World ID
                        </button>
                        
                        <button className="simulate-btn" onClick={simulateVerification}>
                            Simulate Verification (Demo)
                        </button>
                    </>
                )}
                
                <div className="auth-footer">
                    Powered by <span>World ID 4.0</span>
                </div>
            </div>
        </div>
    );
};

export default WorldIDAuth;
