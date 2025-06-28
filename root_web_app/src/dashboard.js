import { useEffect, useState } from 'react';
import { get } from 'aws-amplify/api';

function Dashboard() {
    const [dashboardData, setDashboardData] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        populateDashboard(setDashboardData, setError);
    }, []);
    return (
        <div className="App">
            <div id="dashboard-container">
                {error && <p>Error al cargar el dashboard: {error}</p>}
                {!error && !dashboardData && <p>Cargando dashboard...</p>}
                {dashboardData && (
                    <iframe
                        src={dashboardData}
                        frameborder="0"
                        width="800"
                        height="600"
                        allowtransparency
                    />
                )}
            </div>
        </div>
    );
}

async function populateDashboard(setDashboardData, setError) {
    try {
        const dashCall = await get({
            apiName: 'tfm01api',
            path: '/dashboard'
        });
        const rawText = await dashCall.response;
        const responseWrapper = new Response(rawText.body);
        const data = await responseWrapper.json();
        setDashboardData(data);
    }
        catch (error) {
        setError(error.message);
        console.log('Error fetching dashboard:', error);
    }
}


export default Dashboard ;
