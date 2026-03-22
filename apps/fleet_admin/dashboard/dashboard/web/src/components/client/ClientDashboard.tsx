import { useState, useEffect } from 'react';
import { Bot, Battery, Activity, TrendingUp, Clock, DollarSign, AlertTriangle, CheckCircle } from 'lucide-react';
import { useAuth, getClientFleetData } from '../../hooks/useAuth';
import './ClientDashboard.css';

export function ClientDashboard() {
  const { user, logout, hasRole } = useAuth();
  const [selectedView, setSelectedView] = useState<'overview' | 'robots' | 'analytics' | 'settings'>('overview');
  const [fleetData, setFleetData] = useState<any>(null);

  useEffect(() => {
    if (user?.companyId) {
      setFleetData(getClientFleetData(user.companyId));
    }
  }, [user]);

  if (!user || !hasRole('client')) {
    return (
      <div className="client-dashboard">
        <div className="access-denied">
          <AlertTriangle size={48} />
          <h2>Access Denied</h2>
          <p>You must be logged in as a client to access this dashboard.</p>
        </div>
      </div>
    );
  }

  const renderOverview = () => (
    <div className="dashboard-overview">
      <div className="welcome-section">
        <div className="user-avatar">{user.avatar}</div>
        <div className="user-info">
          <h1>Welcome back, {user.name}!</h1>
          <p>{user.company} • Client Dashboard</p>
        </div>
      </div>

      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">
            <Bot size={24} />
          </div>
          <div className="metric-content">
            <span className="metric-number">{fleetData?.robots?.length || 0}</span>
            <span className="metric-label">Active Robots</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">
            <Battery size={24} />
          </div>
          <div className="metric-content">
            <span className="metric-number">{fleetData?.metrics?.uptime || 0}%</span>
            <span className="metric-label">System Uptime</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">
            <Activity size={24} />
          </div>
          <div className="metric-content">
            <span className="metric-number">{fleetData?.metrics?.totalTasks || 0}</span>
            <span className="metric-label">Tasks Completed</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">
            <DollarSign size={24} />
          </div>
          <div className="metric-content">
            <span className="metric-number">${fleetData?.metrics?.costSavings || 0}</span>
            <span className="metric-label">Monthly Savings</span>
          </div>
        </div>
      </div>

      <div className="quick-actions">
        <h3>Quick Actions</h3>
        <div className="action-grid">
          <button className="action-btn" onClick={() => setSelectedView('robots')}>
            <Bot size={20} />
            <span>Manage Fleet</span>
          </button>
          <button className="action-btn" onClick={() => setSelectedView('analytics')}>
            <TrendingUp size={20} />
            <span>View Analytics</span>
          </button>
          <button className="action-btn" onClick={() => setSelectedView('settings')}>
            <Clock size={20} />
            <span>Settings</span>
          </button>
        </div>
      </div>
    </div>
  );

  const renderRobots = () => (
    <div className="robots-view">
      <div className="view-header">
        <h2>Fleet Management</h2>
        <p>Monitor and manage your robot fleet</p>
      </div>

      <div className="robots-grid">
        {fleetData?.robots?.map((robot: any) => (
          <div key={robot.id} className="robot-card">
            <div className="robot-header">
              <div className="robot-type">
                <span className="type-icon">
                  {robot.category === 'Humanoid' ? '🤖' : '🐕'}
                </span>
                <div className="type-info">
                  <strong>{robot.type}</strong>
                  <span>{robot.category}</span>
                </div>
              </div>
              <div className={`status-badge ${robot.status}`}>
                {robot.status === 'active' ? (
                  <><CheckCircle size={12} /> Active</>
                ) : (
                  <><AlertTriangle size={12} /> {robot.status}</>
                )}
              </div>
            </div>

            <div className="robot-metrics">
              <div className="metric-row">
                <span>Battery</span>
                <div className="battery-indicator">
                  <Battery size={16} />
                  <span>{robot.battery}%</span>
                  <div
                    className="battery-bar"
                    style={{ width: `${robot.battery}%` }}
                  />
                </div>
              </div>

              <div className="metric-row">
                <span>Zone</span>
                <strong>{robot.zone}</strong>
              </div>

              <div className="metric-row">
                <span>Tasks</span>
                <strong>{robot.tasksCompleted.toLocaleString()}</strong>
              </div>

              <div className="metric-row">
                <span>Operating Hours</span>
                <strong>{robot.operatingHours}</strong>
              </div>

              <div className="metric-row">
                <span>Last Maintenance</span>
                <strong>{new Date(robot.lastMaintenance).toLocaleDateString()}</strong>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderAnalytics = () => (
    <div className="analytics-view">
      <div className="view-header">
        <h2>Performance Analytics</h2>
        <p>Track your fleet's efficiency and ROI</p>
      </div>

      <div className="analytics-grid">
        <div className="chart-card">
          <h3>Efficiency Trends</h3>
          <div className="chart-placeholder">
            <div className="chart-line" style={{ height: '60%' }} />
            <div className="chart-line" style={{ height: '75%' }} />
            <div className="chart-line" style={{ height: '85%' }} />
            <div className="chart-line" style={{ height: '90%' }} />
            <div className="chart-line" style={{ height: '95%' }} />
          </div>
          <div className="chart-labels">
            <span>Jan</span>
            <span>Feb</span>
            <span>Mar</span>
            <span>Apr</span>
            <span>May</span>
          </div>
        </div>

        <div className="stats-card">
          <h3>Performance Metrics</h3>
          <div className="stats-list">
            <div className="stat-item">
              <span>Overall Efficiency</span>
              <strong>{fleetData?.metrics?.efficiency || 0}%</strong>
            </div>
            <div className="stat-item">
              <span>System Uptime</span>
              <strong>{fleetData?.metrics?.uptime || 0}%</strong>
            </div>
            <div className="stat-item">
              <span>Cost Savings</span>
              <strong>${fleetData?.metrics?.costSavings || 0}/month</strong>
            </div>
            <div className="stat-item">
              <span>ROI Timeline</span>
              <strong>8 months</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSettings = () => (
    <div className="settings-view">
      <div className="view-header">
        <h2>Account Settings</h2>
        <p>Manage your client account and preferences</p>
      </div>

      <div className="settings-grid">
        <div className="settings-card">
          <h3>Profile Information</h3>
          <div className="profile-info">
            <div className="info-row">
              <span>Company</span>
              <strong>{user.company}</strong>
            </div>
            <div className="info-row">
              <span>Name</span>
              <strong>{user.name}</strong>
            </div>
            <div className="info-row">
              <span>Email</span>
              <strong>{user.email}</strong>
            </div>
            <div className="info-row">
              <span>Client ID</span>
              <strong>{user.companyId}</strong>
            </div>
          </div>
        </div>

        <div className="settings-card">
          <h3>Notification Preferences</h3>
          <div className="notification-settings">
            <label className="checkbox-label">
              <input type="checkbox" defaultChecked />
              <span>Email notifications for robot issues</span>
            </label>
            <label className="checkbox-label">
              <input type="checkbox" defaultChecked />
              <span>Weekly performance reports</span>
            </label>
            <label className="checkbox-label">
              <input type="checkbox" defaultChecked />
              <span>Maintenance reminders</span>
            </label>
          </div>
        </div>

        <div className="settings-card">
          <h3>Account Actions</h3>
          <div className="account-actions">
            <button className="btn-secondary">Download Data</button>
            <button className="btn-secondary">Export Reports</button>
            <button className="btn-danger" onClick={logout}>
              Sign Out
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (selectedView) {
      case 'overview':
        return renderOverview();
      case 'robots':
        return renderRobots();
      case 'analytics':
        return renderAnalytics();
      case 'settings':
        return renderSettings();
      default:
        return renderOverview();
    }
  };

  return (
    <div className="client-dashboard">
      <header className="client-header">
        <div className="header-left">
          <div className="user-avatar">{user.avatar}</div>
          <div className="user-info">
            <h1>{user.company}</h1>
            <span>Client Portal</span>
          </div>
        </div>
        
        <div className="header-right">
          <nav className="client-nav">
            <button 
              className={`nav-btn ${selectedView === 'overview' ? 'active' : ''}`}
              onClick={() => setSelectedView('overview')}
            >
              Overview
            </button>
            <button 
              className={`nav-btn ${selectedView === 'robots' ? 'active' : ''}`}
              onClick={() => setSelectedView('robots')}
            >
              Fleet
            </button>
            <button 
              className={`nav-btn ${selectedView === 'analytics' ? 'active' : ''}`}
              onClick={() => setSelectedView('analytics')}
            >
              Analytics
            </button>
            <button 
              className={`nav-btn ${selectedView === 'settings' ? 'active' : ''}`}
              onClick={() => setSelectedView('settings')}
            >
              Settings
            </button>
          </nav>
          
          <button className="logout-btn" onClick={logout}>
            Sign Out
          </button>
        </div>
      </header>

      <main className="client-main">
        {renderContent()}
      </main>
    </div>
  );
}
