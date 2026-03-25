// Admin Dashboard Types

export interface User {
  id: string;
  username: string;
  email: string;
  role: 'superadmin' | 'support' | 'billing' | 'technical';
  profile: {
    firstName: string;
    lastName: string;
    department: string;
    phone: string;
  };
  permissions: string[];
  lastLogin: string;
  createdAt: string;
}

export interface Client {
  id: string;
  name: string;
  status: 'active' | 'inactive' | 'suspended' | 'trial';
  plan: 'starter' | 'professional' | 'enterprise';
  contact: {
    email: string;
    phone: string;
    address: string;
  };
  fleet: {
    totalRobots: number;
    activeRobots: number;
    idleRobots: number;
    maintenanceRobots: number;
  };
  warehouse: {
    name: string;
    location: string;
    totalArea: number;
    zones: number;
  };
  metrics: {
    tasksCompleted: number;
    uptime: number;
    lastActivity: string;
  };
  createdAt: string;
  subscription: {
    startDate: string;
    endDate: string;
    mrr: number;
  };
}

export interface Robot {
  id: string;
  clientId: string;
  clientName: string;
  name: string;
  type: 'humanoid' | 'mobile' | 'arm';
  status: 'idle' | 'busy' | 'charging' | 'maintenance' | 'offline';
  batteryPct: number;
  location: {
    zone: string;
    x: number;
    y: number;
  };
  currentTask?: {
    id: string;
    type: string;
    progress: number;
  };
  lastSeen: string;
}

export interface SystemHealth {
  overall: 'healthy' | 'degraded' | 'critical';
  services: {
    aiEngine: ServiceStatus;
    fleetControl: ServiceStatus;
    digitalTwin: ServiceStatus;
    eventProcessor: ServiceStatus;
    auth: ServiceStatus;
  };
  metrics: {
    totalRobots: number;
    activeClients: number;
    apiRequests: number;
    errorRate: number;
    avgResponseTime: number;
  };
  alerts: Alert[];
}

export interface ServiceStatus {
  status: 'healthy' | 'degraded' | 'down';
  uptime: number;
  lastChecked: string;
  responseTime: number;
}

export interface Alert {
  id: string;
  severity: 'critical' | 'warning' | 'info';
  message: string;
  source: string;
  clientId?: string;
  robotId?: string;
  createdAt: string;
  acknowledged: boolean;
}

export interface DashboardStats {
  totalClients: number;
  activeClients: number;
  trialClients: number;
  totalRobots: number;
  activeRobots: number;
  monthlyRevenue: number;
  systemUptime: number;
}
