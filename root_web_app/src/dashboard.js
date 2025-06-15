import { fetchAuthSession } from '@aws-amplify/auth';
import { useEffect } from 'react';
import { get } from 'aws-amplify/api';

function Dashboard() {

    useEffect(() => {
        populateDashboard();
    }, []);
    return (
        <div className="App">
            <div id="dashboard-container">
                <p> Cargando dashboard... </p>
            </div>
        </div>
    );
}

async function populateDashboard() {
    console.log('populateDashboard called');
    const container = document.getElementById('dashboard-container');
    const session = await fetchAuthSession();
    const jwt_token = session.tokens?.idToken.toString();
    try {
        
        const dashCall = await get({
            apiName: 'tfm-educ-app-api',
            path: '/dashboard',
            headers: {
                'authorization': `Bearer ${jwt_token}`,
                'Content-Type': 'application/json'
            }
        })
        const response = await dashCall.response;
        container.innerHTML = `<img src="${response.dashboard}" alt="Dashboard Image" />`;
        console.log('Dashboard image loaded successfully');

    }
    catch (error) {
        console.error('Error fetching dashboard:', error);
        container.innerHTML = '<p>Error generando Dashboard.</p>';
    }
}




export default Dashboard ;
