// Shared Types for Robot Fleet System

export interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'manager';
  permissions: string[];
  created_at: string;
  last_login: string;
}

export interface Robot {
  id: string;
  model: string;
  type: 'delivery' | 'security' | 'inspection' | 'maintenance';
  serial: string;
  status: 'active' | 'idle' | 'maintenance' | 'offline';
  battery_level: number;
  location: string;
  current_task?: string;
  capabilities: string[];
  specifications: {
    weight_capacity: string;
    battery_life: string;
    speed: string;
    navigation: string;
  };
  performance: {
    total_tasks: number;
    uptime: string;
    efficiency: number;
    error_rate: number;
  };
  last_maintenance: string;
  next_maintenance: string;
}

export interface Customer {
  id: string;
  name: string;
  company: string;
  email: string;
  phone: string;
  address: string;
  requirements: string;
  industry: string;
  status: 'active' | 'inactive' | 'trial';
  sales_stage: 'lead' | 'qualified' | 'proposal' | 'negotiation' | 'closed_won' | 'closed_lost';
  fleet_config?: FleetConfig;
  created_at: string;
  last_updated: string;
}

export interface FleetConfig {
  id: string;
  customer_id: string;
  configuration_name: string;
  industry: string;
  configuration_data: {
    environment_type: 'indoor' | 'outdoor' | 'mixed';
    robot_count: number;
    robot_types: RobotType[];
    network_config: NetworkConfig;
    safety_config: SafetyConfig;
    deployment_zones: DeploymentZone[];
    operational_hours: OperationalHours;
    maintenance_schedule: MaintenanceSchedule;
  };
  created_at: string;
  updated_at: string;
}

export interface RobotType {
  id: string;
  model: string;
  type: string;
  count: number;
  capabilities: string[];
  specifications: {
    weight_capacity: string;
    battery_life: string;
    speed: string;
    navigation: string;
  };
}

export interface NetworkConfig {
  ssid: string;
  security_type: string;
  frequency_band: string;
  mesh_network: boolean;
  failover_enabled: boolean;
}

export interface SafetyConfig {
  emergency_stop: boolean;
  obstacle_detection: boolean;
  speed_limits: {
    indoor: string;
    outdoor: string;
  };
  restricted_zones: any[];
  human_detection: boolean;
  collision_prevention: boolean;
}

export interface DeploymentZone {
  id: string;
  name: string;
  type: 'work' | 'charging' | 'maintenance' | 'restricted';
  coordinates: {
    x: number;
    y: number;
    z?: number;
  };
  boundaries: any[];
}

export interface OperationalHours {
  monday: DaySchedule;
  tuesday: DaySchedule;
  wednesday: DaySchedule;
  thursday: DaySchedule;
  friday: DaySchedule;
  saturday: DaySchedule;
  sunday: DaySchedule;
}

export interface DaySchedule {
  start: string;
  end: string;
  active: boolean;
}

export interface MaintenanceSchedule {
  frequency: string;
  tasks: any[];
  auto_scheduling: boolean;
  notification_preferences: {
    email: boolean;
    sms: boolean;
    dashboard: boolean;
  };
}

export interface ApiResponse<T> {
  data: T;
  message: string;
  success: boolean;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  has_next: boolean;
}
