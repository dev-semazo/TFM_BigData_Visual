import { useEffect, useState } from 'react';
import { get } from 'aws-amplify/api';

function Control_Panel() {
const [responseMsg, setResponseMsg] = useState('');
    const [showPopup, setShowPopup] = useState(false);

    const handleClick = async () => {
        try {
            const dashCall = await get({
                apiName: 'tfm01api',
                path: '/dashboard/execute_model/'
            });
            const rawText = await dashCall.response;
            const responseWrapper = new Response(rawText.body);
            const data = await responseWrapper.text();
            console.log('Respuesta del API:', data);
            setResponseMsg('Request realizado, ejecutando');
            setShowPopup(true);
        } catch (error) {
            setResponseMsg(`Error: ${error.message}`);
            setShowPopup(true);
            console.log('Error fetching dashboard:', error);
        }
    };

    const handleClosePopup = () => {
        setShowPopup(false);
        setResponseMsg('');
    };

    return (
        <div id="control-panel">
            <button onClick={handleClick}>Actualizar Modelo de Previsión</button>
            {showPopup && (
                <div style={{
                    position: 'fixed',
                    top: 0, left: 0, right: 0, bottom: 0,
                    background: 'rgba(0,0,0,0.3)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 1000
                }}>
                    <div style={{
                        background: '#fff',
                        padding: '24px 32px',
                        borderRadius: '8px',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
                        minWidth: '300px',
                        maxWidth: '90%',
                        textAlign: 'center',
                        position: 'relative'
                    }}>
                        <button
                            onClick={handleClosePopup}
                            style={{
                                position: 'absolute',
                                top: 8,
                                right: 12,
                                background: 'transparent',
                                border: 'none',
                                fontSize: 20,
                                cursor: 'pointer'
                            }}
                            aria-label="Cerrar"
                        >
                            ×
                        </button>
                        <div>{responseMsg}</div>
                    </div>
                </div>
            )}
        </div>
    );
}


export default Control_Panel ;