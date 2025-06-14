import logo from './logo.svg';
import './App.css';
import {Amplify} from 'aws-amplify';
import awsconfig from './aws-exports';
import { Authenticator, withAuthenticator } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';

Amplify.configure(awsconfig);

function App() {
  return (
    <div className="App">
      <Authenticator>
        {({ signOut }) => (
        <header className="App-header">
          <h2>Testing App</h2>
          <button 
                onClick={signOut} 
                style={{ 
                  margin: '20px', 
                  fontSize: '0.8rem', 
                  padding: '5px 10px', 
                  marginTop: '20px'
                }}
              >
            Cerrar Sesión
          </button>
          
        </header>
        )}
      </Authenticator>
    </div>
  );
}

export default withAuthenticator(App);
