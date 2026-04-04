import React, { useState, useEffect } from 'react';
import { IDKitRequestWidget, orbLegacy } from '@worldcoin/idkit';
import { signRequest } from '@worldcoin/idkit-core/signing';

const AuthWidget = ({ onVerifySuccess }) => {
    const [verified, setVerified] = useState(false);
    const [rpContext, setRpContext] = useState(null);

    // Hardcoded for demo/hackathon purposes to run purely locally
    const APP_ID = process.env.REACT_APP_WORLD_ID_APP_ID || "app_staging_placeholder";
    const RP_ID = process.env.REACT_APP_WORLD_ID_RP_ID || "rp_staging_placeholder";
    const ACTION = process.env.REACT_APP_WORLD_ID_ACTION || "my-action";
    const DUMMY_SIGNING_KEY = "0000000000000000000000000000000000000000000000000000000000000000"; // 32 byte hex

    useEffect(() => {
        // Generate RP signature locally for demo bypass.
        // NOTE: In production, NEVER store RP_SIGNING_KEY on frontend.
        try {
            const sigData = signRequest({
                signingKeyHex: process.env.REACT_APP_RP_SIGNING_KEY || DUMMY_SIGNING_KEY,
                action: ACTION,
            });
            
            setRpContext({
                rp_id: RP_ID,
                nonce: sigData.nonce,
                created_at: sigData.createdAt,
                expires_at: sigData.expiresAt,
                signature: sigData.sig,
            });
        } catch (e) {
            console.error("Local signing failed:", e);
        }
    }, [ACTION, RP_ID]);

    const handleVerify = async (result) => {
        try {
            // Forward payload to FastAPI backend
            const res = await fetch('http://localhost:8000/verify-human', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    rp_id: rpContext.rp_id,
                    idkitResponse: result
                })
            });
            const data = await res.json();
            if (data.status !== 'success') {
                throw new Error("Backend verification failed");
            }
        } catch (error) {
            console.error("Verification failed", error);
            throw error;
        }
    };

    if (verified) {
        return (
            <div style={{ position:'absolute', top: 30, right: 30, zIndex: 10, background: 'rgba(15, 20, 30, 0.75)', backdropFilter: 'blur(12px)', WebkitBackdropFilter: 'blur(12px)', border: '1px solid rgba(255, 255, 255, 0.1)', padding: '12px 24px', borderRadius: '16px', color: '#00ffcc', fontWeight: 'bold' }}>
                ✓ Human Verified
            </div>
        );
    }

    if (!rpContext) return null;

    return (
        <div style={{ position:'absolute', top: 30, right: 30, zIndex: 10 }}>
            <IDKitRequestWidget
                app_id={APP_ID}
                action={ACTION}
                rp_context={rpContext}
                allow_legacy_proofs={true}
                preset={orbLegacy({ signal: "terraform-demo" })}
                handleVerify={handleVerify}
                onSuccess={(result) => {
                    console.log('Successfully verified', result);
                    setVerified(true);
                    if (onVerifySuccess) onVerifySuccess();
                }}
            >
                {({ open }) => (
                    <button 
                        onClick={open}
                        style={{
                            backgroundColor: '#ffffff',
                            color: '#0b0b1b',
                            border: 'none',
                            padding: '14px 28px',
                            borderRadius: '12px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            boxShadow: '0 8px 32px 0 rgba(255, 255, 255, 0.15)',
                            transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                            fontSize: '15px'
                        }}
                        onMouseOver={(e) => {
                            e.target.style.transform = 'translateY(-2px)';
                            e.target.style.boxShadow = '0 12px 40px 0 rgba(255, 255, 255, 0.2)';
                        }}
                        onMouseOut={(e) => {
                            e.target.style.transform = 'translateY(0)';
                            e.target.style.boxShadow = '0 8px 32px 0 rgba(255, 255, 255, 0.15)';
                        }}
                    >
                        Verify with World ID
                    </button>
                )}
            </IDKitRequestWidget>
        </div>
    );
};

export default AuthWidget;
