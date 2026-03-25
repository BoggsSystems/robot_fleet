import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Client, DashboardStats, SystemHealth } from '../types';
import { dashboardAPI, clientAPI, systemAPI } from '../services/api';

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
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [clients, setClients] = useState<Client[]>([]);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        const [statsRes, clientsRes, healthRes] = await Promise.all([
          dashboardAPI.getStats(),
          clientAPI.getClients(),
          systemAPI.getHealth()
        ]);
        
        setStats(statsRes);
        setClients(clientsRes.clients.slice(0, 5));
        
        const healthData = healthRes;
        setHealth({
          overall: healthData.overall,
          services: {
            aiEngine: healthData.services.ai_engine,
            fleetControl: healthData.services.fleet_control,
            digitalTwin: healthData.services.digital_twin,
            eventProcessor: healthData.services.event_processor,
            auth: healthData.services.auth
          },
          metrics: healthData.metrics,
          alerts: []
        });
        
        setError(null);
      } catch (err: any) {
        setError(err.response?.data?.error || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (error) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <div style={{ 
          backgroundColor: '#dc262620', 
          border: '1px solid #dc2626',
          borderRadius: '8px',
          padding: '20px',
          maxWidth: '500px',
          margin: '0 auto'
        }}>
          <p style={{ color: '#dc2626', fontSize: '16px', marginBottom: '8px' }}>Error loading dashboard</p>
          <p style={{ color: '#94a3b8', fontSize: '14px' }}>{error}</p>
          <button 
            onClick={() => window.location.reload()}
            style={{
              marginTop: '16px',
              padding: '8px 16px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer'
            }}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!stats || !health) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8' }}>
        <p>No data available</p>
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
        <StatCard label="Total Clients" value={stats.total_clients} trend="+2 this month" color="#3b82f6" />
        <StatCard label="Active Robots" value={`${stats.active_robots}/${stats.total_robots}`} color="#22c55e" />
        <StatCard label="Monthly Revenue" value={`$${stats.monthly_revenue.toLocaleString()}`} trend="+12% vs last month" color="#a855f7" />
        <StatCard label="System Uptime" value={`${stats.system_uptime}%`} color="#f59e0b" />
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
