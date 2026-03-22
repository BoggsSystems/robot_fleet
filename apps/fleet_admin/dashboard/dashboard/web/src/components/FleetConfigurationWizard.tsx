import { useState } from 'react';
import { X, ArrowRight, ArrowLeft, Check, Building2, ShoppingCart, Stethoscope, Factory, HardHat, Hotel, GraduationCap, Briefcase, Bot, Package, Shield, Zap, Settings, TrendingUp, Users, MapPin, Clock, DollarSign, Wifi } from 'lucide-react';
import './FleetConfigurationWizard.css';

interface FleetConfigurationWizardProps {
  isOpen: boolean;
  onClose: () => void;
  customer: any;
  onSaveConfiguration: (config: FleetConfig) => void;
}

interface IndustryTemplate {
  id: string;
  name: string;
  icon: React.ReactNode;
  description: string;
  useCases: string[];
  recommendedRobots: {
    model: string;
    type: string;
    quantity: number;
    purpose: string;
    capabilities: string[];
  }[];
  estimatedCost: number;
  deploymentTime: string;
  roi: string;
}

interface FleetConfig {
  id: string;
  customer_id: string;
  configuration_name: string;
  industry: string;
  configuration_data: {
    environment_type: 'indoor' | 'outdoor' | 'mixed';
    robot_count: number;
    robot_types: any[];
    network_config: any;
    safety_config: any;
    deployment_zones: any[];
    operational_hours: any;
    maintenance_schedule: any;
  };
  created_at: string;
  updated_at: string;
}

