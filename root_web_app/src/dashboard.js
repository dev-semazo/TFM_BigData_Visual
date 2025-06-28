import { useEffect, useState } from 'react';
import { secret } from '@aws-amplify/backend';

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
        const jwt = require("jsonwebtoken");
        const METABASE_SITE_URL = "http://ec2-54-166-177-96.compute-1.amazonaws.com:3000/";
        const METABASE_SECRET_KEY = secret('METABASE_SECRET_KEY');
        const payload = {
        resource: { dashboard: 2 },
        params: {},
        exp: Math.round(Date.now() / 1000) + (10 * 60) // 10 minute expiration
        };
        const token = jwt.sign(payload, METABASE_SECRET_KEY);

        const iframeUrl = METABASE_SITE_URL + "/embed/dashboard/" + token +
        "#bordered=true&titled=true";
        setDashboardData(iframeUrl);
    }
        catch (error) {
        setError(error.message);
        console.log('Error fetching dashboard:', error);
    }
}


export default Dashboard ;
