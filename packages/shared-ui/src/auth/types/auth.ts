export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  permissions: Permission[];
  clientId?: string;
  createdAt: string;
  lastLogin?: string;
  isActive: boolean;
  twoFactorEnabled: boolean;
}

export interface AuthResponse {
  token: string;
  user: User;
  expiresIn: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
  role?: UserRole;
  clientId?: string;
}

export enum UserRole {
  SUPER_ADMIN = 'super_admin',
  CLIENT_ADMIN = 'client_admin',
  OPERATOR = 'operator',
  VIEWER = 'viewer'
}

export enum Permission {
  // Super Admin permissions
  READ_ALL_FLEETS = 'read_all_fleets',
  WRITE_ALL_FLEETS = 'write_all_fleets',
  MANAGE_CLIENTS = 'manage_clients',
  SYSTEM_ADMIN = 'system_admin',
  
  // Client Admin permissions
  READ_OWN_FLEET = 'read_own_fleet',
  WRITE_OWN_FLEET = 'write_own_fleet',
  MANAGE_OPERATORS = 'manage_operators',
  VIEW_ANALYTICS = 'view_analytics',
  
  // Operator permissions
  CONTROL_ROBOTS = 'control_robots',
  VIEW_ROBOT_STATUS = 'view_robot_status',
  VIEW_SCHEDULE = 'view_schedule',
  
  // Viewer permissions
  READ_ONLY = 'read_only'
}
