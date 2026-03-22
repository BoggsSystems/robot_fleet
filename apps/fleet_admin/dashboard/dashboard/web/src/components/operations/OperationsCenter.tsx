import { useState, useEffect } from 'react';
import { Activity, AlertTriangle, CheckCircle, Wifi, Battery, Camera, Terminal, ArrowRight, Play, Square, Download, Eye } from 'lucide-react';
import './OperationsCenter.css';

export type RobotHealth = {
  robotId: string;
  robotType: string;
  robotCategory: string;
  clientId: string;
  clientName: string;
  fleetId: string;
  fleetName: string;
  status: 'online' | 'offline' | 'warning' | 'error';
  battery: number;
  lastSeen: string;
  telemetry: {
    pose: { x: number; y: number; theta: number };
    temperature: number;
    cpuLoad: number;
    memoryUsage: number;
  };
  alerts: string[];
};

interface OperationsCenterProps {
  onCancel?: () => void;
}

const DEFAULT_ROBOTS: RobotHealth[] = [
  {
    robotId: 'unitree_warehouse_bot_01',
    robotType: 'unitree_r1',
    robotCategory: 'Humanoid',
    clientId: 'client_1',
    clientName: 'Acme Distribution',
    fleetId: 'fleet_1',
    fleetName: 'Warehouse Alpha',
    status: 'online',
    battery: 87,
    lastSeen: '2 min ago',
    telemetry: {
      pose: { x: 1.2, y: -0.5, theta: 45 },
      temperature: 42,
      cpuLoad: 35,
      memoryUsage: 62,
    },
    alerts: [],
  },
  {
    robotId: 'unitree_warehouse_bot_02',
    robotType: 'unitree_r1',
    robotCategory: 'Humanoid',
    clientId: 'client_1',
    clientName: 'Acme Distribution',
    fleetId: 'fleet_1',
    fleetName: 'Warehouse Alpha',
    status: 'warning',
    battery: 23,
    lastSeen: '5 min ago',
    telemetry: {
      pose: { x: -2.1, y: 1.3, theta: 180 },
      temperature: 48,
      cpuLoad: 72,
      memoryUsage: 81,
    },
    alerts: ['Battery below 25%', 'High CPU load'],
  },
  {
    robotId: 'techstart_g1_01',
    robotType: 'unitree_g1',
    robotCategory: 'Humanoid',
    clientId: 'client_2',
    clientName: 'TechStart Inc',
    fleetId: 'fleet_2',
    fleetName: 'Office Automation',
    status: 'online',
    battery: 94,
    lastSeen: '1 min ago',
    telemetry: {
      pose: { x: 0, y: 0, theta: 0 },
      temperature: 38,
      cpuLoad: 22,
      memoryUsage: 45,
    },
    alerts: [],
  },
  {
    robotId: 'techstart_go2_01',
    robotType: 'unitree_go2',
    robotCategory: 'Quadruped',
    clientId: 'client_2',
    clientName: 'TechStart Inc',
    fleetId: 'fleet_2',
    fleetName: 'Office Automation',
    status: 'offline',
    battery: 0,
    lastSeen: '2 hours ago',
    telemetry: {
      pose: { x: 0, y: 0, theta: 0 },
      temperature: 0,
      cpuLoad: 0,
      memoryUsage: 0,
    },
    alerts: ['Connection lost', 'Last seen 2 hours ago'],
  },
];