const INDUSTRY_TEMPLATES: IndustryTemplate[] = [
  {
    id: 'warehouse',
    name: 'Warehouse & Logistics',
    icon: <Building2 className="industry-icon" />,
    description: 'Automated warehouse operations and inventory management',
    useCases: ['Package delivery', 'Inventory tracking', 'Security patrols', 'Facility maintenance'],
    recommendedRobots: [
      {
        model: 'Unitree A1',
        type: 'delivery',
        quantity: 4,
        purpose: 'Package transport between zones',
        capabilities: ['package_delivery', 'navigation', 'climbing', 'dynamic_balance']
      },
      {
        model: 'Unitree Go1',
        type: 'security',
        quantity: 2,
        purpose: 'Security patrols and surveillance',
        capabilities: ['surveillance', 'patrol', 'human_detection', 'night_vision']
      },
      {
        model: 'Unitree Z1',
        type: 'maintenance',
        quantity: 1,
        purpose: 'Facility maintenance and repairs',
        capabilities: ['diagnostics', 'repair_assistance', 'tool_carrying', 'preventive_maintenance']
      }
    ],
    estimatedCost: 95000,
    deploymentTime: '2-3 weeks',
    roi: '18-24 months'
  },
  {
    id: 'retail',
    name: 'Retail & Commerce',
    icon: <ShoppingCart className="industry-icon" />,
    description: 'Customer service, inventory management, and store security',
    useCases: ['Customer assistance', 'Inventory restocking', 'Loss prevention', 'Store monitoring'],
    recommendedRobots: [
      {
        model: 'Unitree A1',
        type: 'delivery',
        quantity: 2,
        purpose: 'Inventory restocking and customer assistance',
        capabilities: ['package_delivery', 'navigation', 'obstacle_avoidance', 'dynamic_balance']
      },
      {
        model: 'Unitree Go1',
        type: 'security',
        quantity: 2,
        purpose: 'Store security and customer monitoring',
        capabilities: ['surveillance', 'patrol', 'human_detection', 'alert_system']
      }
    ],
    estimatedCost: 68000,
    deploymentTime: '1-2 weeks',
    roi: '12-18 months'
  },
  {
    id: 'healthcare',
    name: 'Healthcare & Hospitals',
    icon: <Stethoscope className="industry-icon" />,
    description: 'Medical supply delivery, patient monitoring, and facility inspection',
    useCases: ['Medical supply transport', 'Patient monitoring', 'Facility inspection', 'Emergency response'],
    recommendedRobots: [
      {
        model: 'Unitree A1',
        type: 'delivery',
        quantity: 3,
        purpose: 'Medical supply and specimen delivery',
        capabilities: ['package_delivery', 'navigation', 'obstacle_avoidance', 'climbing']
      },
      {
        model: 'Unitree Aliengo',
        type: 'inspection',
        quantity: 2,
        purpose: 'Facility inspection and environmental monitoring',
        capabilities: ['visual_inspection', 'thermal_imaging', 'sensor_monitoring', 'gas_detection']
      },
      {
        model: 'Unitree Go1',
        type: 'security',
        quantity: 1,
        purpose: 'Patient monitoring and emergency response',
        capabilities: ['surveillance', 'human_detection', 'alert_system', 'night_vision']
      }
    ],
    estimatedCost: 116000,
    deploymentTime: '3-4 weeks',
    roi: '15-20 months'
  },
  {
    id: 'manufacturing',
    name: 'Manufacturing',
    icon: <Factory className="industry-icon" />,
    description: 'Production line monitoring, quality control, and maintenance',
    useCases: ['Production monitoring', 'Quality inspection', 'Maintenance support', 'Safety patrols'],
    recommendedRobots: [
      {
        model: 'Unitree Aliengo',
        type: 'inspection',
        quantity: 3,
        purpose: 'Quality control and production monitoring',
        capabilities: ['visual_inspection', 'thermal_imaging', 'sensor_monitoring', 'reporting']
      },
      {
        model: 'Unitree Z1',
        type: 'maintenance',
        quantity: 2,
        purpose: 'Equipment maintenance and repair support',
        capabilities: ['diagnostics', 'repair_assistance', 'tool_carrying', 'remote_operation']
      },
      {
        model: 'Unitree A1',
        type: 'delivery',
        quantity: 2,
        purpose: 'Parts and material transport',
        capabilities: ['package_delivery', 'navigation', 'climbing', 'dynamic_balance']
      },
      {
        model: 'Unitree Go1',
        type: 'security',
        quantity: 1,
        purpose: 'Safety patrols and emergency response',
        capabilities: ['surveillance', 'patrol', 'human_detection', 'alert_system']
      }
    ],
    estimatedCost: 158000,
    deploymentTime: '4-5 weeks',
    roi: '20-30 months'
  },
  {
    id: 'construction',
    name: 'Construction',
    icon: <HardHat className="industry-icon" />,
    description: 'Site monitoring, material transport, and safety inspections',
    useCases: ['Site surveillance', 'Material delivery', 'Safety inspections', 'Progress monitoring'],
    recommendedRobots: [
      {
        model: 'Unitree Go1',
        type: 'security',
        quantity: 2,
        purpose: 'Site security and safety monitoring',
        capabilities: ['surveillance', 'patrol', 'human_detection', 'night_vision']
      },
      {
        model: 'Unitree Aliengo',
        type: 'inspection',
        quantity: 2,
        purpose: 'Site inspection and progress monitoring',
        capabilities: ['visual_inspection', 'thermal_imaging', 'sensor_monitoring', 'reporting']
      },
      {
        model: 'Unitree A1',
        type: 'delivery',
        quantity: 2,
        purpose: 'Tool and material transport',
        capabilities: ['package_delivery', 'navigation', 'climbing', 'dynamic_balance']
      }
    ],
    estimatedCost: 106000,
    deploymentTime: '2-3 weeks',
    roi: '12-18 months'
  },
  {
    id: 'hospitality',
    name: 'Hospitality',
    icon: <Hotel className="industry-icon" />,
    description: 'Guest services, room service, and facility management',
    useCases: ['Room service delivery', 'Guest assistance', 'Facility monitoring', 'Security'],
    recommendedRobots: [
      {
        model: 'Unitree A1',
        type: 'delivery',
        quantity: 3,
        purpose: 'Room service and guest amenities delivery',
        capabilities: ['package_delivery', 'navigation', 'obstacle_avoidance', 'dynamic_balance']
      },
      {
        model: 'Unitree Go1',
        type: 'security',
        quantity: 1,
        purpose: 'Guest safety and facility security',
        capabilities: ['surveillance', 'patrol', 'human_detection', 'alert_system']
      }
    ],
    estimatedCost: 66000,
    deploymentTime: '1-2 weeks',
    roi: '10-15 months'
  },
  {
    id: 'education',
    name: 'Education Campuses',
    icon: <GraduationCap className="industry-icon" />,
    description: 'Campus security, facility monitoring, and support services',
    useCases: ['Campus patrols', 'Facility monitoring', 'Emergency response', 'Support services'],
    recommendedRobots: [
      {
        model: 'Unitree Go1',
        type: 'security',
        quantity: 3,
        purpose: 'Campus security and student safety',
        capabilities: ['surveillance', 'patrol', 'human_detection', 'night_vision']
      },
      {
        model: 'Unitree A1',
        type: 'delivery',
        quantity: 2,
        purpose: 'Campus deliveries and support services',
        capabilities: ['package_delivery', 'navigation', 'obstacle_avoidance', 'climbing']
      }
    ],
    estimatedCost: 88000,
    deploymentTime: '2-3 weeks',
    roi: '15-20 months'
  },
  {
    id: 'corporate',
    name: 'Corporate Offices',
    icon: <Briefcase className="industry-icon" />,
    description: 'Office security, facility management, and employee services',
    useCases: ['Office security', 'Facility monitoring', 'Mail delivery', 'Employee assistance'],
    recommendedRobots: [
      {
        model: 'Unitree Go1',
        type: 'security',
        quantity: 2,
        purpose: 'Office security and access control',
        capabilities: ['surveillance', 'patrol', 'human_detection', 'alert_system']
      },
      {
        model: 'Unitree A1',
        type: 'delivery',
        quantity: 2,
        purpose: 'Mail and package delivery',
        capabilities: ['package_delivery', 'navigation', 'obstacle_avoidance', 'dynamic_balance']
      },
      {
        model: 'Unitree Z1',
        type: 'maintenance',
        quantity: 1,
        purpose: 'Facility maintenance and support',
        capabilities: ['diagnostics', 'repair_assistance', 'preventive_maintenance', 'tool_carrying']
      }
    ],
    estimatedCost: 85000,
    deploymentTime: '2-3 weeks',
    roi: '12-18 months'
  }
];

