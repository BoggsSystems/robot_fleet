import api from './api';
import { Robot, RobotCommand, CommandResponse, Alert, AlertStatistics, ProcessingStats } from '../types/robot';

export const robotService = {
  async getAllRobots(): Promise<Record<string, Robot>> {
    const response = await api.get('/api/robots');
    return response.data;
  },

  async getRobot(robotId: string): Promise<Robot> {
    const response = await api.get(`/api/robots/${robotId}`);
    return response.data;
  },

  async sendCommand(robotId: string, command: RobotCommand): Promise<CommandResponse> {
    const response = await api.post(`/api/robots/${robotId}/commands`, command);
    return response.data;
  },
};

export const alertService = {
  async getAlerts(robotId?: string): Promise<Alert[]> {
    const params = robotId ? { robotId } : {};
    const response = await api.get('/api/alerts', { params });
    return response.data;
  },

  async acknowledgeAlert(alertId: string, notes?: string): Promise<void> {
    const response = await api.post(`/api/alerts/${alertId}/acknowledge`, {
      acknowledged: true,
      notes,
    });
    return response.data;
  },

  async resolveAlert(alertId: string): Promise<void> {
    const response = await api.post(`/api/alerts/${alertId}/resolve`);
    return response.data;
  },

  async getAlertStatistics(): Promise<AlertStatistics> {
    const response = await api.get('/api/alerts/statistics');
    return response.data;
  },
};

export const digitalTwinsService = {
  async getAllRobotTwins(): Promise<any[]> {
    const response = await api.get('/api/digitaltwins/robots');
    return response.data;
  },

  async getZoneTwins(): Promise<any[]> {
    const response = await api.get('/api/digitaltwins/zones');
    return response.data;
  },

  async getRobotsInZone(zoneId: string): Promise<any[]> {
    const response = await api.get(`/api/digitaltwins/zones/${zoneId}/robots`);
    return response.data;
  },

  async createTaskTwin(taskId: string, taskType: string, priority: number): Promise<any> {
    const response = await api.post('/api/digitaltwins/tasks', {
      taskId,
      taskType,
      priority,
    });
    return response.data;
  },
};

export const systemService = {
  async getStats(): Promise<ProcessingStats> {
    const response = await api.get('/api/stats');
    return response.data;
  },

  async getHealth(): Promise<any> {
    const response = await api.get('/health');
    return response.data;
  },
};
