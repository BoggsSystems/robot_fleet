import { useState } from 'react';
import { Bot, Settings, Plus, Trash2, Edit2, Battery, Wifi, MapPin, Clock, Package, Shield, AlertCircle, CheckCircle, Activity, Zap, Eye, MoreVertical, ChevronDown, ChevronUp } from 'lucide-react';
import './FleetDetailView.css';

interface RobotDetail {
  id: string;
  model: string;
  type: string;
  serial: string;
  status: 'active' | 'idle' | 'maintenance' | 'offline';
  battery_level: number;
  last_maintenance: string;
  next_maintenance: string;
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
}

interface FleetDetailViewProps {
  customer: any;
  fleetConfig: any;
  onEditRobot?: (robotId: string) => void;
  onRemoveRobot?: (robotId: string) => void;
}

const MOCK_ROBOT_DETAILS: RobotDetail[] = [
  {
    id: 'robot_001',
    model: 'Unitree A1',
    type: 'delivery',
    serial: 'UT-A1-2024-001',
    status: 'active',
    battery_level: 85,
    last_maintenance: '2024-03-01',
    next_maintenance: '2024-04-01',
    location: 'Warehouse Zone A',
    current_task: 'Package delivery to Zone B',
    capabilities: ['package_delivery', 'navigation', 'climbing', 'dynamic_balance'],
    specifications: {
      weight_capacity: '5 kg',
      battery_life: '8 hours',
      speed: '6 km/h',
      navigation: 'LiDAR + Visual SLAM'
    },
    performance: {
      total_tasks: 156,
      uptime: '98.5%',
      efficiency: 94.2,
      error_rate: 0.8
    }
  },
  {
    id: 'robot_002',
    model: 'Unitree Go1',
    type: 'security',
    serial: 'UT-GO1-2024-001',
    status: 'idle',
    battery_level: 92,
    last_maintenance: '2024-03-05',
    next_maintenance: '2024-04-05',
    location: 'Main Lobby',
    capabilities: ['surveillance', 'patrol', 'human_detection', 'night_vision'],
    specifications: {
      weight_capacity: '3 kg',
      battery_life: '10 hours',
      speed: '4.5 km/h',
      navigation: 'Visual SLAM + GPS'
    },
    performance: {
      total_tasks: 89,
      uptime: '99.1%',
      efficiency: 91.7,
      error_rate: 0.3
    }
  },
  {
    id: 'robot_003',
    model: 'Unitree Aliengo',
    type: 'inspection',
    serial: 'UT-AL-2024-001',
    status: 'maintenance',
    battery_level: 45,
    last_maintenance: '2024-03-10',
    next_maintenance: '2024-03-15',
    location: 'Maintenance Bay',
    capabilities: ['visual_inspection', 'thermal_imaging', 'sensor_monitoring', 'reporting'],
    specifications: {
      weight_capacity: '2 kg',
      battery_life: '12 hours',
      speed: '3.5 km/h',
      navigation: 'LiDAR + RTK GPS'
    },
    performance: {
      total_tasks: 67,
      uptime: '96.8%',
      efficiency: 88.9,
      error_rate: 1.2
    }
  },
  {
    id: 'robot_004',
    model: 'Unitree Z1',
    type: 'maintenance',
    serial: 'UT-Z1-2024-001',
    status: 'active',
    battery_level: 78,
    last_maintenance: '2024-03-08',
    next_maintenance: '2024-04-08',
    location: 'Production Line',
    current_task: 'Equipment diagnostic check',
    capabilities: ['diagnostics', 'repair_assistance', 'tool_carrying', 'preventive_maintenance'],
    specifications: {
      weight_capacity: '10 kg',
      battery_life: '16 hours',
      speed: '2 km/h',
      navigation: 'LiDAR + Visual SLAM'
    },
    performance: {
      total_tasks: 124,
      uptime: '97.2%',
      efficiency: 92.5,
      error_rate: 0.6
    }
  }
];