export function FleetConfigurationWizard({ isOpen, onClose, customer, onSaveConfiguration }: FleetConfigurationWizardProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedIndustry, setSelectedIndustry] = useState<IndustryTemplate | null>(null);
  const [customizationOptions, setCustomizationOptions] = useState({
    facilitySize: '',
    operatingHours: '',
    specialRequirements: '',
    budget: ''
  });

  if (!isOpen) return null;

  const handleIndustrySelect = (industry: IndustryTemplate) => {
    setSelectedIndustry(industry);
    setCurrentStep(2);
  };

  const handleCustomizationSubmit = () => {
    setCurrentStep(3);
  };

  const handleConfigurationSave = () => {
    if (!selectedIndustry) return;

    const fleetConfig: FleetConfig = {
      id: `fleet_${Date.now()}`,
      customer_id: customer.id,
      configuration_name: `${customer.company}_${selectedIndustry.name}_Fleet`,
      industry: selectedIndustry.id,
      configuration_data: {
        environment_type: 'mixed',
        robot_count: selectedIndustry.recommendedRobots.reduce((sum, robot) => sum + robot.quantity, 0),
        robot_types: selectedIndustry.recommendedRobots.map(robot => ({
          id: `robot_${Date.now()}_${robot.model}`,
          model: robot.model,
          type: robot.type,
          count: robot.quantity,
          capabilities: robot.capabilities,
          specifications: {
            weight_capacity: '5 kg',
            battery_life: '8 hours',
            speed: '3 mph',
            navigation: 'LiDAR + GPS'
          }
        })),
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
      },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    onSaveConfiguration(fleetConfig);
    onClose();
  };

  const renderStep1 = () => (
    <div className="wizard-step">
      <div className="step-header">
        <h2>Select Your Industry</h2>
        <p>Choose the industry that best matches your operations</p>
      </div>
      
      <div className="industry-grid">
        {INDUSTRY_TEMPLATES.map((industry) => (
          <div
            key={industry.id}
            className="industry-card"
            onClick={() => handleIndustrySelect(industry)}
          >
            <div className="industry-icon-wrapper">
              {industry.icon}
            </div>
            <h3>{industry.name}</h3>
            <p>{industry.description}</p>
            <div className="industry-stats">
              <div className="stat">
                <Bot className="stat-icon" />
                <span>{industry.recommendedRobots.length} Robots</span>
              </div>
              <div className="stat">
                <DollarSign className="stat-icon" />
                <span>${industry.estimatedCost.toLocaleString()}</span>
              </div>
            </div>
            <div className="industry-roi">
              <TrendingUp className="roi-icon" />
              <span>ROI: {industry.roi}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="wizard-step">
      <div className="step-header">
        <h2>Customize Your Fleet</h2>
        <p>Tell us about your specific requirements</p>
      </div>

      <div className="customization-content">
        <div className="selected-industry">
          <div className="industry-summary">
            <div className="industry-icon-wrapper">
              {selectedIndustry?.icon}
            </div>
            <div>
              <h3>{selectedIndustry?.name}</h3>
              <p>{selectedIndustry?.description}</p>
            </div>
          </div>
        </div>

        <div className="customization-form">
          <div className="form-group">
            <label>
              <MapPin className="label-icon" />
              Facility Size
            </label>
            <select
              value={customizationOptions.facilitySize}
              onChange={(e) => setCustomizationOptions({...customizationOptions, facilitySize: e.target.value})}
            >
              <option value="">Select facility size</option>
              <option value="small">Small (&lt;10,000 sq ft)</option>
              <option value="medium">Medium (10,000-50,000 sq ft)</option>
              <option value="large">Large (50,000-100,000 sq ft)</option>
              <option value="xlarge">Extra Large (&gt;100,000 sq ft)</option>
            </select>
          </div>

          <div className="form-group">
            <label>
              <Clock className="label-icon" />
              Operating Hours
            </label>
            <select
              value={customizationOptions.operatingHours}
              onChange={(e) => setCustomizationOptions({...customizationOptions, operatingHours: e.target.value})}
            >
              <option value="">Select operating hours</option>
              <option value="standard">Standard (9am-5pm)</option>
              <option value="extended">Extended (7am-9pm)</option>
              <option value="247">24/7 Operations</option>
              <option value="custom">Custom Schedule</option>
            </select>
          </div>

          <div className="form-group">
            <label>
              <DollarSign className="label-icon" />
              Budget Range
            </label>
            <select
              value={customizationOptions.budget}
              onChange={(e) => setCustomizationOptions({...customizationOptions, budget: e.target.value})}
            >
              <option value="">Select budget range</option>
              <option value="50-100">$50,000 - $100,000</option>
              <option value="100-150">$100,000 - $150,000</option>
              <option value="150-200">$150,000 - $200,000</option>
              <option value="200+">$200,000+</option>
            </select>
          </div>

          <div className="form-group">
            <label>
              <Settings className="label-icon" />
              Special Requirements
            </label>
            <textarea
              value={customizationOptions.specialRequirements}
              onChange={(e) => setCustomizationOptions({...customizationOptions, specialRequirements: e.target.value})}
              placeholder="Any special requirements or considerations..."
              rows={3}
            />
          </div>
        </div>

        <div className="recommended-fleet">
          <h3>Recommended Fleet Configuration</h3>
          <div className="fleet-preview">
            {selectedIndustry?.recommendedRobots.map((robot, index) => (
              <div key={index} className="robot-preview-card">
                <div className="robot-header">
                  <h4>{robot.model}</h4>
                  <span className="robot-type">{robot.type}</span>
                </div>
                <div className="robot-details">
                  <div className="robot-quantity">
                    <span className="quantity-label">Quantity:</span>
                    <span className="quantity-value">{robot.quantity}</span>
                  </div>
                  <div className="robot-purpose">
                    <span className="purpose-label">Purpose:</span>
                    <span className="purpose-value">{robot.purpose}</span>
                  </div>
                </div>
                <div className="robot-capabilities">
                  {robot.capabilities.slice(0, 3).map((capability, capIndex) => (
                    <span key={capIndex} className="capability-tag">
                      {capability.replace('_', ' ')}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="wizard-step">
      <div className="step-header">
        <h2>Review Your Fleet Configuration</h2>
        <p>Confirm your customized fleet configuration before deployment</p>
      </div>

      <div className="review-content">
        <div className="configuration-summary">
          <div className="summary-header">
            <div className="industry-info">
              <div className="industry-icon-wrapper">
                {selectedIndustry?.icon}
              </div>
              <div>
                <h3>{selectedIndustry?.name}</h3>
                <p>{customer.company}</p>
              </div>
            </div>
            <div className="summary-stats">
              <div className="summary-stat">
                <Bot className="stat-icon" />
                <div>
                  <span className="stat-value">
                    {selectedIndustry?.recommendedRobots.reduce((sum, robot) => sum + robot.quantity, 0)}
                  </span>
                  <span className="stat-label">Total Robots</span>
                </div>
              </div>
              <div className="summary-stat">
                <DollarSign className="stat-icon" />
                <div>
                  <span className="stat-value">
                    ${selectedIndustry?.estimatedCost.toLocaleString()}
                  </span>
                  <span className="stat-label">Est. Cost</span>
                </div>
              </div>
              <div className="summary-stat">
                <TrendingUp className="stat-icon" />
                <div>
                  <span className="stat-value">{selectedIndustry?.roi}</span>
                  <span className="stat-label">ROI</span>
                </div>
              </div>
            </div>
          </div>

          <div className="deployment-details">
            <h4>Deployment Information</h4>
            <div className="detail-grid">
              <div className="detail-item">
                <Clock className="detail-icon" />
                <div>
                  <span className="detail-label">Deployment Time</span>
                  <span className="detail-value">{selectedIndustry?.deploymentTime}</span>
                </div>
              </div>
              <div className="detail-item">
                <Wifi className="detail-icon" />
                <div>
                  <span className="detail-label">Network Requirements</span>
                  <span className="detail-value">WiFi + 4G Coverage</span>
                </div>
              </div>
              <div className="detail-item">
                <Users className="detail-icon" />
                <div>
                  <span className="detail-label">Training Required</span>
                  <span className="detail-value">2-3 days</span>
                </div>
              </div>
            </div>
          </div>

          <div className="use-cases">
            <h4>Use Cases</h4>
            <ul>
              {selectedIndustry?.useCases.map((useCase, index) => (
                <li key={index}>{useCase}</li>
              ))}
            </ul>
          </div>

          <div className="next-steps">
            <h4>Next Steps</h4>
            <ol>
              <li>Site survey and network assessment</li>
              <li>Robot configuration and programming</li>
              <li>Staff training and handover</li>
              <li>Go-live and ongoing support</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="wizard-overlay">
      <div className="wizard-modal">
        <div className="wizard-header">
          <div className="wizard-title">
            <h1>Fleet Configuration Wizard</h1>
            <p>Configure your perfect robot fleet in 3 simple steps</p>
          </div>
          <button className="close-btn" onClick={onClose}>
            <X className="close-icon" />
          </button>
        </div>

        <div className="wizard-progress">
          <div className="progress-steps">
            <div className={`progress-step ${currentStep >= 1 ? 'active' : ''}`}>
              <div className="step-number">1</div>
              <span className="step-label">Industry</span>
            </div>
            <div className={`progress-step ${currentStep >= 2 ? 'active' : ''}`}>
              <div className="step-number">2</div>
              <span className="step-label">Customize</span>
            </div>
            <div className={`progress-step ${currentStep >= 3 ? 'active' : ''}`}>
              <div className="step-number">3</div>
              <span className="step-label">Review</span>
            </div>
          </div>
        </div>

        <div className="wizard-content">
          {currentStep === 1 && renderStep1()}
          {currentStep === 2 && renderStep2()}
          {currentStep === 3 && renderStep3()}
        </div>

        <div className="wizard-footer">
          <div className="footer-actions">
            {currentStep > 1 && (
              <button className="btn-secondary" onClick={() => setCurrentStep(currentStep - 1)}>
                <ArrowLeft className="btn-icon" />
                Previous
              </button>
            )}
            
            {currentStep === 1 && (
              <button className="btn-secondary" onClick={onClose}>
                Cancel
              </button>
            )}

            {currentStep === 2 && (
              <button className="btn-primary" onClick={handleCustomizationSubmit}>
                Continue to Review
                <ArrowRight className="btn-icon" />
              </button>
            )}

            {currentStep === 3 && (
              <button className="btn-primary" onClick={handleConfigurationSave}>
                <Check className="btn-icon" />
                Save Configuration
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
