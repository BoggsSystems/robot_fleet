import { useState, useEffect } from 'react';

export type UserRole = 'admin' | 'client';

export interface ClientUser {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  company?: string;
  companyId?: string;
  avatar?: string;
  lastLogin?: string;
  createdAt: string;
}

export interface AuthToken {
  token: string;
  refreshToken: string;
  expiresAt: string;
  user: ClientUser;
}

// Mock client users database
const CLIENT_USERS: ClientUser[] = [
  {
    id: 'client-001',
    email: 's.mitchell@techcorp.com',
    name: 'Sarah Mitchell',
    role: 'client',
    company: 'TechCorp Industries',
    companyId: 'techcorp-001',
    avatar: '👩‍💼',
    lastLogin: '2024-03-15T10:30:00Z',
    createdAt: '2024-03-15T08:00:00Z',
  },
  {
    id: 'client-002',
    email: 'm.chen@globallogistics.com',
    name: 'Michael Chen',
    role: 'client',
    company: 'Global Logistics Inc',
    companyId: 'globallogistics-001',
    avatar: '👨‍💼',
    lastLogin: '2024-03-14T14:20:00Z',
    createdAt: '2024-03-14T09:00:00Z',
  },
  {
    id: 'client-003',
    email: 'e.rodriguez@healthfirst.com',
    name: 'Dr. Emily Rodriguez',
    role: 'client',
    company: 'HealthFirst Medical',
    companyId: 'healthfirst-001',
    avatar: '👩‍⚕️',
    lastLogin: '2024-03-13T16:45:00Z',
    createdAt: '2024-03-13T11:00:00Z',
  },
];

// Mock admin users
const ADMIN_USERS = [
  {
    id: 'admin-001',
    email: 'admin@robotfleet.com',
    name: 'System Administrator',
    role: 'admin' as UserRole,
    avatar: '👨‍💻',
    lastLogin: '2024-03-15T09:00:00Z',
    createdAt: '2024-01-01T00:00:00Z',
  },
];

export interface AuthContextType {
  user: ClientUser | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  hasRole: (role: UserRole) => boolean;
  canAccessCompany: (companyId: string) => boolean;
}

export function useAuth(): AuthContextType {
  const [user, setUser] = useState<ClientUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Check for existing session on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token');
    const storedUser = localStorage.getItem('auth_user');
    
    if (storedToken && storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        const parsedToken = JSON.parse(storedToken);
        
        // Check if token is expired
        if (new Date(parsedToken.expiresAt) > new Date()) {
          setUser(parsedUser);
          setToken(parsedToken.token);
        } else {
          // Token expired, clear storage
          localStorage.removeItem('auth_token');
          localStorage.removeItem('auth_user');
        }
      } catch (error) {
        console.error('Error parsing stored auth data:', error);
        localStorage.removeItem('auth_token');
        localStorage.removeItem('auth_user');
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    setIsLoading(true);

    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Check client users
      const clientUser = CLIENT_USERS.find(u => u.email === email);
      if (clientUser && password === 'demo123') {
        const authToken: AuthToken = {
          token: `client_token_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          refreshToken: `refresh_${Date.now()}`,
          expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(), // 24 hours
          user: clientUser,
        };

        // Store in localStorage
        localStorage.setItem('auth_token', JSON.stringify(authToken));
        localStorage.setItem('auth_user', JSON.stringify(clientUser));
        
        setUser(clientUser);
        setToken(authToken.token);
        setIsLoading(false);
        return true;
      }

      // Check admin users
      const adminUser = ADMIN_USERS.find(u => u.email === email);
      if (adminUser && password === 'admin123') {
        const authToken: AuthToken = {
          token: `admin_token_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          refreshToken: `refresh_${Date.now()}`,
          expiresAt: new Date(Date.now() + 8 * 60 * 60 * 1000).toISOString(), // 8 hours for admin
          user: adminUser,
        };

        localStorage.setItem('auth_token', JSON.stringify(authToken));
        localStorage.setItem('auth_user', JSON.stringify(adminUser));
        
        setUser(adminUser);
        setToken(authToken.token);
        setIsLoading(false);
        return true;
      }

      setIsLoading(false);
      return false;
    } catch (error) {
      console.error('Login error:', error);
      setIsLoading(false);
      return false;
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
  };

  const hasRole = (role: UserRole): boolean => {
    return user?.role === role;
  };

  const canAccessCompany = (companyId: string): boolean => {
    // Admins can access all companies
    if (user?.role === 'admin') return true;
    
    // Clients can only access their own company
    return user?.companyId === companyId;
  };

  return {
    user,
    token,
    isAuthenticated: !!user && !!token,
    isLoading,
    login,
    logout,
    hasRole,
    canAccessCompany,
  };
}