export function FleetDetailView({ customer, fleetConfig, onEditRobot, onRemoveRobot }: FleetDetailViewProps) {
  const [robots, setRobots] = useState<RobotDetail[]>(MOCK_ROBOT_DETAILS);
  const [selectedRobot, setSelectedRobot] = useState<RobotDetail | null>(null);
  const [expandedRobot, setExpandedRobot] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('list');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  const getStatusColor = (status: RobotDetail['status']) => {
    switch (status) {
      case 'active': return '#10b981';
      case 'idle': return '#f59e0b';
      case 'maintenance': return '#ef4444';
      case 'offline': return '#6b7280';
      default: return '#6b7280';
    }
  };

  const getStatusIcon = (status: RobotDetail['status']) => {
    switch (status) {
      case 'active': return <Activity className="status-icon" />;
      case 'idle': return <Clock className="status-icon" />;
      case 'maintenance': return <Settings className="status-icon" />;
      case 'offline': return <AlertCircle className="status-icon" />;
      default: return <AlertCircle className="status-icon" />;
    }
  };

  const getBatteryColor = (level: number) => {
    if (level >= 80) return '#10b981';
    if (level >= 50) return '#f59e0b';
    return '#ef4444';
  };

  const getEfficiencyColor = (efficiency: number) => {
    if (efficiency >= 90) return '#10b981';
    if (efficiency >= 75) return '#f59e0b';
    return '#ef4444';
  };

  const filteredRobots = filterStatus === 'all' 
    ? robots 
    : robots.filter(robot => robot.status === filterStatus);

  const toggleRobotExpansion = (robotId: string) => {
    setExpandedRobot(expandedRobot === robotId ? null : robotId);
  };

  const renderRobotCard = (robot: RobotDetail) => (
    <div key={robot.id} className="robot-card">
      <div className="robot-header">
        <div className="robot-info">
          <div className="robot-avatar">
            <Bot className="robot-icon" />
          </div>
          <div>
            <h3>{robot.model}</h3>
            <p className="robot-serial">{robot.serial}</p>
          </div>
        </div>
        <div className="robot-status">
          <div className="status-badge" style={{ color: getStatusColor(robot.status) }}>
            {getStatusIcon(robot.status)}
            <span>{robot.status}</span>
          </div>
          <div className="battery-indicator">
            <Battery className="battery-icon" style={{ color: getBatteryColor(robot.battery_level) }} />
            <span>{robot.battery_level}%</span>
          </div>
        </div>
      </div>

      <div className="robot-location">
        <MapPin className="location-icon" />
        <span>{robot.location}</span>
        {robot.current_task && (
          <div className="current-task">
            <Activity className="task-icon" />
            <span>{robot.current_task}</span>
          </div>
        )}
      </div>

      <div className="robot-specs">
        <div className="spec-item">
          <Package className="spec-icon" />
          <span>{robot.specifications.weight_capacity}</span>
        </div>
        <div className="spec-item">
          <Zap className="spec-icon" />
          <span>{robot.specifications.speed}</span>
        </div>
        <div className="spec-item">
          <Shield className="spec-icon" />
          <span>{robot.specifications.navigation}</span>
        </div>
      </div>

      <div className="robot-performance">
        <div className="perf-item">
          <span className="perf-label">Efficiency</span>
          <div className="perf-bar">
            <div 
              className="perf-fill" 
              style={{ 
                width: `${robot.performance.efficiency}%`,
                backgroundColor: getEfficiencyColor(robot.performance.efficiency)
              }}
            />
          </div>
          <span className="perf-value">{robot.performance.efficiency}%</span>
        </div>
        <div className="perf-item">
          <span className="perf-label">Uptime</span>
          <span className="perf-value">{robot.performance.uptime}</span>
        </div>
        <div className="perf-item">
          <span className="perf-label">Tasks</span>
          <span className="perf-value">{robot.performance.total_tasks}</span>
        </div>
      </div>

      <div className="robot-actions">
        <button 
          className="action-btn secondary"
          onClick={() => toggleRobotExpansion(robot.id)}
        >
          {expandedRobot === robot.id ? <ChevronUp className="btn-icon" /> : <ChevronDown className="btn-icon" />}
          {expandedRobot === robot.id ? 'Hide Details' : 'Show Details'}
        </button>
        <button className="action-btn primary">
          <Eye className="btn-icon" />
          Monitor
        </button>
        <button className="action-btn secondary">
          <Edit2 className="btn-icon" />
          Edit
        </button>
      </div>

      {expandedRobot === robot.id && (
        <div className="robot-details-expanded">
          <div className="details-grid">
            <div className="detail-section">
              <h4>Maintenance Schedule</h4>
              <div className="detail-item">
                <span className="detail-label">Last Maintenance:</span>
                <span className="detail-value">{robot.last_maintenance}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Next Maintenance:</span>
                <span className="detail-value">{robot.next_maintenance}</span>
              </div>
            </div>

            <div className="detail-section">
              <h4>Capabilities</h4>
              <div className="capability-tags">
                {robot.capabilities.map((capability, index) => (
                  <span key={index} className="capability-tag">
                    {capability.replace('_', ' ')}
                  </span>
                ))}
              </div>
            </div>

            <div className="detail-section">
              <h4>Performance Metrics</h4>
              <div className="detail-item">
                <span className="detail-label">Total Tasks:</span>
                <span className="detail-value">{robot.performance.total_tasks}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Uptime:</span>
                <span className="detail-value">{robot.performance.uptime}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Efficiency:</span>
                <span className="detail-value">{robot.performance.efficiency}%</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Error Rate:</span>
                <span className="detail-value">{robot.performance.error_rate}%</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="fleet-detail-view">
      <div className="fleet-header">
        <div className="header-info">
          <h2>{customer.company} Fleet</h2>
          <p>{robots.length} robots deployed</p>
        </div>
        <div className="header-actions">
          <div className="view-toggle">
            <button 
              className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
              onClick={() => setViewMode('list')}
            >
              List View
            </button>
            <button 
              className={`view-btn ${viewMode === 'grid' ? 'active' : ''}`}
              onClick={() => setViewMode('grid')}
            >
              Grid View
            </button>
          </div>
          <button className="btn-primary">
            <Plus className="btn-icon" />
            Add Robot
          </button>
        </div>
      </div>

      <div className="fleet-stats">
        <div className="stat-card">
          <div className="stat-icon-wrapper active">
            <Activity className="stat-icon" />
          </div>
          <div className="stat-info">
            <span className="stat-value">
              {robots.filter(r => r.status === 'active').length}
            </span>
            <span className="stat-label">Active</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon-wrapper idle">
            <Clock className="stat-icon" />
          </div>
          <div className="stat-info">
            <span className="stat-value">
              {robots.filter(r => r.status === 'idle').length}
            </span>
            <span className="stat-label">Idle</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon-wrapper maintenance">
            <Settings className="stat-icon" />
          </div>
          <div className="stat-info">
            <span className="stat-value">
              {robots.filter(r => r.status === 'maintenance').length}
            </span>
            <span className="stat-label">Maintenance</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon-wrapper offline">
            <AlertCircle className="stat-icon" />
          </div>
          <div className="stat-info">
            <span className="stat-value">
              {robots.filter(r => r.status === 'offline').length}
            </span>
            <span className="stat-label">Offline</span>
          </div>
        </div>
      </div>

      <div className="fleet-controls">
        <div className="filter-controls">
          <label className="filter-label">Filter by Status:</label>
          <select 
            value={filterStatus} 
            onChange={(e) => setFilterStatus(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Robots ({robots.length})</option>
            <option value="active">Active ({robots.filter(r => r.status === 'active').length})</option>
            <option value="idle">Idle ({robots.filter(r => r.status === 'idle').length})</option>
            <option value="maintenance">Maintenance ({robots.filter(r => r.status === 'maintenance').length})</option>
            <option value="offline">Offline ({robots.filter(r => r.status === 'offline').length})</option>
          </select>
        </div>
        <div className="search-controls">
          <input 
            type="text" 
            placeholder="Search robots..."
            className="search-input"
          />
        </div>
      </div>

      <div className={`robots-container ${viewMode}`}>
        {filteredRobots.map(renderRobotCard)}
      </div>

      {filteredRobots.length === 0 && (
        <div className="empty-state">
          <Bot className="empty-icon" />
          <h3>No robots found</h3>
          <p>Try adjusting your filters or add new robots to your fleet.</p>
        </div>
      )}
    </div>
  );
}
