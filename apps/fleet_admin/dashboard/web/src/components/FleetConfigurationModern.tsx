import { useState, useEffect } from 'react';
import { Bot, Settings, Plus, Trash2, Save, X, Check, AlertCircle, Wifi, Battery, Package, MapPin, Shield, Zap, ChevronRight, ChevronDown, Grid3x3, List, Search, Filter, MoreVertical } from 'lucide-react';
import './FleetConfigurationModern.css';

interface FleetConfigurationProps {
  customer: any;
  onSaveConfiguration: (config: FleetConfig) => void;
  onCancel: () => void;
}

export type FleetConfig = {
  id: string;
  customer_id: string;
  configuration_name: string;
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
};

export type RobotType = {
  id: string;
  model: string;
  type: 'delivery' | 'security' | 'cleaning' | 'inspection' | 'maintenance';
  count: number;
  capabilities: string[];
  specifications: {
    weight_capacity: string;
    battery_life: string;
    speed: string;
    navigation: string;
  };
};

export type NetworkConfig = {
  ssid: string;
  security_type: 'WPA2' | 'WPA3' | 'Open';
  frequency_band: '2.4GHz' | '5GHz' | 'Dual';
  mesh_network: boolean;
  failover_enabled: boolean;
};

export type SafetyConfig = {
  emergency_stop: boolean;
  obstacle_detection: boolean;
  speed_limits: {
    indoor: string;
    outdoor: string;
  };
  restricted_zones: string[];
  human_detection: boolean;
  collision_prevention: boolean;
};

export type DeploymentZone = {
  id: string;
  name: string;
  type: 'indoor' | 'outdoor' | 'mixed';
  coordinates: string;
  access_restrictions: string[];
  environmental_conditions: string[];
};

export type OperationalHours = {
  monday: { start: string; end: string; active: boolean };
  tuesday: { start: string; end: string; active: boolean };
  wednesday: { start: string; end: string; active: boolean };
  thursday: { start: string; end: string; active: boolean };
  friday: { start: string; end: string; active: boolean };
  saturday: { start: string; end: string; active: boolean };
  sunday: { start: string; end: string; active: boolean };
};

export type MaintenanceSchedule = {
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly';
  tasks: MaintenanceTask[];
  auto_scheduling: boolean;
  notification_preferences: {
    email: boolean;
    sms: boolean;
    dashboard: boolean;
  };
};

export type MaintenanceTask = {
  id: string;
  name: string;
  description: string;
  estimated_duration: string;
  required_parts: string[];
  priority: 'low' | 'medium' | 'high';
};

const ROBOT_MODELS = [
  { model: 'Cottage-R1', type: 'delivery', capabilities: ['package_delivery', 'navigation', 'obstacle_avoidance'], color: '#3b82f6' },
  { model: 'Cottage-S1', type: 'security', capabilities: ['surveillance', 'patrol', 'alert_system'], color: '#10b981' },
  { model: 'Cottage-C1', type: 'cleaning', capabilities: ['floor_cleaning', 'surface_sanitization', 'waste_collection'], color: '#8b5cf6' },
  { model: 'Cottage-I1', type: 'inspection', capabilities: ['visual_inspection', 'sensor_monitoring', 'reporting'], color: '#f59e0b' },
  { model: 'Cottage-M1', type: 'maintenance', capabilities: ['diagnostics', 'repair_assistance', 'preventive_maintenance'], color: '#ef4444' }
];

const DEFAULT_FLEET_CONFIG: Partial<FleetConfig> = {
  configuration_name: '',
  configuration_data: {
    environment_type: 'mixed',
    robot_count: 3,
    robot_types: [],
    network_config: {
      ssid: '',
      security_type: 'WPA2',
      frequency_band: 'Dual',
      mesh_network: true,
      failover_enabled: true
    },
    safety_config: {
      emergency_stop: true,
      obstacle_detection: true,
      speed_limits: {
        indoor: '2 mph',
        outdoor: '5 mph'
      },
      restricted_zones: [],
      human_detection: true,
      collision_prevention: true
    },
    deployment_zones: [],
    operational_hours: {
      monday: { start: '09:00', end: '17:00', active: true },
      tuesday: { start: '09:00', end: '17:00', active: true },
      wednesday: { start: '09:00', end: '17:00', active: true },
      thursday: { start: '09:00', end: '17:00', active: true },
      friday: { start: '09:00', end: '17:00', active: true },
      saturday: { start: '10:00', end: '14:00', active: false },
      sunday: { start: '10:00', end: '14:00', active: false }
    },
    maintenance_schedule: {
      frequency: 'weekly',
      tasks: [],
      auto_scheduling: true,
      notification_preferences: {
        email: true,
        sms: false,
        dashboard: true
      }
    }
  }
};

// API interfaces
interface RobotTypeAPI {
  id: string;
  manufacturer: string;
  model: string;
  robot_type: string;
  capabilities: string[];
  specifications: {
    weight_capacity: number;
    battery_life_hours: number;
    max_speed_kmh: number;
    navigation_system: string;
    sensor_suite: string[];
    dimensions: { length: number; width: number; height: number };
    weight_kg: number;
    operating_temperature_range: string;
    ip_rating: string;
    connectivity_options: string[];
  };
  weight_capacity: number;
  battery_life_hours: number;
  max_speed_kmh: number;
  navigation_system: string;
  price_amount: number;
  availability_status: string;
  image_url?: string;
  documentation_url?: string;
  data_sheet_url?: string;
}

