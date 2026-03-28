import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredPermission?: string;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requiredPermission 
}) => {
  const { isAuthenticated, user, isLoading } = useAuth();
  const location = useLocation();

  console.log('🔍 DEBUG: ProtectedRoute rendering');
  console.log('🔍 DEBUG: ProtectedRoute state:', { isAuthenticated, isLoading, user });
  console.log('🔍 DEBUG: Current path:', location.pathname);
  console.log('🔍 DEBUG: Required permission:', requiredPermission);

  if (isLoading) {
    console.log('🔍 DEBUG: ProtectedRoute - still loading...');
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        <div>Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    console.log('🔍 DEBUG: ProtectedRoute - not authenticated, redirecting to login');
    console.log('🔍 DEBUG: ProtectedRoute - redirecting from:', location.pathname);
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  console.log('🔍 DEBUG: ProtectedRoute - authenticated, checking permissions...');
  if (requiredPermission && user && !user.permissions.includes(requiredPermission)) {
    console.log('🔍 DEBUG: ProtectedRoute - permission denied for:', requiredPermission);
    return <Navigate to="/unauthorized" replace />;
  }

  console.log('🔍 DEBUG: ProtectedRoute - access granted, rendering children');
  return <>{children}</>;
};
