import { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, Building2, Users, CheckCircle, AlertCircle, ArrowRight, Calendar, Phone, Mail, MapPin, Settings, Bot, Package, TrendingUp, Wifi, Wand2, Eye } from 'lucide-react';
import { FleetConfigurationModern as FleetConfiguration, type FleetConfig } from './FleetConfigurationModern';
import { FleetConfigurationWizard } from './FleetConfigurationWizard';
import { FleetDetailView } from './FleetDetailView';
import './CustomerOnboardingAdmin.css';

export type Customer = {
  id: string;
  name: string;
  company: string;
  email: string;
  phone: string;
  address: string;
  requirements: string;
  fleet_requirements: string;
  status: 'prospect' | 'active' | 'inactive' | 'completed';
  sales_stage: 'initial_contact' | 'needs_assessment' | 'site_survey' | 'fleet_planning' | 'deployment';
  created_at: string;
  updated_at: string;
  fleet_config?: FleetConfig;
  robot_deployments?: RobotDeployment[];
  onboarding_tasks?: OnboardingTask[];
};

export type RobotDeployment = {
  id: string;
  customer_id: string;
  robot_id: string;
  deployment_type: 'delivery' | 'setup' | 'maintenance';
  robot_config: string;
  deployment_status: 'pending' | 'in_progress' | 'completed' | 'failed';
  deployment_location: string;
  deployed_at: string;
};

export type OnboardingTask = {
  id: string;
  customer_id: string;
  task_type: string;
  task_description: string;
  assigned_to: string;
  status: 'pending' | 'in_progress' | 'completed';
  due_date: string;
  completed_at?: string;
  created_at: string;
};

interface CustomerOnboardingAdminProps {
  onSelectCustomer?: (customer: Customer) => void;
  onCancel?: () => void;
}

const SALES_STAGES = [
  { value: 'initial_contact', label: 'Initial Contact', color: '#3B82F6' },
  { value: 'needs_assessment', label: 'Needs Assessment', color: '#8B5CF6' },
  { value: 'site_survey', label: 'Site Survey', color: '#F59E0B' },
  { value: 'fleet_planning', label: 'Fleet Planning', color: '#10B981' },
  { value: 'deployment', label: 'Deployment', color: '#EF4444' }
];

const STATUS_COLORS = {
  prospect: '#F59E0B',
  active: '#10B981',
  inactive: '#6B7280',
  completed: '#3B82F6'
};

const MOCK_CUSTOMERS: Customer[] = [
  {
    id: 'boggs_systems',
    name: 'Boggs Systems Corporation',
    company: 'Boggs Systems',
    email: 'contact@boggs.com',
    phone: '+1-555-ROBOTS',
    address: '123 Tech Street, Robot City, RC 12345',
    requirements: 'Cottage automation with advanced fleet management',
    fleet_requirements: '3-5 robots, mixed indoor/outdoor capabilities',
    status: 'prospect',
    sales_stage: 'initial_contact',
    created_at: '2024-01-15T00:00:00Z',
    updated_at: '2024-01-20T00:00:00Z'
  },
  {
    id: 'cottage_owner_001',
    name: 'Cottage Owner',
    company: 'Private Residence',
    email: 'owner@cottage.com',
    phone: '+1-555-COTTAGE',
    address: '456 Lakeview Drive, Cottage Town',
    requirements: 'Basic home automation with 1-2 robots',
    fleet_requirements: '1-2 robots, indoor focus',
    status: 'active',
    sales_stage: 'needs_assessment',
    created_at: '2024-02-01T00:00:00Z',
    updated_at: '2024-02-10T00:00:00Z'
  }
];

