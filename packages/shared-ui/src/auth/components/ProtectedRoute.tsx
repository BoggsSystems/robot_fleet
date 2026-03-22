import React from 'react';
import { AuthService } from '../services/authService';
import { UserRole, Permission } from '../types/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: UserRole;
  requiredPermission?: Permission;
  fallback?: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requiredRole, 
  requiredPermission,
  fallback = <div>Access Denied</div>
}) => {
  const authService = new AuthService();

  if (!authService.isAuthenticated()) {
    return <div>Please log in to access this page</div>;
  }

  if (requiredRole && !authService.isRole(requiredRole)) {
    return fallback;
  }

  if (requiredPermission && !authService.hasPermission(requiredPermission)) {
    return fallback;
  }

  return <>{children}</>;
};
