import { useEffect, useState } from 'react';
import { get } from 'aws-amplify/api';

function Dashboard() {
    const [dashboardData, setDashboardData] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        populateDashboard(setDashboardData, setError);
    }, []);

    return (
        <div id="dashboard-container">
            {error && <p>Error al cargar el dashboard: {error}</p>}
            {!error && !dashboardData && <p>Cargando dashboard...</p>}
            {dashboardData && (
                <iframe
                    src={dashboardData}
                    title="Dashboard"
                    width="100%"
                    height="1000"
                    style={{ border: 0 }}
                    allowFullScreen
                />
            )}
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