// API functions
const fetchRobotTypes = async (): Promise<RobotTypeAPI[]> => {
  try {
    console.log('🌐 Making API call to http://localhost:8002/api/robots/types');
    const response = await fetch('http://localhost:8002/api/robots/types');
    console.log('📡 Response status:', response.status);
    console.log('📡 Response headers:', response.headers);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('📊 Parsed JSON data:', data);
    return data;
  } catch (error) {
    console.error('❌ Error fetching robot types:', error);
    return [];
  }
};

const getRobotIcon = (type: string) => {
  switch (type) {
    case 'delivery': return '📦';
    case 'security': return '🛡️';
    case 'cleaning': return '🧹';
    case 'inspection': return '🔍';
    case 'maintenance': return '🔧';
    default: return '🤖';
  }
};

const getRobotColor = (type: string) => {
  switch (type) {
    case 'delivery': return '#3b82f6';
    case 'security': return '#10b981';
    case 'cleaning': return '#8b5cf6';
    case 'inspection': return '#f59e0b';
    case 'maintenance': return '#ef4444';
    default: return '#6b7280';
  }
};

export function FleetConfigurationModern({ customer, onSaveConfiguration, onCancel }: FleetConfigurationProps) {
  const [config, setConfig] = useState<FleetConfig>({
    id: `fleet_${Date.now()}`,
    customer_id: customer.id,
    configuration_name: `${customer.company}_Fleet_Config`,
    ...DEFAULT_FLEET_CONFIG,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  } as FleetConfig);

  const [activeSection, setActiveSection] = useState<'overview' | 'robots' | 'network' | 'safety' | 'zones' | 'operations' | 'maintenance'>('overview');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchTerm, setSearchTerm] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [availableRobots, setAvailableRobots] = useState<RobotTypeAPI[]>([]);
  const [loadingRobots, setLoadingRobots] = useState(true);

  // Fetch available robots from API
  useEffect(() => {
    const loadRobotTypes = async () => {
      try {
        console.log('🔄 Starting to fetch robot types...');
        setLoadingRobots(true);
        const robots = await fetchRobotTypes();
        console.log('📦 Received robots from API:', robots);
        setAvailableRobots(robots);
        console.log('✅ Set available robots:', robots.length);
      } catch (error) {
        console.error('❌ Failed to load robot types:', error);
      } finally {
        setLoadingRobots(false);
        console.log('🏁 Finished loading robots');
      }
    };

    loadRobotTypes();
  }, []);

  const handleSave = () => {
    const newErrors: Record<string, string> = {};
    
    if (!config.configuration_name) {
      newErrors.configuration_name = 'Configuration name is required';
    }
    
    if (config.configuration_data.robot_count === 0) {
      newErrors.robot_count = 'At least one robot is required';
    }
    
    if (config.configuration_data.robot_types.length === 0) {
      newErrors.robot_types = 'At least one robot type must be selected';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setErrors({});
    onSaveConfiguration({ ...config, updated_at: new Date().toISOString() });
  };

  const addRobotType = () => {
    // Use the first available robot from API or fallback
    console.log('🤖 Available robots when adding:', availableRobots);
    const selectedRobot = availableRobots.length > 0 ? availableRobots[0] : null;
    console.log('🎯 Selected robot:', selectedRobot);
    
    const newRobot: RobotType = {
      id: `robot_${Date.now()}`,
      model: selectedRobot?.model || 'Cottage-R1',
      type: selectedRobot?.robot_type as any || 'delivery',
      count: 1,
      capabilities: selectedRobot?.capabilities || ['package_delivery', 'navigation', 'obstacle_avoidance'],
      specifications: {
        weight_capacity: selectedRobot ? `${selectedRobot.weight_capacity} kg` : '50 lbs',
        battery_life: selectedRobot ? `${selectedRobot.battery_life_hours} hours` : '8 hours',
        speed: selectedRobot ? `${selectedRobot.max_speed_kmh} km/h` : '3 mph',
        navigation: selectedRobot?.navigation_system || 'LiDAR + GPS'
      }
    };
    
    console.log('🆕 New robot to add:', newRobot);
    
    setConfig({
      ...config,
      configuration_data: {
        ...config.configuration_data,
        robot_types: [...config.configuration_data.robot_types, newRobot]
      }
    });
    
    console.log('✅ Robot added to configuration');
  };

  const updateRobotType = (index: number, field: keyof RobotType, value: any) => {
    const updatedRobots = [...config.configuration_data.robot_types];
    updatedRobots[index] = { ...updatedRobots[index], [field]: value };
    
    setConfig({
      ...config,
      configuration_data: {
        ...config.configuration_data,
        robot_types: updatedRobots
      }
    });
  };

  const removeRobotType = (index: number) => {
    const updatedRobots = config.configuration_data.robot_types.filter((_, i) => i !== index);
    
    setConfig({
      ...config,
      configuration_data: {
        ...config.configuration_data,
        robot_types: updatedRobots,
        robot_count: updatedRobots.reduce((sum, robot) => sum + robot.count, 0)
      }
    });
  };

  const getRobotModelColor = (model: string) => {
    const robotModel = availableRobots.find(r => r.model === model);
    return robotModel ? getRobotColor(robotModel.robot_type) : '#6b7280';
  };

  const getRobotIcon = (type: string) => {
    switch (type) {
      case 'delivery': return '📦';
      case 'security': return '🛡️';
      case 'cleaning': return '🧹';
      case 'inspection': return '🔍';
      case 'maintenance': return '🔧';
      default: return '🤖';
    }
  };

  return (
    <div className="fleet-configuration-modern">
      <div className="config-header-modern">
        <div className="header-content">
          <div className="header-left">
            <div className="header-title">
              <div className="title-icon-wrapper">
                <Settings className="title-icon" />
              </div>
              <div>
                <h1>Fleet Configuration</h1>
                <p className="customer-name">{customer.name}</p>
              </div>
            </div>
            <div className="header-badges">
              <div className="badge">
                <Bot className="badge-icon" />
                <span>{config.configuration_data.robot_count} Robots</span>
              </div>
              <div className="badge">
                <Package className="badge-icon" />
                <span>{config.configuration_data.environment_type}</span>
              </div>
            </div>
          </div>
          <div className="header-actions">
            <button onClick={onCancel} className="btn-ghost">
              <X className="btn-icon" />
              Cancel
            </button>
            <button onClick={handleSave} className="btn-primary">
              <Save className="btn-icon" />
              Save Configuration
            </button>
          </div>
        </div>
      </div>

      <div className="config-content-modern">
        <div className="config-sidebar-modern">
          <div className="section-nav-modern">
            {[
              { id: 'overview', label: 'Overview', icon: Grid3x3 },
              { id: 'robots', label: 'Robot Fleet', icon: Bot },
              { id: 'network', label: 'Network', icon: Wifi },
              { id: 'safety', label: 'Safety', icon: Shield },
              { id: 'zones', label: 'Zones', icon: MapPin },
              { id: 'operations', label: 'Operations', icon: Zap },
              { id: 'maintenance', label: 'Maintenance', icon: Settings }
            ].map((section) => (
              <button
                key={section.id}
                className={`nav-item-modern ${activeSection === section.id ? 'active' : ''}`}
                onClick={() => setActiveSection(section.id as any)}
              >
                <section.icon className="nav-icon" />
                <span className="nav-label">{section.label}</span>
                {activeSection === section.id && <ChevronRight className="nav-arrow" />}
              </button>
            ))}
          </div>
        </div>

        <div className="config-main-modern">
          {activeSection === 'overview' && (
            <div className="config-section-modern">
              <div className="section-header">
                <div className="section-title">
                  <h2>Configuration Overview</h2>
                  <p className="section-description">Set up your fleet configuration and basic settings</p>
                </div>
                <div className="section-actions">
                  <button
                    className="btn-toggle-advanced"
                    onClick={() => setShowAdvanced(!showAdvanced)}
                  >
                    <Settings className="btn-icon" />
                    {showAdvanced ? 'Simple' : 'Advanced'}
                  </button>
                </div>
              </div>

              <div className="overview-grid-modern">
                <div className="config-card-modern">
                  <div className="card-header">
                    <div className="card-title">
                      <Package className="card-icon" />
                      <h3>Basic Settings</h3>
                    </div>
                  </div>
                  <div className="card-content">
                    <div className="form-group-modern">
                      <label>Configuration Name</label>
                      <div className="input-wrapper">
                        <input
                          type="text"
                          value={config.configuration_name}
                          onChange={(e) => setConfig({ ...config, configuration_name: e.target.value })}
                          className={`form-input-modern ${errors.configuration_name ? 'error' : ''}`}
                          placeholder="Enter configuration name"
                        />
                        {errors.configuration_name && <span className="error-message">{errors.configuration_name}</span>}
                      </div>
                    </div>

                    <div className="form-group-modern">
                      <label>Environment Type</label>
                      <div className="radio-group-modern">
                        {[
                          { value: 'indoor', label: 'Indoor Only', icon: '🏠' },
                          { value: 'outdoor', label: 'Outdoor Only', icon: '🌳' },
                          { value: 'mixed', label: 'Mixed Environment', icon: '🏢' }
                        ].map((option) => (
                          <label key={option.value} className="radio-option-modern">
                            <input
                              type="radio"
                              name="environment_type"
                              value={option.value}
                              checked={config.configuration_data.environment_type === option.value}
                              onChange={(e) => setConfig({
                                ...config,
                                configuration_data: {
                                  ...config.configuration_data,
                                  environment_type: e.target.value as any
                                }
                              })}
                            />
                            <div className="radio-content">
                              <span className="radio-icon">{option.icon}</span>
                              <span className="radio-label">{option.label}</span>
                            </div>
                          </label>
                        ))}
                      </div>
                    </div>

                    <div className="form-group-modern">
                      <label>Total Robot Count</label>
                      <div className="input-wrapper">
                        <input
                          type="number"
                          value={config.configuration_data.robot_count}
                          onChange={(e) => setConfig({
                            ...config,
                            configuration_data: {
                              ...config.configuration_data,
                              robot_count: parseInt(e.target.value) || 0
                            }
                          })}
                          className={`form-input-modern ${errors.robot_count ? 'error' : ''}`}
                          min="1"
                        />
                        {errors.robot_count && <span className="error-message">{errors.robot_count}</span>}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="config-card-modern">
                  <div className="card-header">
                    <div className="card-title">
                      <Bot className="card-icon" />
                      <h3>Available Robots</h3>
                    </div>
                    <div className="badge">
                      <span>{availableRobots.length} Available</span>
                    </div>
                  </div>
                  <div className="card-content">
                    {loadingRobots ? (
                      <div className="loading-state">
                        <p>Loading available robots...</p>
                      </div>
                    ) : availableRobots.length === 0 ? (
                      <div className="empty-state-modern">
                        <p>No robots available</p>
                      </div>
                    ) : (
                      <div className="available-robots-grid">
                        {availableRobots.map((robot) => (
                          <div key={robot.id} className="available-robot-card">
                            <div className="robot-header">
                              <div className="robot-info">
                                <div 
                                  className="robot-avatar"
                                  style={{ backgroundColor: getRobotColor(robot.robot_type) }}
                                >
                                  <span className="robot-emoji">{getRobotIcon(robot.robot_type)}</span>
                                </div>
                                <div>
                                  <h4>{robot.manufacturer} {robot.model}</h4>
                                  <p className="robot-type">{robot.robot_type}</p>
                                </div>
                              </div>
                              <div className="robot-price">
                                <span>${robot.price_amount.toLocaleString()}</span>
                              </div>
                            </div>
                            <div className="robot-specs">
                              <div className="spec-item">
                                <span className="spec-label">Capacity:</span>
                                <span className="spec-value">{robot.weight_capacity} kg</span>
                              </div>
                              <div className="spec-item">
                                <span className="spec-label">Battery:</span>
                                <span className="spec-value">{robot.battery_life_hours} hrs</span>
                              </div>
                              <div className="spec-item">
                                <span className="spec-label">Speed:</span>
                                <span className="spec-value">{robot.max_speed_kmh} km/h</span>
                              </div>
                            </div>
                            <div className="robot-capabilities">
                              {robot.capabilities.slice(0, 3).map((capability, capIndex) => (
                                <span key={capIndex} className="capability-tag-modern">
                                  {capability.replace('_', ' ')}
                                </span>
                              ))}
                              {robot.capabilities.length > 3 && (
                                <span className="capability-tag-modern">+{robot.capabilities.length - 3} more</span>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                <div className="config-card-modern">
                  <div className="card-header">
                    <div className="card-title">
                      <Bot className="card-icon" />
                      <h3>Fleet Summary</h3>
                    </div>
                    <div className="view-toggle">
                      <button
                        className={`view-btn ${viewMode === 'grid' ? 'active' : ''}`}
                        onClick={() => setViewMode('grid')}
                      >
                        <Grid3x3 className="view-icon" />
                      </button>
                      <button
                        className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
                        onClick={() => setViewMode('list')}
                      >
                        <List className="view-icon" />
                      </button>
                    </div>
                  </div>
                  <div className="card-content">
                    <div className="search-bar">
                      <Search className="search-icon" />
                      <input
                        type="text"
                        placeholder="Search robots..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="search-input"
                      />
                    </div>

                    {config.configuration_data.robot_types.length === 0 ? (
                      <div className="empty-state-modern">
                        <Bot className="empty-icon" />
                        <h3>No Robots Configured</h3>
                        <p>Add robots to your fleet to get started</p>
                        <button onClick={addRobotType} className="btn-primary">
                          <Plus className="btn-icon" />
                          Add First Robot
                        </button>
                      </div>
                    ) : (
                      <div className={`robots-${viewMode}`}>
                        {config.configuration_data.robot_types.map((robot, index) => (
                          <div key={robot.id} className="robot-card-modern">
                            <div className="robot-header">
                              <div className="robot-info">
                                <div 
                                  className="robot-avatar"
                                  style={{ backgroundColor: getRobotModelColor(robot.model) }}
                                >
                                  <span className="robot-emoji">{getRobotIcon(robot.type)}</span>
                                </div>
                                <div>
                                  <h4>{robot.model}</h4>
                                  <p className="robot-type">{robot.type}</p>
                                </div>
                              </div>
                              <div className="robot-actions">
                                <button className="btn-icon-btn">
                                  <MoreVertical className="icon" />
                                </button>
                              </div>
                            </div>
                            <div className="robot-details">
                              <div className="robot-specs">
                                <div className="spec-item">
                                  <span className="spec-label">Quantity:</span>
                                  <span className="spec-value">{robot.count}</span>
                                </div>
                                <div className="spec-item">
                                  <span className="spec-label">Capacity:</span>
                                  <span className="spec-value">{robot.specifications.weight_capacity}</span>
                                </div>
                                <div className="spec-item">
                                  <span className="spec-label">Battery:</span>
                                  <span className="spec-value">{robot.specifications.battery_life}</span>
                                </div>
                              </div>
                              <div className="robot-capabilities">
                                {robot.capabilities.map((capability, capIndex) => (
                                  <span key={capIndex} className="capability-tag-modern">
                                    {capability.replace('_', ' ')}
                                  </span>
                                ))}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                <div className="config-card-modern">
                  <div className="card-header">
                    <div className="card-title">
                      <Wifi className="card-icon" />
                      <h3>Quick Stats</h3>
                    </div>
                  </div>
                  <div className="card-content">
                    <div className="stats-grid">
                      <div className="stat-card">
                        <div className="stat-icon-wrapper">
                          <Bot className="stat-icon" />
                        </div>
                        <div className="stat-content">
                          <h4>Robot Types</h4>
                          <p>{config.configuration_data.robot_types.length} configured</p>
                        </div>
                      </div>
                      <div className="stat-card">
                        <div className="stat-icon-wrapper">
                          <MapPin className="stat-icon" />
                        </div>
                        <div className="stat-content">
                          <h4>Deployment Zones</h4>
                          <p>{config.configuration_data.deployment_zones.length} zones</p>
                        </div>
                      </div>
                      <div className="stat-card">
                        <div className="stat-icon-wrapper">
                          <Wifi className="stat-icon" />
                        </div>
                        <div className="stat-content">
                          <h4>Network</h4>
                          <p>{config.configuration_data.network_config.ssid || 'Not configured'}</p>
                        </div>
                      </div>
                      <div className="stat-card">
                        <div className="stat-icon-wrapper">
                          <Shield className="stat-icon" />
                        </div>
                        <div className="stat-content">
                          <h4>Safety Features</h4>
                          <p>{Object.values(config.configuration_data.safety_config).filter(Boolean).length} enabled</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeSection === 'robots' && (
            <div className="config-section-modern">
              <div className="section-header">
                <div className="section-title">
                  <h2>Robot Fleet Configuration</h2>
                  <p className="section-description">Configure your robot fleet with different models and specifications</p>
                </div>
                <div className="section-actions">
                  <button onClick={addRobotType} className="btn-primary">
                    <Plus className="btn-icon" />
                    Add Robot Type
                  </button>
                </div>
              </div>

              {errors.robot_types && <div className="error-banner-modern">{errors.robot_types}</div>}

              <div className="robots-grid-modern">
                {config.configuration_data.robot_types.map((robot, index) => (
                  <div key={robot.id} className="robot-config-card-modern">
                    <div className="card-header">
                      <div className="card-title">
                        <div 
                          className="robot-avatar-large"
                          style={{ backgroundColor: getRobotModelColor(robot.model) }}
                        >
                          <span className="robot-emoji-large">{getRobotIcon(robot.type)}</span>
                        </div>
                        <div>
                          <h3>Robot {index + 1}</h3>
                          <p className="robot-model">{robot.model}</p>
                        </div>
                      </div>
                      <button 
                        onClick={() => removeRobotType(index)}
                        className="btn-danger"
                      >
                        <Trash2 className="btn-icon" />
                        Remove
                      </button>
                    </div>

                    <div className="card-content">
                      <div className="config-grid">
                        <div className="form-group-modern">
                          <label>Model</label>
                          <div className="select-wrapper">
                            <select
                              value={robot.model}
                              onChange={(e) => {
                                const selectedRobot = availableRobots.find(r => r.model === e.target.value);
                                if (selectedRobot) {
                                  updateRobotType(index, 'model', selectedRobot.model);
                                  updateRobotType(index, 'type', selectedRobot.robot_type);
                                  updateRobotType(index, 'capabilities', selectedRobot.capabilities);
                                  updateRobotType(index, 'specifications', {
                                    weight_capacity: `${selectedRobot.weight_capacity} kg`,
                                    battery_life: `${selectedRobot.battery_life_hours} hours`,
                                    speed: `${selectedRobot.max_speed_kmh} km/h`,
                                    navigation: selectedRobot.navigation_system
                                  });
                                }
                              }}
                              className="form-select-modern"
                              disabled={loadingRobots}
                            >
                              {loadingRobots ? (
                                <option>Loading robots...</option>
                              ) : availableRobots.length > 0 ? (
                                availableRobots.map(robot => (
                                  <option key={robot.id} value={robot.model}>
                                    {robot.manufacturer} {robot.model} - ${robot.robot_type}
                                  </option>
                                ))
                              ) : (
                                <option>No robots available</option>
                              )}
                            </select>
                          </div>
                        </div>

                        <div className="form-group-modern">
                          <label>Quantity</label>
                          <div className="input-wrapper">
                            <input
                              type="number"
                              value={robot.count}
                              onChange={(e) => updateRobotType(index, 'count', parseInt(e.target.value) || 1)}
                              className="form-input-modern"
                              min="1"
                            />
                          </div>
                        </div>

                        <div className="form-group-modern">
                          <label>Weight Capacity</label>
                          <div className="input-wrapper">
                            <input
                              type="text"
                              value={robot.specifications.weight_capacity}
                              onChange={(e) => updateRobotType(index, 'specifications', {
                                ...robot.specifications,
                                weight_capacity: e.target.value
                              })}
                              className="form-input-modern"
                            />
                          </div>
                        </div>

                        <div className="form-group-modern">
                          <label>Battery Life</label>
                          <div className="input-wrapper">
                            <input
                              type="text"
                              value={robot.specifications.battery_life}
                              onChange={(e) => updateRobotType(index, 'specifications', {
                                ...robot.specifications,
                                battery_life: e.target.value
                              })}
                              className="form-input-modern"
                            />
                          </div>
                        </div>

                        <div className="form-group-modern">
                          <label>Speed</label>
                          <div className="input-wrapper">
                            <input
                              type="text"
                              value={robot.specifications.speed}
                              onChange={(e) => updateRobotType(index, 'specifications', {
                                ...robot.specifications,
                                speed: e.target.value
                              })}
                              className="form-input-modern"
                            />
                          </div>
                        </div>

                        <div className="form-group-modern">
                          <label>Navigation</label>
                          <div className="input-wrapper">
                            <input
                              type="text"
                              value={robot.specifications.navigation}
                              onChange={(e) => updateRobotType(index, 'specifications', {
                                ...robot.specifications,
                                navigation: e.target.value
                              })}
                              className="form-input-modern"
                            />
                          </div>
                        </div>
                      </div>

                      <div className="form-group-modern">
                        <label>Capabilities</label>
                        <div className="capabilities-grid">
                          {robot.capabilities.map((capability, capIndex) => (
                            <span key={capIndex} className="capability-card">
                              <Check className="capability-icon" />
                              {capability.replace('_', ' ')}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeSection === 'network' && (
            <div className="config-section-modern">
              <div className="section-header">
                <div className="section-title">
                  <h2>Network Configuration</h2>
                  <p className="section-description">Set up network connectivity and security settings</p>
                </div>
              </div>

              <div className="config-grid-modern">
                <div className="config-card-modern">
                  <div className="card-header">
                    <div className="card-title">
                      <Wifi className="card-icon" />
                      <h3>Network Settings</h3>
                    </div>
                  </div>
                  <div className="card-content">
                    <div className="form-group-modern">
                      <label>Network SSID</label>
                      <div className="input-wrapper">
                        <input
                          type="text"
                          value={config.configuration_data.network_config.ssid}
                          onChange={(e) => setConfig({
                            ...config,
                            configuration_data: {
                              ...config.configuration_data,
                              network_config: {
                                ...config.configuration_data.network_config,
                                ssid: e.target.value
                              }
                            }
                          })}
                          className="form-input-modern"
                          placeholder="Enter WiFi network name"
                        />
                      </div>
                    </div>

                    <div className="form-group-modern">
                      <label>Security Type</label>
                      <div className="select-wrapper">
                        <select
                          value={config.configuration_data.network_config.security_type}
                          onChange={(e) => setConfig({
                            ...config,
                            configuration_data: {
                              ...config.configuration_data,
                              network_config: {
                                ...config.configuration_data.network_config,
                                security_type: e.target.value as any
                              }
                            }
                          })}
                          className="form-select-modern"
                        >
                          <option value="WPA2">WPA2</option>
                          <option value="WPA3">WPA3</option>
                          <option value="Open">Open</option>
                        </select>
                      </div>
                    </div>

                    <div className="form-group-modern">
                      <label>Frequency Band</label>
                      <div className="select-wrapper">
                        <select
                          value={config.configuration_data.network_config.frequency_band}
                          onChange={(e) => setConfig({
                            ...config,
                            configuration_data: {
                              ...config.configuration_data,
                              network_config: {
                                ...config.configuration_data.network_config,
                                frequency_band: e.target.value as any
                              }
                            }
                          })}
                          className="form-select-modern"
                        >
                          <option value="2.4GHz">2.4GHz</option>
                          <option value="5GHz">5GHz</option>
                          <option value="Dual">Dual Band</option>
                        </select>
                      </div>
                    </div>

                    <div className="toggle-group-modern">
                      <label className="toggle-option-modern">
                        <input
                          type="checkbox"
                          checked={config.configuration_data.network_config.mesh_network}
                          onChange={(e) => setConfig({
                            ...config,
                            configuration_data: {
                              ...config.configuration_data,
                              network_config: {
                                ...config.configuration_data.network_config,
                                mesh_network: e.target.checked
                              }
                            }
                          })}
                        />
                        <div className="toggle-content">
                          <div className="toggle-switch"></div>
                          <div className="toggle-label">
                            <h4>Mesh Network</h4>
                            <p>Enable mesh networking for extended coverage</p>
                          </div>
                        </div>
                      </label>

                      <label className="toggle-option-modern">
                        <input
                          type="checkbox"
                          checked={config.configuration_data.network_config.failover_enabled}
                          onChange={(e) => setConfig({
                            ...config,
                            configuration_data: {
                              ...config.configuration_data,
                              network_config: {
                                ...config.configuration_data.network_config,
                                failover_enabled: e.target.checked
                              }
                            }
                          })}
                        />
                        <div className="toggle-content">
                          <div className="toggle-switch"></div>
                          <div className="toggle-label">
                            <h4>Network Failover</h4>
                            <p>Automatic failover to backup connection</p>
                          </div>
                        </div>
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeSection === 'safety' && (
            <div className="config-section-modern">
              <div className="section-header">
                <div className="section-title">
                  <h2>Safety Configuration</h2>
                  <p className="section-description">Configure safety features and operational limits</p>
                </div>
              </div>

              <div className="config-grid-modern">
                <div className="config-card-modern">
                  <div className="card-header">
                    <div className="card-title">
                      <Shield className="card-icon" />
                      <h3>Safety Features</h3>
                    </div>
                  </div>
                  <div className="card-content">
                    <div className="toggle-group-modern">
                      {[
                        { key: 'emergency_stop', label: 'Emergency Stop', description: 'Enable physical emergency stop buttons' },
                        { key: 'obstacle_detection', label: 'Obstacle Detection', description: 'Automatic obstacle detection and avoidance' },
                        { key: 'human_detection', label: 'Human Detection', description: 'Detect and avoid humans in operational area' },
                        { key: 'collision_prevention', label: 'Collision Prevention', description: 'Advanced collision prevention system' }
                      ].map((feature) => (
                        <label key={feature.key} className="toggle-option-modern">
                          <input
                            type="checkbox"
                            checked={config.configuration_data.safety_config[feature.key as keyof typeof config.configuration_data.safety_config] as boolean}
                            onChange={(e) => setConfig({
                              ...config,
                              configuration_data: {
                                ...config.configuration_data,
                                safety_config: {
                                  ...config.configuration_data.safety_config,
                                  [feature.key]: e.target.checked
                                }
                              }
                            })}
                          />
                          <div className="toggle-content">
                            <div className="toggle-switch"></div>
                            <div className="toggle-label">
                              <h4>{feature.label}</h4>
                              <p>{feature.description}</p>
                            </div>
                          </div>
                        </label>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="config-card-modern">
                  <div className="card-header">
                    <div className="card-title">
                      <Zap className="card-icon" />
                      <h3>Speed Limits</h3>
                    </div>
                  </div>
                  <div className="card-content">
                    <div className="form-group-modern">
                      <label>Indoor Speed Limit</label>
                      <div className="input-wrapper">
                        <input
                          type="text"
                          value={config.configuration_data.safety_config.speed_limits.indoor}
                          onChange={(e) => setConfig({
                            ...config,
                            configuration_data: {
                              ...config.configuration_data,
                              safety_config: {
                                ...config.configuration_data.safety_config,
                                speed_limits: {
                                  ...config.configuration_data.safety_config.speed_limits,
                                  indoor: e.target.value
                                }
                              }
                            }
                          })}
                          className="form-input-modern"
                        />
                      </div>
                    </div>

                    <div className="form-group-modern">
                      <label>Outdoor Speed Limit</label>
                      <div className="input-wrapper">
                        <input
                          type="text"
                          value={config.configuration_data.safety_config.speed_limits.outdoor}
                          onChange={(e) => setConfig({
                            ...config,
                            configuration_data: {
                              ...config.configuration_data,
                              safety_config: {
                                ...config.configuration_data.safety_config,
                                speed_limits: {
                                  ...config.configuration_data.safety_config.speed_limits,
                                  outdoor: e.target.value
                                }
                              }
                            }
                          })}
                          className="form-input-modern"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeSection === 'zones' && (
            <div className="config-section-modern">
              <div className="section-header">
                <div className="section-title">
                  <h2>Deployment Zones</h2>
                  <p className="section-description">Define operational areas and access restrictions</p>
                </div>
                <div className="section-actions">
                  <button onClick={() => {
                    const newZone: DeploymentZone = {
                      id: `zone_${Date.now()}`,
                      name: '',
                      type: 'indoor',
                      coordinates: '',
                      access_restrictions: [],
                      environmental_conditions: []
                    };
                    
                    setConfig({
                      ...config,
                      configuration_data: {
                        ...config.configuration_data,
                        deployment_zones: [...config.configuration_data.deployment_zones, newZone]
                      }
                    });
                  }} className="btn-primary">
                    <Plus className="btn-icon" />
                    Add Zone
                  </button>
                </div>
              </div>

              <div className="zones-grid-modern">
                {config.configuration_data.deployment_zones.map((zone, index) => (
                  <div key={zone.id} className="zone-card-modern">
                    <div className="card-header">
                      <div className="card-title">
                        <MapPin className="card-icon" />
                        <h3>Zone {index + 1}</h3>
                      </div>
                      <button 
                        onClick={() => {
                          const updatedZones = config.configuration_data.deployment_zones.filter((_, i) => i !== index);
                          setConfig({
                            ...config,
                            configuration_data: {
                              ...config.configuration_data,
                              deployment_zones: updatedZones
                            }
                          });
                        }}
                        className="btn-danger"
                      >
                        <Trash2 className="btn-icon" />
                        Remove
                      </button>
                    </div>

                    <div className="card-content">
                      <div className="form-group-modern">
                        <label>Zone Name</label>
                        <div className="input-wrapper">
                          <input
                            type="text"
                            value={zone.name}
                            onChange={(e) => {
                              const updatedZones = [...config.configuration_data.deployment_zones];
                              updatedZones[index] = { ...updatedZones[index], name: e.target.value };
                              setConfig({
                                ...config,
                                configuration_data: {
                                  ...config.configuration_data,
                                  deployment_zones: updatedZones
                                }
                              });
                            }}
                            className="form-input-modern"
                            placeholder="e.g., Warehouse A, Lobby, Parking Lot"
                          />
                        </div>
                      </div>

                      <div className="form-group-modern">
                        <label>Zone Type</label>
                        <div className="select-wrapper">
                          <select
                            value={zone.type}
                            onChange={(e) => {
                              const updatedZones = [...config.configuration_data.deployment_zones];
                              updatedZones[index] = { ...updatedZones[index], type: e.target.value as any };
                              setConfig({
                                ...config,
                                configuration_data: {
                                  ...config.configuration_data,
                                  deployment_zones: updatedZones
                                }
                              });
                            }}
                            className="form-select-modern"
                          >
                            <option value="indoor">Indoor</option>
                            <option value="outdoor">Outdoor</option>
                            <option value="mixed">Mixed</option>
                          </select>
                        </div>
                      </div>

                      <div className="form-group-modern">
                        <label>Coordinates/Description</label>
                        <div className="input-wrapper">
                          <textarea
                            value={zone.coordinates}
                            onChange={(e) => {
                              const updatedZones = [...config.configuration_data.deployment_zones];
                              updatedZones[index] = { ...updatedZones[index], coordinates: e.target.value };
                              setConfig({
                                ...config,
                                configuration_data: {
                                  ...config.configuration_data,
                                  deployment_zones: updatedZones
                                }
                              });
                            }}
                            className="form-textarea-modern"
                            rows={3}
                            placeholder="GPS coordinates, floor plan coordinates, or description of area"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeSection === 'operations' && (
            <div className="config-section-modern">
              <div className="section-header">
                <div className="section-title">
                  <h2>Operational Hours</h2>
                  <p className="section-description">Set working hours and operational schedule</p>
                </div>
              </div>

              <div className="config-card-modern">
                <div className="card-header">
                  <div className="card-title">
                    <Zap className="card-icon" />
                    <h3>Weekly Schedule</h3>
                  </div>
                </div>
                <div className="card-content">
                  <div className="schedule-grid-modern">
                    {Object.entries(config.configuration_data.operational_hours).map(([day, hours]) => (
                      <div key={day} className="schedule-item-modern">
                        <div className="schedule-header">
                          <label className="schedule-toggle">
                            <input
                              type="checkbox"
                              checked={hours.active}
                              onChange={(e) => setConfig({
                                ...config,
                                configuration_data: {
                                  ...config.configuration_data,
                                  operational_hours: {
                                    ...config.configuration_data.operational_hours,
                                    [day]: { ...hours, active: e.target.checked }
                                  }
                                }
                              })}
                            />
                            <div className="schedule-toggle-switch"></div>
                          </label>
                          <div className="schedule-day">
                            <h4>{day.charAt(0).toUpperCase() + day.slice(1)}</h4>
                          </div>
                        </div>
                        
                        {hours.active && (
                          <div className="schedule-time-range">
                            <input
                              type="time"
                              value={hours.start}
                              onChange={(e) => setConfig({
                                ...config,
                                configuration_data: {
                                  ...config.configuration_data,
                                  operational_hours: {
                                    ...config.configuration_data.operational_hours,
                                    [day]: { ...hours, start: e.target.value }
                                  }
                                }
                              })}
                              className="time-input-modern"
                            />
                            <span className="time-separator">to</span>
                            <input
                              type="time"
                              value={hours.end}
                              onChange={(e) => setConfig({
                                ...config,
                                configuration_data: {
                                  ...config.configuration_data,
                                  operational_hours: {
                                    ...config.configuration_data.operational_hours,
                                    [day]: { ...hours, end: e.target.value }
                                  }
                                }
                              })}
                              className="time-input-modern"
                            />
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeSection === 'maintenance' && (
            <div className="config-section-modern">
              <div className="section-header">
                <div className="section-title">
                  <h2>Maintenance Schedule</h2>
                  <p className="section-description">Configure maintenance tasks and notifications</p>
                </div>
              </div>

              <div className="config-grid-modern">
                <div className="config-card-modern">
                  <div className="card-header">
                    <div className="card-title">
                      <Settings className="card-icon" />
                      <h3>Maintenance Settings</h3>
                    </div>
                  </div>
                  <div className="card-content">
                    <div className="form-group-modern">
                      <label>Maintenance Frequency</label>
                      <div className="select-wrapper">
                        <select
                          value={config.configuration_data.maintenance_schedule.frequency}
                          onChange={(e) => setConfig({
                            ...config,
                            configuration_data: {
                              ...config.configuration_data,
                              maintenance_schedule: {
                                ...config.configuration_data.maintenance_schedule,
                                frequency: e.target.value as any
                              }
                            }
                          })}
                          className="form-select-modern"
                        >
                          <option value="daily">Daily</option>
                          <option value="weekly">Weekly</option>
                          <option value="monthly">Monthly</option>
                          <option value="quarterly">Quarterly</option>
                        </select>
                      </div>
                    </div>

                    <div className="toggle-group-modern">
                      <label className="toggle-option-modern">
                        <input
                          type="checkbox"
                          checked={config.configuration_data.maintenance_schedule.auto_scheduling}
                          onChange={(e) => setConfig({
                            ...config,
                            configuration_data: {
                              ...config.configuration_data,
                              maintenance_schedule: {
                                ...config.configuration_data.maintenance_schedule,
                                auto_scheduling: e.target.checked
                              }
                            }
                          })}
                        />
                        <div className="toggle-content">
                          <div className="toggle-switch"></div>
                          <div className="toggle-label">
                            <h4>Auto-scheduling</h4>
                            <p>Automatically schedule maintenance tasks</p>
                          </div>
                        </div>
                      </label>
                    </div>
                  </div>
                </div>

                <div className="config-card-modern">
                  <div className="card-header">
                    <div className="card-title">
                      <AlertCircle className="card-icon" />
                      <h3>Notification Preferences</h3>
                    </div>
                  </div>
                  <div className="card-content">
                    <div className="toggle-group-modern">
                      <label className="toggle-option-modern">
                        <input
                          type="checkbox"
                          checked={config.configuration_data.maintenance_schedule.notification_preferences.email}
                          onChange={(e) => setConfig({
                            ...config,
                            configuration_data: {
                              ...config.configuration_data,
                              maintenance_schedule: {
                                ...config.configuration_data.maintenance_schedule,
                                notification_preferences: {
                                  ...config.configuration_data.maintenance_schedule.notification_preferences,
                                  email: e.target.checked
                                }
                              }
                            }
                          })}
                        />
                        <div className="toggle-content">
                          <div className="toggle-switch"></div>
                          <div className="toggle-label">
                            <h4>Email Notifications</h4>
                            <p>Receive maintenance alerts via email</p>
                          </div>
                        </div>
                      </label>

                      <label className="toggle-option-modern">
                        <input
                          type="checkbox"
                          checked={config.configuration_data.maintenance_schedule.notification_preferences.sms}
                          onChange={(e) => setConfig({
                            ...config,
                            configuration_data: {
                              ...config.configuration_data,
                              maintenance_schedule: {
                                ...config.configuration_data.maintenance_schedule,
                                notification_preferences: {
                                  ...config.configuration_data.maintenance_schedule.notification_preferences,
                                  sms: e.target.checked
                                }
                              }
                            }
                          })}
                        />
                        <div className="toggle-content">
                          <div className="toggle-switch"></div>
                          <div className="toggle-label">
                            <h4>SMS Notifications</h4>
                            <p>Receive maintenance alerts via SMS</p>
                          </div>
                        </div>
                      </label>

                      <label className="toggle-option-modern">
                        <input
                          type="checkbox"
                          checked={config.configuration_data.maintenance_schedule.notification_preferences.dashboard}
                          onChange={(e) => setConfig({
                            ...config,
                            configuration_data: {
                              ...config.configuration_data,
                              maintenance_schedule: {
                                ...config.configuration_data.maintenance_schedule,
                                notification_preferences: {
                                  ...config.configuration_data.maintenance_schedule.notification_preferences,
                                  dashboard: e.target.checked
                                }
                              }
                            }
                          })}
                        />
                        <div className="toggle-content">
                          <div className="toggle-switch"></div>
                          <div className="toggle-label">
                            <h4>Dashboard Notifications</h4>
                            <p>Show maintenance alerts in dashboard</p>
                          </div>
                        </div>
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
