import React, { useState, useEffect } from 'react';
import { systemAPI } from '../services/api';
import { SystemHealth, Alert } from '../types';

const SystemHealthPage: React.FC = () => {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchHealthData();
    const interval = setInterval(fetchHealthData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchHealthData = async () => {
    try {
      setLoading(true);
      
      const [healthRes, alertsRes] = await Promise.all([
        systemAPI.getHealth(),
        systemAPI.getAlerts({ acknowledged: false })
      ]);
      
      // Transform backend health format to frontend format
      setHealth({
        overall: healthRes.overall,
        services: {
          aiEngine: healthRes.services.ai_engine,
          fleetControl: healthRes.services.fleet_control,
          digitalTwin: healthRes.services.digital_twin,
          eventProcessor: healthRes.services.event_processor,
          auth: healthRes.services.auth
        },
        metrics: healthRes.metrics,
        alerts: []
      });
      
      setAlerts(alertsRes.alerts || []);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load system health');
    } finally {
      setLoading(false);
    }
  };

  const handleAcknowledgeAlert = async (alertId: string) => {
    try {
      await systemAPI.acknowledgeAlert(alertId);
      fetchHealthData();
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to acknowledge alert');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return '#22c55e';
      case 'degraded': return '#f59e0b';
      case 'down': return '#dc2626';
      default: return '#64748b';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#dc2626';
      case 'warning': return '#f59e0b';
      case 'info': return '#3b82f6';
      default: return '#64748b';
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8' }}>
        <div style={{ fontSize: '24px', marginBottom: '16px' }}>⏳</div>
        <p>Loading system health...</p>
      </div>
    );
  }

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
          <p style={{ color: '#dc2626', fontSize: '16px', marginBottom: '8px' }}>Error loading system health</p>
          <p style={{ color: '#94a3b8', fontSize: '14px' }}>{error}</p>
          <button 
            onClick={fetchHealthData}
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

  if (!health) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8' }}>
        <p>No health data available</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '32px' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: 700, color: '#f8fafc', marginBottom: '8px' }}>
          System Health
        </h1>
        <p style={{ fontSize: '16px', color: '#94a3b8' }}>
          Monitor backend services and infrastructure
        </p>
      </div>

      {/* Overall Status */}
      <div style={{ 
        backgroundColor: '#1e293b', 
        borderRadius: '12px', 
        border: '1px solid #334155',
        padding: '24px',
        marginBottom: '24px',
        display: 'flex',
        alignItems: 'center',
        gap: '16px'
      }}>
        <div style={{
          width: '24px',
          height: '24px',
          borderRadius: '50%',
          backgroundColor: getStatusColor(health.overall),
          boxShadow: `0 0 16px ${getStatusColor(health.overall)}`
        }} />
        <div>
          <p style={{ fontSize: '24px', fontWeight: 600, color: '#f8fafc', textTransform: 'capitalize' }}>
            System {health.overall}
          </p>
          <p style={{ fontSize: '14px', color: '#94a3b8' }}>
            All services operational • Last updated: {new Date().toLocaleTimeString()}
          </p>
        </div>
      </div>

      {/* Services Grid */}
      <div style={{ 
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '16px',
        marginBottom: '24px'
      }}>
        {Object.entries(health.services).map(([name, service]: [string, any]) => (
          <div key={name} style={{
            backgroundColor: '#1e293b',
            borderRadius: '12px',
            border: '1px solid #334155',
            padding: '20px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#f8fafc', textTransform: 'capitalize' }}>
                {name.replace(/([A-Z])/g, ' $1').trim()}
              </h3>
              <span style={{
                padding: '4px 12px',
                borderRadius: '20px',
                fontSize: '12px',
                fontWeight: 500,
                backgroundColor: `${getStatusColor(service.status)}20`,
                color: getStatusColor(service.status),
                textTransform: 'capitalize'
              }}>
                {service.status}
              </span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
              <div>
                <p style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>Uptime</p>
                <p style={{ fontSize: '16px', fontWeight: 500, color: '#f8fafc' }}>{service.uptime}%</p>
              </div>
              <div>
                <p style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>Response Time</p>
                <p style={{ fontSize: '16px', fontWeight: 500, color: '#f8fafc' }}>
                  {service.response_time_ms || service.responseTime}ms
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Metrics & Alerts */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        {/* System Metrics */}
        <div style={{ backgroundColor: '#1e293b', borderRadius: '12px', border: '1px solid #334155' }}>
          <div style={{ padding: '20px', borderBottom: '1px solid #334155' }}>
            <h2 style={{ fontSize: '18px', fontWeight: 600, color: '#f8fafc' }}>System Metrics</h2>
          </div>
          <div style={{ padding: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderBottom: '1px solid #334155' }}>
              <span style={{ fontSize: '14px', color: '#94a3b8' }}>Total Robots</span>
              <span style={{ fontSize: '16px', fontWeight: 500, color: '#f8fafc' }}>{health.metrics.total_robots}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderBottom: '1px solid #334155' }}>
              <span style={{ fontSize: '14px', color: '#94a3b8' }}>Active Clients</span>
              <span style={{ fontSize: '16px', fontWeight: 500, color: '#f8fafc' }}>{health.metrics.active_clients}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderBottom: '1px solid #334155' }}>
              <span style={{ fontSize: '14px', color: '#94a3b8' }}>API Requests</span>
              <span style={{ fontSize: '16px', fontWeight: 500, color: '#f8fafc' }}>{health.metrics.api_requests?.toLocaleString()}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderBottom: '1px solid #334155' }}>
              <span style={{ fontSize: '14px', color: '#94a3b8' }}>Error Rate</span>
              <span style={{ fontSize: '16px', fontWeight: 500, color: health.metrics.error_rate > 0.05 ? '#dc2626' : '#22c55e' }}>
                {(health.metrics.error_rate * 100).toFixed(2)}%
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0' }}>
              <span style={{ fontSize: '14px', color: '#94a3b8' }}>Avg Response Time</span>
              <span style={{ fontSize: '16px', fontWeight: 500, color: '#f8fafc' }}>{health.metrics.avg_response_time_ms}ms</span>
            </div>
          </div>
        </div>

        {/* Active Alerts */}
        <div style={{ backgroundColor: '#1e293b', borderRadius: '12px', border: '1px solid #334155' }}>
          <div style={{ padding: '20px', borderBottom: '1px solid #334155', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2 style={{ fontSize: '18px', fontWeight: 600, color: '#f8fafc' }}>Active Alerts</h2>
            <span style={{ padding: '4px 8px', backgroundColor: alerts.length > 0 ? '#dc2626' : '#22c55e', borderRadius: '12px', fontSize: '12px', color: 'white' }}>
              {alerts.length}
            </span>
          </div>
          <div style={{ maxHeight: '400px', overflow: 'auto' }}>
            {alerts.length === 0 ? (
              <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8' }}>
                <p>No active alerts</p>
              </div>
            ) : (
              alerts.map(alert => (
                <div key={alert.id} style={{ padding: '16px 20px', borderBottom: '1px solid #334155' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                    <span style={{
                      width: '8px',
                      height: '8px',
                      borderRadius: '50%',
                      backgroundColor: getSeverityColor(alert.severity)
                    }} />
                    <span style={{ fontSize: '12px', fontWeight: 500, color: getSeverityColor(alert.severity), textTransform: 'uppercase' }}>
                      {alert.severity}
                    </span>
                    <span style={{ fontSize: '12px', color: '#64748b' }}>• {alert.source}</span>
                  </div>
                  <p style={{ fontSize: '14px', color: '#e2e8f0', marginBottom: '8px' }}>{alert.message}</p>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <p style={{ fontSize: '12px', color: '#64748b' }}>
                      {new Date(alert.createdAt).toLocaleString()}
                    </p>
                    <button
                      onClick={() => handleAcknowledgeAlert(alert.id)}
                      style={{
                        padding: '4px 12px',
                        backgroundColor: '#3b82f620',
                        color: '#3b82f6',
                        border: 'none',
                        borderRadius: '4px',
                        fontSize: '12px',
                        cursor: 'pointer'
                      }}
                    >
                      Acknowledge
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemHealthPage;