export function OperationsCenter({ onCancel }: OperationsCenterProps) {
  const [robots, setRobots] = useState<RobotHealth[]>([]);
  const [selectedRobot, setSelectedRobot] = useState<RobotHealth | null>(null);
  const [filter, setFilter] = useState<'all' | 'online' | 'warning' | 'offline'>('all');
  const [remoteSession, setRemoteSession] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem('operations_robots');
    if (stored) {
      setRobots(JSON.parse(stored));
    } else {
      setRobots(DEFAULT_ROBOTS);
      localStorage.setItem('operations_robots', JSON.stringify(DEFAULT_ROBOTS));
    }
  }, []);

  const stats = {
    total: robots.length,
    online: robots.filter(r => r.status === 'online').length,
    warning: robots.filter(r => r.status === 'warning').length,
    offline: robots.filter(r => r.status === 'offline' || r.status === 'error').length,
  };

  const filteredRobots = filter === 'all' 
    ? robots 
    : robots.filter(r => r.status === filter || (filter === 'offline' && r.status === 'error'));

  const getStatusIcon = (status: RobotHealth['status']) => {
    switch (status) {
      case 'online': return <CheckCircle size={16} className="status-online" />;
      case 'warning': return <AlertTriangle size={16} className="status-warning" />;
      case 'offline': return <Wifi size={16} className="status-offline" />;
      case 'error': return <AlertTriangle size={16} className="status-error" />;
    }
  };

  const getTypeIcon = (category: string) => {
    switch (category) {
      case 'Humanoid': return '🤖';
      case 'Quadruped': return '🐕';
      case 'Wheeled': return '🔄';
      default: return '⚙️';
    }
  };

  const getBatteryColor = (level: number) => {
    if (level > 50) return '#10b981';
    if (level > 25) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className="operations-center">
      {/* Header */}
      <div className="ops-header">
        <div>
          <h2>Remote Operations Center</h2>
          <p>Monitor and support all client robots</p>
        </div>
        <div className="ops-stats">
          <div className="stat-pill online">
            <span className="stat-dot" />
            {stats.online} Online
          </div>
          <div className="stat-pill warning">
            <span className="stat-dot" />
            {stats.warning} Warning
          </div>
          <div className="stat-pill offline">
            <span className="stat-dot" />
            {stats.offline} Offline
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="ops-filters">
        {(['all', 'online', 'warning', 'offline'] as const).map(f => (
          <button
            key={f}
            className={`ops-filter ${filter === f ? 'active' : ''}`}
            onClick={() => setFilter(f)}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
            <span className="count">
              {f === 'all' ? stats.total : stats[f]}
            </span>
          </button>
        ))}
      </div>

      {/* Robot Grid */}
      <div className="robot-grid">
        {filteredRobots.map(robot => (
          <div
            key={robot.robotId}
            className={`robot-card ${robot.status} ${selectedRobot?.robotId === robot.robotId ? 'selected' : ''}`}
            onClick={() => setSelectedRobot(robot)}
          >
            <div className="card-header">
              <div className="robot-identity">
                <span className="type-icon">{getTypeIcon(robot.robotCategory)}</span>
                <div>
                  <h4>{robot.robotId}</h4>
                  <span className="client-name">{robot.clientName}</span>
                </div>
              </div>
              {getStatusIcon(robot.status)}
            </div>

            <div className="card-fleet">
              <span className="fleet-badge">{robot.fleetName}</span>
            </div>

            <div className="card-metrics">
              <div className="metric">
                <Battery size={14} style={{ color: getBatteryColor(robot.battery) }} />
                <span style={{ color: getBatteryColor(robot.battery) }}>{robot.battery}%</span>
              </div>
              <div className="metric">
                <Activity size={14} />
                <span>{robot.telemetry.cpuLoad}% CPU</span>
              </div>
              <div className="metric">
                <span className="temp-icon">🌡️</span>
                <span>{robot.telemetry.temperature}°C</span>
              </div>
            </div>

            <div className="card-footer">
              <span className="last-seen">{robot.lastSeen}</span>
              {robot.alerts.length > 0 && (
                <span className="alert-count">
                  <AlertTriangle size={12} />
                  {robot.alerts.length}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Remote Control Panel */}
      {selectedRobot && (
        <div className="remote-panel">
          <div className="panel-header">
            <div className="panel-title">
              <span className="panel-icon">{getTypeIcon(selectedRobot.robotCategory)}</span>
              <div>
                <h3>{selectedRobot.robotId}</h3>
                <p>{selectedRobot.clientName} • {selectedRobot.fleetName}</p>
              </div>
            </div>
            <div className="panel-actions">
              <button
                className={`btn-remote ${remoteSession ? 'active' : ''}`}
                onClick={() => setRemoteSession(!remoteSession)}
              >
                {remoteSession ? (
                  <><Square size={14} /> End Session</>
                ) : (
                  <><Play size={14} /> Remote Control</>
                )}
              </button>
              <button className="btn-icon" onClick={() => setSelectedRobot(null)}>
                ×
              </button>
            </div>
          </div>

          <div className="panel-content">
            {/* Telemetry */}
            <div className="telemetry-section">
              <h4>Live Telemetry</h4>
              <div className="telemetry-grid">
                <div className="telemetry-item">
                  <label>Battery</label>
                  <div className="battery-bar">
                    <div 
                      className="battery-fill" 
                      style={{ 
                        width: `${selectedRobot.battery}%`,
                        backgroundColor: getBatteryColor(selectedRobot.battery)
                      }}
                    />
                    <span>{selectedRobot.battery}%</span>
                  </div>
                </div>
                <div className="telemetry-item">
                  <label>CPU Load</label>
                  <span className="value">{selectedRobot.telemetry.cpuLoad}%</span>
                </div>
                <div className="telemetry-item">
                  <label>Memory</label>
                  <span className="value">{selectedRobot.telemetry.memoryUsage}%</span>
                </div>
                <div className="telemetry-item">
                  <label>Temperature</label>
                  <span className="value">{selectedRobot.telemetry.temperature}°C</span>
                </div>
                <div className="telemetry-item">
                  <label>Position</label>
                  <span className="value">
                    X: {selectedRobot.telemetry.pose.x.toFixed(2)} Y: {selectedRobot.telemetry.pose.y.toFixed(2)}
                  </span>
                </div>
                <div className="telemetry-item">
                  <label>Heading</label>
                  <span className="value">{selectedRobot.telemetry.pose.theta.toFixed(0)}°</span>
                </div>
              </div>
            </div>

            {/* Camera Feed Placeholder */}
            <div className="camera-section">
              <h4>
                <Camera size={14} />
                Camera Feed
                {remoteSession && <span className="live-badge">LIVE</span>}
              </h4>
              <div className="camera-feed">
                {remoteSession ? (
                  <div className="feed-active">
                    <div className="feed-placeholder">
                      <Camera size={48} />
                      <p>Receiving video stream...</p>
                      <span>Robot POV Camera • 30 FPS</span>
                    </div>
                    <div className="feed-overlay">
                      <span className="timestamp">{new Date().toLocaleTimeString()}</span>
                      <span className="connection-status">
                        <span className="pulse" />
                        Remote Session Active
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="feed-inactive">
                    <Eye size={48} />
                    <p>Camera feed available</p>
                    <span>Start remote session to view</span>
                  </div>
                )}
              </div>
            </div>

            {/* Alerts */}
            {selectedRobot.alerts.length > 0 && (
              <div className="alerts-section">
                <h4>
                  <AlertTriangle size={14} />
                  Active Alerts
                </h4>
                <div className="alerts-list">
                  {selectedRobot.alerts.map((alert, idx) => (
                    <div key={idx} className="alert-item">
                      <AlertTriangle size={14} />
                      <span>{alert}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Quick Actions */}
            <div className="quick-actions">
              <h4>Quick Actions</h4>
              <div className="action-buttons">
                <button className="action-btn" disabled={!remoteSession}>
                  <Play size={14} />
                  Stand Up
                </button>
                <button className="action-btn" disabled={!remoteSession}>
                  <ArrowRight size={14} />
                  Move Forward
                </button>
                <button className="action-btn diagnostic">
                  <Terminal size={14} />
                  Run Diagnostics
                </button>
                <button className="action-btn">
                  <Download size={14} />
                  Download Logs
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {onCancel && (
        <div className="ops-footer">
          <button className="btn-secondary" onClick={onCancel}>
            Back to Dashboard
          </button>
        </div>
      )}
    </div>
  );
}
