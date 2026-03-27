import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Clients from './pages/Clients';
import ClientDetail from './pages/ClientDetail';
import Fleet from './pages/Fleet';
import Users from './pages/Users';
import SystemHealth from './pages/SystemHealth';

console.log('🔍 App: App component imported successfully');

const App: React.FC = () => {
  console.log('🔍 App: App component starting...');
  
  // Always call hooks at the top level
  const { isAuthenticated, isLoading } = useAuth();
  
  try {
    console.log('🔍 App: Rendering App component');
    console.log('🔍 App: isAuthenticated:', isAuthenticated);
    console.log('🔍 App: isLoading:', isLoading);

    if (isLoading) {
      console.log('🔍 App: Showing loading state');
      return (
        <div style={{ 
          padding: '50px', 
          textAlign: 'center', 
          color: 'white', 
          backgroundColor: '#0f172a',
          fontFamily: 'monospace'
        }}>
          <h2>Loading Admin Dashboard...</h2>
          <p>Checking authentication...</p>
        </div>
      );
    }

    if (!isAuthenticated) {
      console.log('🔍 App: Showing Login component');
      return <Login />;
    }

    console.log('🔍 App: Showing authenticated app with Layout');
    return (
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/clients" element={<Clients />} />
          <Route path="/clients/:id" element={<ClientDetail />} />
          <Route path="/fleet" element={<Fleet />} />
          <Route path="/users" element={<Users />} />
          <Route path="/system" element={<SystemHealth />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    );
  } catch (error) {
    console.error('❌ App: Error in App component:', error);
    return (
      <div style={{ 
        padding: '50px', 
        textAlign: 'center', 
        color: 'white', 
        backgroundColor: '#0f172a',
        fontFamily: 'monospace'
      }}>
        <h2>App Component Error</h2>
        <p>Check browser console for details</p>
        <pre style={{ fontSize: '12px', textAlign: 'left' }}>
          {String(error)}
        </pre>
      </div>
    );
  }
};

export default App;
