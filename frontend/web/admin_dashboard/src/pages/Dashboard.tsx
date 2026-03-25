import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Client, Robot, DashboardStats, SystemHealth } from '../types';

// Mock data for Phase 1
const mockStats: DashboardStats = {
  totalClients: 12,
  activeClients: 8,
  trialClients: 3,
  totalRobots: 47,
  activeRobots: 38,
  monthlyRevenue: 28500,
  systemUptime: 99.8
};

const mockClients: Client[] = [
  {
    id: '1',
    name: 'Acme Distribution',
    status: 'active',
    plan: 'professional',
    contact: { email: 'admin@acme.com', phone: '+1-555-0101', address: '123 Main St, NY' },
    fleet: { totalRobots: 8, activeRobots: 6, idleRobots: 2, maintenanceRobots: 0 },
    warehouse: { name: 'NYC Distribution', location: 'New York, NY', totalArea: 50000, zones: 4 },
    metrics: { tasksCompleted: 1247, uptime: 98.5, lastActivity: '2024-01-15T10:30:00Z' },
    createdAt: '2023-08-01T00:00:00Z',
    subscription: { startDate: '2023-08-01', endDate: '2024-08-01', mrr: 5000 }
  },
  {
    id: '2',
    name: 'TechFlow Logistics',
    status: 'active',
    plan: 'enterprise',
    contact: { email: 'ops@techflow.com', phone: '+1-555-0102', address: '456 Tech Blvd, CA' },
    fleet: { totalRobots: 15, activeRobots: 12, idleRobots: 2, maintenanceRobots: 1 },
    warehouse: { name: 'SF Bay Hub', location: 'San Francisco, CA', totalArea: 100000, zones: 6 },
    metrics: { tasksCompleted: 3421, uptime: 99.1, lastActivity: '2024-01-15T09:45:00Z' },
    createdAt: '2023-06-15T00:00:00Z',
    subscription: { startDate: '2023-06-15', endDate: '2024-06-15', mrr: 12000 }
  },
  {
    id: '3',
    name: 'StartupXYZ',
    status: 'trial',
    plan: 'starter',
    contact: { email: 'hello@startupxyz.com', phone: '+1-555-0103', address: '789 Startup Ave, TX' },
    fleet: { totalRobots: 2, activeRobots: 2, idleRobots: 0, maintenanceRobots: 0 },
    warehouse: { name: 'Austin Mini-Warehouse', location: 'Austin, TX', totalArea: 15000, zones: 2 },
    metrics: { tasksCompleted: 89, uptime: 95.0, lastActivity: '2024-01-14T16:20:00Z' },
    createdAt: '2024-01-01T00:00:00Z',
    subscription: { startDate: '2024-01-01', endDate: '2024-02-01', mrr: 0 }
  }
];

const mockHealth: SystemHealth = {
  overall: 'healthy',
  services: {
    aiEngine: { status: 'healthy', uptime: 99.9, lastChecked: '2024-01-15T10:00:00Z', responseTime: 45 },
    fleetControl: { status: 'healthy', uptime: 99.8, lastChecked: '2024-01-15T10:00:00Z', responseTime: 32 },
    digitalTwin: { status: 'healthy', uptime: 99.9, lastChecked: '2024-01-15T10:00:00Z', responseTime: 28 },
    eventProcessor: { status: 'healthy', uptime: 99.7, lastChecked: '2024-01-15T10:00:00Z', responseTime: 15 },
    auth: { status: 'healthy', uptime: 100, lastChecked: '2024-01-15T10:00:00Z', responseTime: 12 }
  },
  metrics: {
    totalRobots: 47,
    activeClients: 8,
    apiRequests: 125000,
    errorRate: 0.02,
    avgResponseTime: 26
  },
  alerts: [
    { id: '1', severity: 'warning', message: 'Robot R-15 battery low (15%)', source: 'fleet-control', clientId: '2', robotId: 'R-15', createdAt: '2024-01-15T09:30:00Z', acknowledged: false },
    { id: '2', severity: 'info', message: 'Client trial expires in 7 days', source: 'billing', clientId: '3', createdAt: '2024-01-14T00:00:00Z', acknowledged: false }
  ]
};

