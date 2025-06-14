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
                
            </div>
        </div>
    );
}

async function populateDashboard() {
    console.log('populateDashboard called');
    const container = document.getElementById('dashboard-container');
    
    try {
        const session = await fetchAuthSession();
        console.log(session.tokens?.idToken.toString());
        const dashCall = await get({
            apiName: 'tfm-educ-app-api',
            path: '/dashboard',
            headers: {
                'authorization': session.tokens?.idToken.toString(),
                'Access-Control-Allow-Origin': 'https://web.d347kktgec41m0.amplifyapp.com',
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