// Mock data for client fleets based on leads
export const getClientFleetData = (companyId: string) => {
  const fleetData: Record<string, any> = {
    'techcorp-001': {
      robots: [
        {
          id: 'R1-001',
          type: 'Unitree R1',
          category: 'Humanoid',
          status: 'active',
          battery: 87,
          zone: 'Assembly Line A',
          tasksCompleted: 1247,
          operatingHours: 342,
          lastMaintenance: '2024-03-10',
        },
        {
          id: 'R1-002',
          type: 'Unitree R1',
          category: 'Humanoid',
          status: 'active',
          battery: 92,
          zone: 'Assembly Line B',
          tasksCompleted: 1156,
          operatingHours: 328,
          lastMaintenance: '2024-03-12',
        },
        {
          id: 'R1-003',
          type: 'Unitree R1',
          category: 'Humanoid',
          status: 'active',
          battery: 78,
          zone: 'Quality Control',
          tasksCompleted: 987,
          operatingHours: 298,
          lastMaintenance: '2024-03-08',
        },
        {
          id: 'G2-001',
          type: 'Unitree Go2',
          category: 'Quadruped',
          status: 'active',
          battery: 95,
          zone: 'Warehouse Floor',
          tasksCompleted: 2134,
          operatingHours: 412,
          lastMaintenance: '2024-03-11',
        },
        {
          id: 'G2-002',
          type: 'Unitree Go2',
          category: 'Quadruped',
          status: 'maintenance',
          battery: 45,
          zone: 'Charging Station',
          tasksCompleted: 1876,
          operatingHours: 387,
          lastMaintenance: '2024-03-15',
        },
      ],
      metrics: {
        totalTasks: 7400,
        uptime: 99.2,
        efficiency: 94.8,
        costSavings: 12400,
        lastUpdate: '2024-03-15T15:30:00Z',
      },
    },
    'globallogistics-001': {
      robots: [
        {
          id: 'G2-003',
          type: 'Unitree Go2',
          category: 'Quadruped',
          status: 'active',
          battery: 88,
          zone: 'Loading Dock A',
          tasksCompleted: 1567,
          operatingHours: 287,
          lastMaintenance: '2024-03-09',
        },
        {
          id: 'G2-004',
          type: 'Unitree Go2',
          category: 'Quadruped',
          status: 'active',
          battery: 91,
          zone: 'Loading Dock B',
          tasksCompleted: 1432,
          operatingHours: 265,
          lastMaintenance: '2024-03-13',
        },
      ],
      metrics: {
        totalTasks: 2999,
        uptime: 98.7,
        efficiency: 91.3,
        costSavings: 8900,
        lastUpdate: '2024-03-14T16:45:00Z',
      },
    },
    'healthfirst-001': {
      robots: [
        {
          id: 'R1-004',
          type: 'Unitree R1',
          category: 'Humanoid',
          status: 'active',
          battery: 84,
          zone: 'Laboratory A',
          tasksCompleted: 892,
          operatingHours: 198,
          lastMaintenance: '2024-03-07',
        },
        {
          id: 'R1-005',
          type: 'Unitree R1',
          category: 'Humanoid',
          status: 'active',
          battery: 79,
          zone: 'Laboratory B',
          tasksCompleted: 756,
          operatingHours: 187,
          lastMaintenance: '2024-03-10',
        },
        {
          id: 'G2-005',
          type: 'Unitree Go2',
          category: 'Quadruped',
          status: 'active',
          battery: 93,
          zone: 'Reception Area',
          tasksCompleted: 1234,
          operatingHours: 234,
          lastMaintenance: '2024-03-12',
        },
      ],
      metrics: {
        totalTasks: 2882,
        uptime: 97.9,
        efficiency: 89.6,
        costSavings: 6700,
        lastUpdate: '2024-03-13T14:20:00Z',
      },
    },
  };

  return fleetData[companyId] || { robots: [], metrics: {} };
};
