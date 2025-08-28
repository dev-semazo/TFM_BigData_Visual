import './App.css';
import Dashboard from './dashboard';
import Control from './control';
import Header from './header';
import { Amplify } from 'aws-amplify';
import awsconfig from './aws-exports';
import { Authenticator, withAuthenticator } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';
import './App.css'
import Footer from './footer';

Amplify.configure(awsconfig)

function App() {
  return (
    <div className="App">
      <Authenticator>
        {({ signOut }) => (
        <main className="App-main"> 
          <Header signOut={signOut} />     
          <Dashboard/>
          <Control/>
        </main>
        
        )}
      </Authenticator>
      <Footer />
    </div>
  );
}

export default withAuthenticator(App);