const StatCard: React.FC<{ label: string; value: string | number; trend?: string; color: string }> = ({ label, value, trend, color }) => (
  <div style={{
    backgroundColor: '#1e293b',
    borderRadius: '12px',
    padding: '24px',
    border: '1px solid #334155'
  }}>
    <p style={{ fontSize: '14px', color: '#94a3b8', marginBottom: '8px' }}>{label}</p>
    <p style={{ fontSize: '32px', fontWeight: 700, color, marginBottom: '4px' }}>{value}</p>
    {trend && <p style={{ fontSize: '12px', color: '#22c55e' }}>{trend}</p>}
  </div>
);

const Dashboard: React.FC = () => {
  const [stats] = useState<DashboardStats>(mockStats);
  const [clients] = useState<Client[]>(mockClients);
  const [health] = useState<SystemHealth>(mockHealth);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate data loading
    setTimeout(() => setLoading(false), 500);
  }, []);

  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8' }}>
        <div style={{ fontSize: '24px', marginBottom: '16px' }}>⏳</div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '32px' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: 700, color: '#f8fafc', marginBottom: '8px' }}>
          SuperAdmin Dashboard
        </h1>
        <p style={{ fontSize: '16px', color: '#94a3b8' }}>
          Overview of all clients, fleet status, and system health
        </p>
      </div>

      {/* Stats Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '16px',
        marginBottom: '32px'
      }}>
        <StatCard label="Total Clients" value={stats.totalClients} trend="+2 this month" color="#3b82f6" />
        <StatCard label="Active Robots" value={`${stats.activeRobots}/${stats.totalRobots}`} color="#22c55e" />
        <StatCard label="Monthly Revenue" value={`$${stats.monthlyRevenue.toLocaleString()}`} trend="+12% vs last month" color="#a855f7" />
        <StatCard label="System Uptime" value={`${stats.systemUptime}%`} color="#f59e0b" />
      </div>

      {/* Two Column Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
        {/* Left Column - Clients & Fleet */}
        <div>
          {/* Recent Clients */}
          <div style={{ backgroundColor: '#1e293b', borderRadius: '12px', border: '1px solid #334155', marginBottom: '24px' }}>
            <div style={{ padding: '20px', borderBottom: '1px solid #334155', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 style={{ fontSize: '18px', fontWeight: 600, color: '#f8fafc' }}>Recent Clients</h2>
              <Link to="/clients" style={{ fontSize: '14px', color: '#3b82f6', textDecoration: 'none' }}>View All →</Link>
            </div>
            <div>
              {clients.map(client => (
                <div key={client.id} style={{ padding: '16px 20px', borderBottom: '1px solid #334155', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <p style={{ fontSize: '16px', fontWeight: 500, color: '#f8fafc' }}>{client.name}</p>
                    <p style={{ fontSize: '14px', color: '#94a3b8' }}>{client.warehouse.location} • {client.fleet.totalRobots} robots</p>
                  </div>
                  <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                    <span style={{
                      padding: '4px 12px',
                      borderRadius: '20px',
                      fontSize: '12px',
                      fontWeight: 500,
                      backgroundColor: client.status === 'active' ? '#22c55e20' : client.status === 'trial' ? '#3b82f620' : '#dc262620',
                      color: client.status === 'active' ? '#22c55e' : client.status === 'trial' ? '#3b82f6' : '#dc2626'
                    }}>
                      {client.status}
                    </span>
                    <span style={{ fontSize: '14px', color: '#94a3b8' }}>
                      {client.fleet.activeRobots}/{client.fleet.totalRobots} active
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div style={{ backgroundColor: '#1e293b', borderRadius: '12px', border: '1px solid #334155' }}>
            <div style={{ padding: '20px', borderBottom: '1px solid #334155' }}>
              <h2 style={{ fontSize: '18px', fontWeight: 600, color: '#f8fafc' }}>Quick Actions</h2>
            </div>
            <div style={{ padding: '20px', display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
              <Link to="/clients" style={{ padding: '16px', backgroundColor: '#0f172a', borderRadius: '8px', textDecoration: 'none', color: '#f8fafc', textAlign: 'center' }}>
                <div style={{ fontSize: '24px', marginBottom: '8px' }}>🏢</div>
                <p style={{ fontSize: '14px', fontWeight: 500 }}>Add Client</p>
              </Link>
              <Link to="/fleet" style={{ padding: '16px', backgroundColor: '#0f172a', borderRadius: '8px', textDecoration: 'none', color: '#f8fafc', textAlign: 'center' }}>
                <div style={{ fontSize: '24px', marginBottom: '8px' }}>🤖</div>
                <p style={{ fontSize: '14px', fontWeight: 500 }}>Assign Robots</p>
              </Link>
              <Link to="/system" style={{ padding: '16px', backgroundColor: '#0f172a', borderRadius: '8px', textDecoration: 'none', color: '#f8fafc', textAlign: 'center' }}>
                <div style={{ fontSize: '24px', marginBottom: '8px' }}>🔧</div>
                <p style={{ fontSize: '14px', fontWeight: 500 }}>System Status</p>
              </Link>
              <Link to="/users" style={{ padding: '16px', backgroundColor: '#0f172a', borderRadius: '8px', textDecoration: 'none', color: '#f8fafc', textAlign: 'center' }}>
                <div style={{ fontSize: '24px', marginBottom: '8px' }}>👥</div>
                <p style={{ fontSize: '14px', fontWeight: 500 }}>Manage Users</p>
              </Link>
            </div>
          </div>
        </div>

        {/* Right Column - System Health & Alerts */}
        <div>
          {/* System Health */}
          <div style={{ backgroundColor: '#1e293b', borderRadius: '12px', border: '1px solid #334155', marginBottom: '24px' }}>
            <div style={{ padding: '20px', borderBottom: '1px solid #334155' }}>
              <h2 style={{ fontSize: '18px', fontWeight: 600, color: '#f8fafc' }}>System Health</h2>
            </div>
            <div style={{ padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
                <div style={{
                  width: '16px',
                  height: '16px',
                  borderRadius: '50%',
                  backgroundColor: health.overall === 'healthy' ? '#22c55e' : health.overall === 'degraded' ? '#f59e0b' : '#dc2626',
                  boxShadow: `0 0 12px ${health.overall === 'healthy' ? '#22c55e' : health.overall === 'degraded' ? '#f59e0b' : '#dc2626'}`
                }} />
                <span style={{ fontSize: '18px', fontWeight: 600, color: '#f8fafc', textTransform: 'capitalize' }}>
                  {health.overall}
                </span>
              </div>

              {Object.entries(health.services).map(([name, status]) => (
                <div key={name} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: '1px solid #334155' }}>
                  <span style={{ fontSize: '14px', color: '#94a3b8', textTransform: 'capitalize' }}>
                    {name.replace(/([A-Z])/g, ' $1').trim()}
                  </span>
                  <span style={{
                    fontSize: '12px',
                    fontWeight: 500,
                    color: status.status === 'healthy' ? '#22c55e' : status.status === 'degraded' ? '#f59e0b' : '#dc2626'
                  }}>
                    {status.status} ({status.responseTime}ms)
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Alerts */}
          <div style={{ backgroundColor: '#1e293b', borderRadius: '12px', border: '1px solid #334155' }}>
            <div style={{ padding: '20px', borderBottom: '1px solid #334155', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 style={{ fontSize: '18px', fontWeight: 600, color: '#f8fafc' }}>Active Alerts</h2>
              <span style={{ padding: '4px 8px', backgroundColor: '#dc2626', borderRadius: '12px', fontSize: '12px', color: 'white' }}>
                {health.alerts.length}
              </span>
            </div>
            <div>
              {health.alerts.map(alert => (
                <div key={alert.id} style={{ padding: '16px 20px', borderBottom: '1px solid #334155' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <span style={{
                      width: '8px',
                      height: '8px',
                      borderRadius: '50%',
                      backgroundColor: alert.severity === 'critical' ? '#dc2626' : alert.severity === 'warning' ? '#f59e0b' : '#3b82f6'
                    }} />
                    <span style={{ fontSize: '12px', fontWeight: 500, color: '#94a3b8', textTransform: 'uppercase' }}>
                      {alert.severity}
                    </span>
                  </div>
                  <p style={{ fontSize: '14px', color: '#e2e8f0', marginBottom: '4px' }}>{alert.message}</p>
                  <p style={{ fontSize: '12px', color: '#64748b' }}>
                    {new Date(alert.createdAt).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
