import './App.css';
import Dashboard from './dashboard';
import Header from './header';
import { Amplify } from 'aws-amplify';
import awsconfig from './aws-exports';
import { Authenticator, withAuthenticator } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';

Amplify.configure(awsconfig)
const existingConfig = Amplify.getConfig();
Amplify.configure({ 
  ...existingConfig, 
  API: {
    ...existingConfig.API,
    REST: {
      ...existingConfig.API?.REST,
      'tfm-educ-app-api': {
        endpoint: 'https://dy00ztk93a.execute-api.us-east-1.amazonaws.com/prod',
        region: 'us-east-1',
      }
    }
  },
});

function App() {
  return (
    <div className="App">
      <Authenticator>
        {({ signOut }) => (
        <main className="App-main">
          <Header />
          <Dashboard />
          <button onClick={signOut} id="logoutbutton">Cerrar Sesión</button>
        </main>
        )}
      </Authenticator>
    </div>
  );
}

export default withAuthenticator(App);