export function CustomerOnboardingAdmin({ onSelectCustomer, onCancel }: CustomerOnboardingAdminProps) {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [loading, setLoading] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'pipeline' | 'fleet' | 'tasks'>('overview');
  const [showFleetConfig, setShowFleetConfig] = useState(false);
  const [showFleetWizard, setShowFleetWizard] = useState(false);
  const [showFleetDetail, setShowFleetDetail] = useState(false);

  useEffect(() => {
    setCustomers(MOCK_CUSTOMERS);
  }, []);

  const handleAddCustomer = () => {
    setShowAddForm(true);
  };

  const handleEditCustomer = (customer: Customer) => {
    setEditingCustomer(customer);
    setSelectedCustomer(customer);
    setActiveTab('overview');
  };

  const handleDeleteCustomer = (customer: Customer) => {
    if (window.confirm(`Delete customer ${customer.name}?`)) {
      setCustomers(customers.filter(c => c.id !== customer.id));
      if (selectedCustomer?.id === customer.id) {
        setSelectedCustomer(null);
      }
    }
  };

  const handleSelectCustomer = (customer: Customer) => {
    setSelectedCustomer(customer);
    setActiveTab('overview');
    onSelectCustomer?.(customer);
  };

  const handleUpdateSalesStage = (customerId: string, newStage: string) => {
    setCustomers(customers.map(c => 
      c.id === customerId 
        ? { ...c, sales_stage: newStage as Customer['sales_stage'], updated_at: new Date().toISOString() }
        : c
    ));
  };

  const handleSaveFleetConfig = (fleetConfig: FleetConfig) => {
    if (selectedCustomer) {
      const updatedCustomer = {
        ...selectedCustomer,
        fleet_config: fleetConfig,
        updated_at: new Date().toISOString()
      };
      
      setCustomers(customers.map(c => c.id === selectedCustomer.id ? updatedCustomer : c));
      setSelectedCustomer(updatedCustomer);
      setShowFleetConfig(false);
    }
  };

  const handleConfigureFleet = () => {
    setShowFleetConfig(true);
  };

  const handleConfigureFleetWizard = () => {
    setShowFleetWizard(true);
  };

  const handleViewFleet = () => {
    setShowFleetDetail(true);
  };

  const getStatusColor = (status: Customer['status']) => STATUS_COLORS[status];
  const getStageColor = (stage: Customer['sales_stage']) => 
    SALES_STAGES.find(s => s.value === stage)?.color || '#6B7280';

  return (
    <div className="customer-onboarding-admin">
      <div className="admin-header">
        <div className="header-content">
          <div className="header-title">
            <Building2 className="title-icon" />
            <h1>Customer Onboarding Admin</h1>
          </div>
          <div className="header-actions">
            <button onClick={handleAddCustomer} className="btn-primary">
              <Plus className="btn-icon" />
              Add Customer
            </button>
            {onCancel && (
              <button onClick={onCancel} className="btn-secondary">
                Cancel
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="admin-content">
        <div className="customers-list">
          <div className="list-header">
            <h2>Customers ({customers.length})</h2>
            <div className="list-stats">
              <div className="stat">
                <TrendingUp className="stat-icon" />
                <span>{customers.filter(c => c.status === 'prospect').length} Prospects</span>
              </div>
              <div className="stat">
                <Users className="stat-icon" />
                <span>{customers.filter(c => c.status === 'active').length} Active</span>
              </div>
            </div>
          </div>

          <div className="customers-grid">
            {customers.map(customer => (
              <div 
                key={customer.id} 
                className={`customer-card ${selectedCustomer?.id === customer.id ? 'selected' : ''}`}
                onClick={() => handleSelectCustomer(customer)}
              >
                <div className="card-header">
                  <div className="customer-info">
                    <h3>{customer.name}</h3>
                    <p>{customer.company}</p>
                  </div>
                  <div className="customer-status">
                    <span 
                      className="status-badge" 
                      style={{ backgroundColor: getStatusColor(customer.status) }}
                    >
                      {customer.status}
                    </span>
                  </div>
                </div>

                <div className="card-content">
                  <div className="contact-info">
                    <div className="contact-item">
                      <Mail className="contact-icon" />
                      <span>{customer.email}</span>
                    </div>
                    <div className="contact-item">
                      <Phone className="contact-icon" />
                      <span>{customer.phone}</span>
                    </div>
                    <div className="contact-item">
                      <MapPin className="contact-icon" />
                      <span>{customer.address}</span>
                    </div>
                  </div>

                  <div className="requirements">
                    <div className="requirement">
                      <strong>Needs:</strong> {customer.requirements}
                    </div>
                    <div className="requirement">
                      <strong>Fleet:</strong> {customer.fleet_requirements}
                    </div>
                  </div>

                  <div className="sales-stage">
                    <div className="stage-indicator">
                      <span className="stage-label">Sales Stage:</span>
                      <span 
                        className="stage-badge"
                        style={{ backgroundColor: getStageColor(customer.sales_stage) }}
                      >
                        {SALES_STAGES.find(s => s.value === customer.sales_stage)?.label}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="card-actions">
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      handleEditCustomer(customer);
                    }}
                    className="btn-edit"
                  >
                    <Edit2 className="btn-icon" />
                    Edit
                  </button>
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteCustomer(customer);
                    }}
                    className="btn-delete"
                  >
                    <Trash2 className="btn-icon" />
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {selectedCustomer && (
          <div className="customer-detail">
            <div className="detail-header">
              <h2>{selectedCustomer.name}</h2>
              <div className="detail-tabs">
                <button 
                  className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
                  onClick={() => setActiveTab('overview')}
                >
                  Overview
                </button>
                <button 
                  className={`tab ${activeTab === 'pipeline' ? 'active' : ''}`}
                  onClick={() => setActiveTab('pipeline')}
                >
                  Sales Pipeline
                </button>
                <button 
                  className={`tab ${activeTab === 'fleet' ? 'active' : ''}`}
                  onClick={() => setActiveTab('fleet')}
                >
                  Fleet Config
                </button>
                <button 
                  className={`tab ${activeTab === 'tasks' ? 'active' : ''}`}
                  onClick={() => setActiveTab('tasks')}
                >
                  Tasks
                </button>
              </div>
            </div>

            <div className="detail-content">
              {activeTab === 'overview' && (
                <div className="overview-tab">
                  <div className="info-grid">
                    <div className="info-group">
                      <h3>Customer Information</h3>
                      <div className="info-item">
                        <label>Company:</label>
                        <span>{selectedCustomer.company}</span>
                      </div>
                      <div className="info-item">
                        <label>Email:</label>
                        <span>{selectedCustomer.email}</span>
                      </div>
                      <div className="info-item">
                        <label>Phone:</label>
                        <span>{selectedCustomer.phone}</span>
                      </div>
                      <div className="info-item">
                        <label>Address:</label>
                        <span>{selectedCustomer.address}</span>
                      </div>
                    </div>

                    <div className="info-group">
                      <h3>Requirements</h3>
                      <div className="info-item">
                        <label>Needs:</label>
                        <span>{selectedCustomer.requirements}</span>
                      </div>
                      <div className="info-item">
                        <label>Fleet Requirements:</label>
                        <span>{selectedCustomer.fleet_requirements}</span>
                      </div>
                    </div>

                    <div className="info-group">
                      <h3>Status</h3>
                      <div className="info-item">
                        <label>Customer Status:</label>
                        <span 
                          className="status-badge"
                          style={{ backgroundColor: getStatusColor(selectedCustomer.status) }}
                        >
                          {selectedCustomer.status}
                        </span>
                      </div>
                      <div className="info-item">
                        <label>Sales Stage:</label>
                        <span 
                          className="status-badge"
                          style={{ backgroundColor: getStageColor(selectedCustomer.sales_stage) }}
                        >
                          {SALES_STAGES.find(s => s.value === selectedCustomer.sales_stage)?.label}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'pipeline' && (
                <div className="pipeline-tab">
                  <div className="pipeline-stages">
                    {SALES_STAGES.map((stage, index) => (
                      <div 
                        key={stage.value}
                        className={`pipeline-stage ${selectedCustomer.sales_stage === stage.value ? 'active' : ''}`}
                      >
                        <div 
                          className="stage-dot"
                          style={{ backgroundColor: stage.color }}
                        />
                        <div className="stage-content">
                          <h4>{stage.label}</h4>
                          <p>Stage {index + 1} of {SALES_STAGES.length}</p>
                        </div>
                        {selectedCustomer.sales_stage === stage.value && (
                          <div className="stage-actions">
                            <button className="btn-complete">
                              <CheckCircle className="btn-icon" />
                              Complete Stage
                            </button>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'fleet' && (
                <div className="fleet-tab">
                  {selectedCustomer.fleet_config ? (
                    <div className="fleet-overview">
                      <div className="fleet-summary">
                        <h3>{selectedCustomer.fleet_config.configuration_name}</h3>
                        <div className="fleet-stats">
                          <div className="stat-item">
                            <Bot className="stat-icon" />
                            <span>{selectedCustomer.fleet_config.configuration_data.robot_count} Robots</span>
                          </div>
                          <div className="stat-item">
                            <Package className="stat-icon" />
                            <span>{selectedCustomer.fleet_config.configuration_data.environment_type}</span>
                          </div>
                          <div className="stat-item">
                            <Wifi className="stat-icon" />
                            <span>{selectedCustomer.fleet_config.configuration_data.network_config.ssid || 'Network Configured'}</span>
                          </div>
                        </div>
                      </div>
                      <div className="fleet-actions">
                        <button onClick={handleViewFleet} className="btn-primary">
                          <Eye className="btn-icon" />
                          View Fleet Details
                        </button>
                        <button onClick={handleConfigureFleet} className="btn-secondary">
                          <Settings className="btn-icon" />
                          Edit Configuration
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="fleet-config">
                      <h3>Fleet Configuration</h3>
                      <div className="config-placeholder">
                        <Package className="placeholder-icon" />
                        <p>No fleet configuration yet</p>
                        <div className="config-buttons">
                          <button onClick={handleConfigureFleetWizard} className="btn-primary">
                            <Wand2 className="btn-icon" />
                            Quick Configuration
                          </button>
                          <button onClick={handleConfigureFleet} className="btn-secondary">
                            <Settings className="btn-icon" />
                            Advanced Configuration
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'tasks' && (
                <div className="tasks-tab">
                  <div className="tasks-list">
                    <h3>Onboarding Tasks</h3>
                    <div className="tasks-placeholder">
                      <CheckCircle className="placeholder-icon" />
                      <p>No tasks assigned yet</p>
                      <button className="btn-primary">
                        <Plus className="btn-icon" />
                        Add Task
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {showFleetConfig && selectedCustomer && (
        <FleetConfiguration
          customer={selectedCustomer}
          onSaveConfiguration={handleSaveFleetConfig}
          onCancel={() => setShowFleetConfig(false)}
        />
      )}

      {showFleetWizard && selectedCustomer && (
        <FleetConfigurationWizard
          isOpen={showFleetWizard}
          onClose={() => setShowFleetWizard(false)}
          customer={selectedCustomer}
          onSaveConfiguration={handleSaveFleetConfig}
        />
      )}

      {showFleetDetail && selectedCustomer && (
        <FleetDetailView
          customer={selectedCustomer}
          fleetConfig={selectedCustomer.fleet_config}
          onEditRobot={(robotId) => console.log('Edit robot:', robotId)}
          onRemoveRobot={(robotId) => console.log('Remove robot:', robotId)}
        />
      )}
    </div>
  );
}
