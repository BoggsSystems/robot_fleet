import React, { createContext, useContext, useState, useCallback } from 'react';
import Cookies from 'js-cookie';
import { User } from '../types';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const login = useCallback(async (username: string, password: string) => {
    setIsLoading(true);
    // TODO: Replace with actual API call
    // Mock successful login for Phase 1
    const mockUser: User = {
      id: '1',
      username,
      email: 'admin@robotfleet.com',
      role: 'superadmin',
      profile: {
        firstName: 'Super',
        lastName: 'Admin',
        department: 'Management',
        phone: '+1-555-0100'
      },
      permissions: ['*'],
      lastLogin: new Date().toISOString(),
      createdAt: new Date().toISOString()
    };
    
    setUser(mockUser);
    Cookies.set('adminToken', 'mock-token', { expires: 1 });
    setIsLoading(false);
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    Cookies.remove('adminToken');
  }, []);

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated: !!user,
      isLoading,
      login,
      logout
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
