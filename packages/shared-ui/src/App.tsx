import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { LoginForm } from './auth/components/LoginForm';
import { ProtectedRoute } from './auth/components/ProtectedRoute';
import { UserRole, Permission } from './auth/types/auth';
import { AuthService } from './auth/services/authService';

// Placeholder components for different dashboards
const SuperAdminDashboard = () => <div>Super Admin Dashboard</div>;
const ClientDashboard = () => <div>Client Dashboard</div>;
const OperatorDashboard = () => <div>Operator Dashboard</div>;
const ViewerDashboard = () => <div>Viewer Dashboard</div>;

function App() {
  const [user, setUser] = React.useState<any>(null);
  const [error, setError] = React.useState('');
  const authService = new AuthService();

  React.useEffect(() => {
    // Check if user is already logged in
    const storedUser = authService.getStoredUser();
    if (storedUser) {
      setUser(storedUser);
    }
  }, []);

  const handleLogin = (userData: any) => {
    setUser(userData);
    setError('');
  };

  const handleLogout = () => {
    authService.logout();
    setUser(null);
  };

  if (!user) {
    return (
      <div className="App">
        <LoginForm onLogin={handleLogin} onError={setError} />
        {error && <div className="error">{error}</div>}
      </div>
    );
  }

  return (
    <Router>
      <div className="App">
        <header>
          <h1>Robot Fleet Management</h1>
          <div className="user-info">
            <span>Welcome, {user.name}</span>
            <button onClick={handleLogout}>Logout</button>
          </div>
        </header>
        
        <main>
          <Routes>
            <Route 
              path="/super-admin" 
              element={
                <ProtectedRoute requiredRole={UserRole.SUPER_ADMIN}>
                  <SuperAdminDashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/client" 
              element={
                <ProtectedRoute requiredRole={UserRole.CLIENT_ADMIN}>
                  <ClientDashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/operator" 
              element={
                <ProtectedRoute requiredRole={UserRole.OPERATOR}>
                  <OperatorDashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/viewer" 
              element={
                <ProtectedRoute requiredRole={UserRole.VIEWER}>
                  <ViewerDashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/" 
              element={
                <Navigate to={
                  user.role === UserRole.SUPER_ADMIN ? '/super-admin' :
                  user.role === UserRole.CLIENT_ADMIN ? '/client' :
                  user.role === UserRole.OPERATOR ? '/operator' :
                  '/viewer'
                } replace 
              />
              } 
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
