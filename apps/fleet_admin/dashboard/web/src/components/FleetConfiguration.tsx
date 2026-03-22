import { useState } from 'react';
import { Bot, Settings, Plus, Trash2, Save, X, Check, AlertCircle, Wifi, Battery, Package, MapPin, Shield, Zap } from 'lucide-react';

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
  { model: 'Cottage-R1', type: 'delivery', capabilities: ['package_delivery', 'navigation', 'obstacle_avoidance'] },
  { model: 'Cottage-S1', type: 'security', capabilities: ['surveillance', 'patrol', 'alert_system'] },
  { model: 'Cottage-C1', type: 'cleaning', capabilities: ['floor_cleaning', 'surface_sanitization', 'waste_collection'] },
  { model: 'Cottage-I1', type: 'inspection', capabilities: ['visual_inspection', 'sensor_monitoring', 'reporting'] },
  { model: 'Cottage-M1', type: 'maintenance', capabilities: ['diagnostics', 'repair_assistance', 'preventive_maintenance'] }
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

export function FleetConfiguration({ customer, onSaveConfiguration, onCancel }: FleetConfigurationProps) {
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
    const newRobot: RobotType = {
      id: `robot_${Date.now()}`,
      model: ROBOT_MODELS[0].model,
      type: ROBOT_MODELS[0].type as any,
      count: 1,
      capabilities: ROBOT_MODELS[0].capabilities,
      specifications: {
        weight_capacity: '50 lbs',
        battery_life: '8 hours',
        speed: '3 mph',
        navigation: 'LiDAR + GPS'
      }
    };
    
    setConfig({
      ...config,
      configuration_data: {
        ...config.configuration_data,
        robot_types: [...config.configuration_data.robot_types, newRobot]
      }
    });
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

  const addDeploymentZone = () => {
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
  };

  const updateDeploymentZone = (index: number, field: keyof DeploymentZone, value: any) => {
    const updatedZones = [...config.configuration_data.deployment_zones];
    updatedZones[index] = { ...updatedZones[index], [field]: value };
    
    setConfig({
      ...config,
      configuration_data: {
        ...config.configuration_data,
        deployment_zones: updatedZones
      }
    });
  };

  const removeDeploymentZone = (index: number) => {
    const updatedZones = config.configuration_data.deployment_zones.filter((_, i) => i !== index);
    
    setConfig({
      ...config,
      configuration_data: {
        ...config.configuration_data,
        deployment_zones: updatedZones
      }
    });
  };

  return (
    <div className="fleet-configuration">
      <div className="config-header">
        <div className="header-content">
          <div className="header-title">
            <Settings className="title-icon" />
            <h2>Fleet Configuration</h2>
            <span className="customer-name">{customer.name}</span>
          </div>
          <div className="header-actions">
            <button onClick={onCancel} className="btn-secondary">
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

      <div className="config-content">
        <div className="config-sidebar">
          <div className="section-nav">
            <button 
              className={`nav-item ${activeSection === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveSection('overview')}
            >
              <Package className="nav-icon" />
              Overview
            </button>
            <button 
              className={`nav-item ${activeSection === 'robots' ? 'active' : ''}`}
              onClick={() => setActiveSection('robots')}
            >
              <Bot className="nav-icon" />
              Robot Types
            </button>
            <button 
              className={`nav-item ${activeSection === 'network' ? 'active' : ''}`}
              onClick={() => setActiveSection('network')}
            >
              <Wifi className="nav-icon" />
              Network
            </button>
            <button 
              className={`nav-item ${activeSection === 'safety' ? 'active' : ''}`}
              onClick={() => setActiveSection('safety')}
            >
              <Shield className="nav-icon" />
              Safety
            </button>
            <button 
              className={`nav-item ${activeSection === 'zones' ? 'active' : ''}`}
              onClick={() => setActiveSection('zones')}
            >
              <MapPin className="nav-icon" />
              Zones
            </button>
            <button 
              className={`nav-item ${activeSection === 'operations' ? 'active' : ''}`}
              onClick={() => setActiveSection('operations')}
            >
              <Zap className="nav-icon" />
              Operations
            </button>
            <button 
              className={`nav-item ${activeSection === 'maintenance' ? 'active' : ''}`}
              onClick={() => setActiveSection('maintenance')}
            >
              <Settings className="nav-icon" />
              Maintenance
            </button>
          </div>
        </div>

        <div className="config-main">
          {activeSection === 'overview' && (
            <div className="config-section">
              <h3>Configuration Overview</h3>
              <div className="overview-grid">
                <div className="form-group">
                  <label>Configuration Name</label>
                  <input
                    type="text"
                    value={config.configuration_name}
                    onChange={(e) => setConfig({ ...config, configuration_name: e.target.value })}
                    className={`form-input ${errors.configuration_name ? 'error' : ''}`}
                  />
                  {errors.configuration_name && <span className="error-message">{errors.configuration_name}</span>}
                </div>

                <div className="form-group">
                  <label>Environment Type</label>
                  <select
                    value={config.configuration_data.environment_type}
                    onChange={(e) => setConfig({
                      ...config,
                      configuration_data: {
                        ...config.configuration_data,
                        environment_type: e.target.value as any
                      }
                    })}
                    className="form-input"
                  >
                    <option value="indoor">Indoor Only</option>
                    <option value="outdoor">Outdoor Only</option>
                    <option value="mixed">Mixed Environment</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Total Robot Count</label>
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
                    className={`form-input ${errors.robot_count ? 'error' : ''}`}
                    min="1"
                  />
                  {errors.robot_count && <span className="error-message">{errors.robot_count}</span>}
                </div>

                <div className="summary-cards">
                  <div className="summary-card">
                    <Bot className="card-icon" />
                    <div className="card-content">
                      <h4>Robot Types</h4>
                      <p>{config.configuration_data.robot_types.length} configured</p>
                    </div>
                  </div>
                  <div className="summary-card">
                    <MapPin className="card-icon" />
                    <div className="card-content">
                      <h4>Deployment Zones</h4>
                      <p>{config.configuration_data.deployment_zones.length} zones</p>
                    </div>
                  </div>
                  <div className="summary-card">
                    <Wifi className="card-icon" />
                    <div className="card-content">
                      <h4>Network</h4>
                      <p>{config.configuration_data.network_config.ssid || 'Not configured'}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeSection === 'robots' && (
            <div className="config-section">
              <div className="section-header">
                <h3>Robot Types</h3>
                <button onClick={addRobotType} className="btn-primary">
                  <Plus className="btn-icon" />
                  Add Robot Type
                </button>
              </div>

              {errors.robot_types && <div className="error-banner">{errors.robot_types}</div>}

              <div className="robots-list">
                {config.configuration_data.robot_types.map((robot, index) => (
                  <div key={robot.id} className="robot-card">
                    <div className="robot-header">
                      <h4>Robot {index + 1}</h4>
                      <button 
                        onClick={() => removeRobotType(index)}
                        className="btn-delete"
                      >
                        <Trash2 className="btn-icon" />
                        Remove
                      </button>
                    </div>

                    <div className="robot-form">
                      <div className="form-row">
                        <div className="form-group">
                          <label>Model</label>
                          <select
                            value={robot.model}
                            onChange={(e) => {
                              const selectedModel = ROBOT_MODELS.find(m => m.model === e.target.value);
                              if (selectedModel) {
                                updateRobotType(index, 'model', selectedModel.model);
                                updateRobotType(index, 'type', selectedModel.type);
                                updateRobotType(index, 'capabilities', selectedModel.capabilities);
                              }
                            }}
                            className="form-input"
                          >
                            {ROBOT_MODELS.map(model => (
                              <option key={model.model} value={model.model}>{model.model}</option>
                            ))}
                          </select>
                        </div>

                        <div className="form-group">
                          <label>Quantity</label>
                          <input
                            type="number"
                            value={robot.count}
                            onChange={(e) => updateRobotType(index, 'count', parseInt(e.target.value) || 1)}
                            className="form-input"
                            min="1"
                          />
                        </div>
                      </div>

                      <div className="form-group">
                        <label>Capabilities</label>
                        <div className="capabilities-list">
                          {robot.capabilities.map((capability, capIndex) => (
                            <span key={capIndex} className="capability-tag">
                              {capability}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div className="form-row">
                        <div className="form-group">
                          <label>Weight Capacity</label>
                          <input
                            type="text"
                            value={robot.specifications.weight_capacity}
                            onChange={(e) => updateRobotType(index, 'specifications', {
                              ...robot.specifications,
                              weight_capacity: e.target.value
                            })}
                            className="form-input"
                          />
                        </div>

                        <div className="form-group">
                          <label>Battery Life</label>
                          <input
                            type="text"
                            value={robot.specifications.battery_life}
                            onChange={(e) => updateRobotType(index, 'specifications', {
                              ...robot.specifications,
                              battery_life: e.target.value
                            })}
                            className="form-input"
                          />
                        </div>

                        <div className="form-group">
                          <label>Speed</label>
                          <input
                            type="text"
                            value={robot.specifications.speed}
                            onChange={(e) => updateRobotType(index, 'specifications', {
                              ...robot.specifications,
                              speed: e.target.value
                            })}
                            className="form-input"
                          />
                        </div>

                        <div className="form-group">
                          <label>Navigation</label>
                          <input
                            type="text"
                            value={robot.specifications.navigation}
                            onChange={(e) => updateRobotType(index, 'specifications', {
                              ...robot.specifications,
                              navigation: e.target.value
                            })}
                            className="form-input"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeSection === 'network' && (
            <div className="config-section">
              <h3>Network Configuration</h3>
              <div className="network-form">
                <div className="form-row">
                  <div className="form-group">
                    <label>Network SSID</label>
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
                      className="form-input"
                      placeholder="Enter WiFi network name"
                    />
                  </div>

                  <div className="form-group">
                    <label>Security Type</label>
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
                      className="form-input"
                    >
                      <option value="WPA2">WPA2</option>
                      <option value="WPA3">WPA3</option>
                      <option value="Open">Open</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Frequency Band</label>
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
                      className="form-input"
                    >
                      <option value="2.4GHz">2.4GHz</option>
                      <option value="5GHz">5GHz</option>
                      <option value="Dual">Dual Band</option>
                    </select>
                  </div>
                </div>

                <div className="checkbox-group">
                  <label className="checkbox-label">
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
                    <span className="checkbox-text">Enable Mesh Network</span>
                  </label>

                  <label className="checkbox-label">
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
                    <span className="checkbox-text">Enable Network Failover</span>
                  </label>
                </div>
              </div>
            </div>
          )}

          {activeSection === 'safety' && (
            <div className="config-section">
              <h3>Safety Configuration</h3>
              <div className="safety-form">
                <div className="checkbox-group">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={config.configuration_data.safety_config.emergency_stop}
                      onChange={(e) => setConfig({
                        ...config,
                        configuration_data: {
                          ...config.configuration_data,
                          safety_config: {
                            ...config.configuration_data.safety_config,
                            emergency_stop: e.target.checked
                          }
                        }
                      })}
                    />
                    <span className="checkbox-text">Emergency Stop Enabled</span>
                  </label>

                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={config.configuration_data.safety_config.obstacle_detection}
                      onChange={(e) => setConfig({
                        ...config,
                        configuration_data: {
                          ...config.configuration_data,
                          safety_config: {
                            ...config.configuration_data.safety_config,
                            obstacle_detection: e.target.checked
                          }
                        }
                      })}
                    />
                    <span className="checkbox-text">Obstacle Detection</span>
                  </label>

                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={config.configuration_data.safety_config.human_detection}
                      onChange={(e) => setConfig({
                        ...config,
                        configuration_data: {
                          ...config.configuration_data,
                          safety_config: {
                            ...config.configuration_data.safety_config,
                            human_detection: e.target.checked
                          }
                        }
                      })}
                    />
                    <span className="checkbox-text">Human Detection</span>
                  </label>

                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={config.configuration_data.safety_config.collision_prevention}
                      onChange={(e) => setConfig({
                        ...config,
                        configuration_data: {
                          ...config.configuration_data,
                          safety_config: {
                            ...config.configuration_data.safety_config,
                            collision_prevention: e.target.checked
                          }
                        }
                      })}
                    />
                    <span className="checkbox-text">Collision Prevention</span>
                  </label>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Indoor Speed Limit</label>
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
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label>Outdoor Speed Limit</label>
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
                      className="form-input"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeSection === 'zones' && (
            <div className="config-section">
              <div className="section-header">
                <h3>Deployment Zones</h3>
                <button onClick={addDeploymentZone} className="btn-primary">
                  <Plus className="btn-icon" />
                  Add Zone
                </button>
              </div>

              <div className="zones-list">
                {config.configuration_data.deployment_zones.map((zone, index) => (
                  <div key={zone.id} className="zone-card">
                    <div className="zone-header">
                      <h4>Zone {index + 1}</h4>
                      <button 
                        onClick={() => removeDeploymentZone(index)}
                        className="btn-delete"
                      >
                        <Trash2 className="btn-icon" />
                        Remove
                      </button>
                    </div>

                    <div className="zone-form">
                      <div className="form-row">
                        <div className="form-group">
                          <label>Zone Name</label>
                          <input
                            type="text"
                            value={zone.name}
                            onChange={(e) => updateDeploymentZone(index, 'name', e.target.value)}
                            className="form-input"
                            placeholder="e.g., Warehouse A, Lobby, Parking Lot"
                          />
                        </div>

                        <div className="form-group">
                          <label>Zone Type</label>
                          <select
                            value={zone.type}
                            onChange={(e) => updateDeploymentZone(index, 'type', e.target.value as any)}
                            className="form-input"
                          >
                            <option value="indoor">Indoor</option>
                            <option value="outdoor">Outdoor</option>
                            <option value="mixed">Mixed</option>
                          </select>
                        </div>
                      </div>

                      <div className="form-group">
                        <label>Coordinates/Description</label>
                        <textarea
                          value={zone.coordinates}
                          onChange={(e) => updateDeploymentZone(index, 'coordinates', e.target.value)}
                          className="form-input"
                          rows={3}
                          placeholder="GPS coordinates, floor plan coordinates, or description of area"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeSection === 'operations' && (
            <div className="config-section">
              <h3>Operational Hours</h3>
              <div className="operations-form">
                {Object.entries(config.configuration_data.operational_hours).map(([day, hours]) => (
                  <div key={day} className="day-schedule">
                    <div className="day-header">
                      <label className="checkbox-label">
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
                        <span className="day-name">{day.charAt(0).toUpperCase() + day.slice(1)}</span>
                      </label>
                    </div>
                    
                    {hours.active && (
                      <div className="time-range">
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
                          className="time-input"
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
                          className="time-input"
                        />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeSection === 'maintenance' && (
            <div className="config-section">
              <h3>Maintenance Schedule</h3>
              <div className="maintenance-form">
                <div className="form-group">
                  <label>Maintenance Frequency</label>
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
                    className="form-input"
                  >
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                    <option value="quarterly">Quarterly</option>
                  </select>
                </div>

                <div className="checkbox-group">
                  <label className="checkbox-label">
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
                    <span className="checkbox-text">Auto-scheduling Enabled</span>
                  </label>
                </div>

                <div className="notification-preferences">
                  <h4>Notification Preferences</h4>
                  <div className="checkbox-group">
                    <label className="checkbox-label">
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
                      <span className="checkbox-text">Email Notifications</span>
                    </label>

                    <label className="checkbox-label">
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
                      <span className="checkbox-text">SMS Notifications</span>
                    </label>

                    <label className="checkbox-label">
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
                      <span className="checkbox-text">Dashboard Notifications</span>
                    </label>
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
