import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Login } from './pages/Login';
import Dashboard from './pages/Dashboard';
import Fleet from './pages/Fleet';
import Locations from './pages/Locations';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';
import SetupPassword from './pages/SetupPassword';
import ResetPassword from './pages/ResetPassword';
import ForgotPassword from './pages/ForgotPassword';
import './styles/global.css';

const AppRoutes: React.FC = () => {
  const { isAuthenticated, user, isLoading } = useAuth();
  
  console.log('🔍 DEBUG: AppRoutes rendering');
  console.log('🔍 DEBUG: Auth state:', { isAuthenticated, isLoading, user });
  console.log('🔍 DEBUG: Current URL:', window.location.href);

  if (isLoading) {
    console.log('🔍 DEBUG: Still loading auth state...');
    return <div>Loading...</div>;
  }

  console.log('🔍 DEBUG: Auth state loaded, setting up routes');

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/setup-password"
        element={<SetupPassword />}
      />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/locations"
        element={
          <ProtectedRoute>
            <Locations />
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <Settings />
          </ProtectedRoute>
        }
      />
      <Route
        path=""
        element={
          (() => {
            console.log('🔍 DEBUG: Default route check - isAuthenticated:', isAuthenticated);
            const destination = isAuthenticated ? '/dashboard' : '/login';
            console.log('🔍 DEBUG: Navigating to:', destination);
            return <Navigate to={destination} />;
          })()
        }
      />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <AppRoutes />
      </Router>
    </AuthProvider>
  );
};

export default App;
