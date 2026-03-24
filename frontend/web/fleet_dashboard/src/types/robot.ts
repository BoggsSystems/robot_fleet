export interface Position {
  x: number;
  y: number;
  z: number;
}

export interface Robot {
  robotId: string;
  battery_level: number;
  status: string;
  temperature: number;
  position: Position;
  lastSeen: string;
  health_score?: number;
  connection_status?: string;
}

export interface Alert {
  id: string;
  robotId: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  timestamp: string;
  acknowledged: boolean;
  resolved: boolean;
  notes?: string;
}

export interface RobotCommand {
  command: string;
  parameters?: {
    x?: number;
    y?: number;
    z?: number;
    pose_id?: string;
    task_id?: string;
    type?: string;
  };
  commandId?: string;
  timestamp?: string;
}

export interface CommandResponse {
  success: boolean;
  commandId: string;
  robotId: string;
  command: RobotCommand;
  timestamp: string;
}

export interface AlertStatistics {
  total: number;
  active: number;
  acknowledged: number;
  resolved: number;
  bySeverity: {
    low: number;
    medium: number;
    high: number;
    critical: number;
  };
  byType: Record<string, number>;
}

export interface ProcessingStats {
  eventsProcessed: number;
  eventsPerSecond: number;
  totalCommands: number;
  successfulCommands: number;
  failedCommands: number;
  uptime: number;
  lastEventTime: string;
}
