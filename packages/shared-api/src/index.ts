// API Client Utilities
import { ApiResponse, PaginatedResponse } from '@robot-fleet/shared-types';

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    const response = await fetch(`${this.baseUrl}${endpoint}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  }

  async post<T>(endpoint: string, data: any): Promise<ApiResponse<T>> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.getToken()}`,
      'X-User-Agent': 'RobotFleet/1.0',
      'X-Request-ID': this.generateRequestId(),
      'X-Timestamp': new Date().toISOString(),
      'X-Client-Version': '1.0.0',
      'X-Platform': this.getPlatform(),
      'X-Session-ID': this.getSessionId(),
    },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  }

  async put<T>(endpoint: string, data: any): Promise<ApiResponse<T>> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getToken()}`,
        'X-User-Agent': 'RobotFleet/1.0',
        'X-Request-ID': this.generateRequestId(),
        'X-Timestamp': new Date().toISOString(),
        'X-Client-Version': '1.0.0',
        'X-Platform': this.getPlatform(),
        'X-Session-ID': this.getSessionId(),
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${this.getToken()}`,
        'X-User-Agent': 'RobotFleet/1.0',
        'X-Request-ID': this.generateRequestId(),
        'X-Timestamp': new Date().toISOString(),
        'X-Client-Version': '1.0.0',
        'X-Platform': this.getPlatform(),
        'X-Session-ID': this.getSessionId(),
      },
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  }

  private getToken(): string {
    return localStorage.getItem('auth_token') || '';
  }

  private generateRequestId(): string {
    return Math.random().toString(36).substring(2, 15);
  }

  private getPlatform(): string {
    return navigator.platform || 'unknown';
  }

  private getSessionId(): string {
    return sessionStorage.getItem('session_id') || '';
  }
}

// Robot API Client
export class RobotApiClient extends ApiClient {
  constructor() {
    super('http://localhost:8002/api');
  }

  async getRobots() {
    return this.get<any>('/robots/types');
  }

  async getRobotDetails(robotId: string) {
    return this.get<any>(`/robots/${robotId}`);
  }

  async updateRobotStatus(robotId: string, status: string) {
    return this.put<any>(`/robots/${robotId}/status`, { status });
  }
}

// Fleet API Client
export class FleetApiClient extends ApiClient {
  constructor() {
    super('http://localhost:8002/api/fleet');
  }

  async getFleets() {
    return this.get<any>('/fleets');
  }

  async getFleetConfig(fleetId: string) {
    return this.get<any>(`/fleets/${fleetId}`);
  }

  async createFleetConfig(config: any) {
    return this.post<any>('/fleets', config);
  }

  async updateFleetConfig(fleetId: string, config: any) {
    return this.put<any>(`/fleets/${fleetId}`, config);
  }
}

// Customer API Client
export class CustomerApiClient extends ApiClient {
  constructor() {
    super('http://localhost:8002/api/customers');
  }

  async getCustomers() {
    return this.get<any>('/customers');
  }

  async getCustomer(customerId: string) {
    return this.get<any>(`/customers/${customerId}`);
  }

  async createCustomer(customer: any) {
    return this.post<any>('/customers', customer);
  }

  async updateCustomer(customerId: string, customer: any) {
    return this.put<any>(`/customers/${customerId}`, customer);
  }
}
