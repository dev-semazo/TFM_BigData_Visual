import { fetchAuthSession } from '@aws-amplify/auth';
import { useState, useEffect } from 'react';

function Dashboard() {

    useEffect(() => {
        populateDashboard();
    }, []);
    return (
        <div className="App">
            <div id="dashboard-container">
                
            </div>
        </div>
    );
}

async function populateDashboard() {
    console.log('populateDashboard called');
    const container = document.getElementById('dashboard-container');
    try {
        const session = await fetchAuthSession();
        /*
        const response = await fetch('https://example.com/api/dashboard', {
                method: 'GET',
                headers: {
                    Authorization: jwt,
                    'Content-Type': 'application/json'
                }
            }
        )
        setImgUrl(await response.json().url);
        */
        const data = { url: "https://via.placeholder.com/300x200.png?text=Dashboard+Image" };
        container.innerHTML = `<img src="${data.url}" alt="Dashboard Image" />`;
    }
    catch (error) {
        container.innerHTML = '<p>Error loading image.</p>';
    }
}




export default Dashboard ;
