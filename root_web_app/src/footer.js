import React from 'react';

function Footer() {
    return (
        <footer style={{
            background: '#282c34',
            color: 'white',
            textAlign: 'center',
            padding: '16px 0',
            position: 'fixed',
            left: 0,
            bottom: 0,
            width: '100%',
            zIndex: 100
        }}>
            <div>
                Desarrollado por: Sebastián Mazo Vélez y Daniela Calderón &copy; 2025
            </div>
        </footer>
    );
}

export default Footer;