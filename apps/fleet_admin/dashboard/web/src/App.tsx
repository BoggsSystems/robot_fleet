import { useState } from 'react'
import { useAuth } from './auth/AuthProvider'
import { CustomerOnboardingAdmin } from './components/CustomerOnboardingAdmin'
import { FleetDetailView } from './components/FleetDetailView'
import { FleetConfigurationWizard } from './components/FleetConfigurationWizard'
import { FleetConfigurationModern as FleetConfiguration } from './components/FleetConfigurationModern'
import type { FleetConfig } from './components/FleetConfigurationModern'
import './App.css'

type Customer = {
  id: string;
  name: string;
  company: string;
  email: string;
  phone: string;
  address: string;
  requirements: string;
  industry: string;
  status: 'active' | 'inactive' | 'trial';
  sales_stage: 'lead' | 'qualified' | 'proposal' | 'negotiation' | 'closed_won' | 'closed_lost';
  fleet_config?: FleetConfig;
  created_at: string;
  last_updated: string;
};

function App() {
  const { user, logout } = useAuth()
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null)
  const [currentView, setCurrentView] = useState<'dashboard' | 'customers' | 'fleet-detail'>('dashboard')
  const [showFleetConfig, setShowFleetConfig] = useState(false)
  const [showFleetWizard, setShowFleetWizard] = useState(false)
  const [showFleetDetail, setShowFleetDetail] = useState(false)

  // Mock customer data
  const customers: Customer[] = [
    {
      id: 'customer_1',
      name: 'John Smith',
      company: 'Boggs Systems',
      email: 'john@boggssystems.com',
      phone: '+1 (555) 123-4567',
      address: '123 Tech Street, San Francisco, CA 94105',
      requirements: 'Complete warehouse automation solution with 24/7 monitoring and maintenance capabilities',
      industry: 'warehouse',
      status: 'active',
      sales_stage: 'closed_won',
      fleet_config: {
        id: 'fleet_001',
        customer_id: 'customer_1',
        configuration_name: 'BoggsSystems_Warehouse_Fleet',
        industry: 'warehouse',
        configuration_data: {
          environment_type: 'mixed',
          robot_count: 7,
          robot_types: [
            {
              id: 'robot_a1_001',
              model: 'Unitree A1',
              type: 'delivery',
              count: 4,
              capabilities: ['package_delivery', 'navigation', 'climbing', 'dynamic_balance'],
              specifications: {
                weight_capacity: '5 kg',
                battery_life: '8 hours',
                speed: '6 km/h',
                navigation: 'LiDAR + Visual SLAM'
              }
            },
            {
              id: 'robot_go1_001',
              model: 'Unitree Go1',
              type: 'security',
              count: 2,
              capabilities: ['surveillance', 'patrol', 'human_detection', 'night_vision'],
              specifications: {
                weight_capacity: '3 kg',
                battery_life: '10 hours',
                speed: '4.5 km/h',
                navigation: 'Visual SLAM + GPS'
              }
            },
            {
              id: 'robot_z1_001',
              model: 'Unitree Z1',
              type: 'maintenance',
              count: 1,
              capabilities: ['diagnostics', 'repair_assistance', 'tool_carrying', 'preventive_maintenance'],
              specifications: {
                weight_capacity: '10 kg',
                battery_life: '16 hours',
                speed: '2 km/h',
                navigation: 'LiDAR + Visual SLAM'
              }
            }
          ],
          network_config: {
            ssid: 'BoggsSystems_Guest',
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
            monday: { start: '06:00', end: '22:00', active: true },
            tuesday: { start: '06:00', end: '22:00', active: true },
            wednesday: { start: '06:00', end: '22:00', active: true },
            thursday: { start: '06:00', end: '22:00', active: true },
            friday: { start: '06:00', end: '22:00', active: true },
            saturday: { start: '08:00', end: '18:00', active: false },
            sunday: { start: '08:00', end: '18:00', active: false }
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
        created_at: '2024-03-15T10:00:00Z',
        updated_at: '2024-03-20T15:30:00Z'
      },
      created_at: '2024-03-15T10:00:00Z',
      last_updated: '2024-03-20T15:30:00Z'
    }
  ];

  const handleSelectCustomer = (customer: Customer) => {
    setSelectedCustomer(customer)
    setCurrentView('dashboard')
  }

  const handleSaveFleetConfig = (config: FleetConfig) => {
    console.log('Saving fleet configuration:', config)
    setShowFleetConfig(false)
    setShowFleetWizard(false)
  }

  const handleViewFleet = () => {
    setShowFleetDetail(true)
  }

  if (!user) {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <h1>🤖 Fleet Admin Portal</h1>
          <p>Please log in to access fleet management</p>
          <button onClick={() => console.log('Login')}>
            Login
          </button>
        </div>
      </div>
    )
  }

  return (
    <main className="fleet-admin-app">
      <header className="admin-header">
        <div className="header-content">
          <div className="header-title">
            <h1>🤖 Fleet Management System</h1>
            <p>Robot Fleet Administration & Customer Management</p>
          </div>
          <div className="header-user">
            <span>Welcome, {user.name}</span>
            <button onClick={logout} className="logout-btn">
              Logout
            </button>
          </div>
        </div>
      </header>

      <nav className="admin-nav">
        <button 
          className={`nav-btn ${currentView === 'dashboard' ? 'active' : ''}`}
          onClick={() => setCurrentView('dashboard')}
        >
          Dashboard
        </button>
        <button 
          className={`nav-btn ${currentView === 'customers' ? 'active' : ''}`}
          onClick={() => setCurrentView('customers')}
        >
          Customers
        </button>
        {selectedCustomer && (
          <button 
            className={`nav-btn ${currentView === 'fleet-detail' ? 'active' : ''}`}
            onClick={() => setCurrentView('fleet-detail')}
          >
            Fleet Detail
          </button>
        )}
      </nav>

      <div className="admin-content">
        {currentView === 'dashboard' && (
          <div className="dashboard-view">
            <div className="dashboard-overview">
              <div className="overview-cards">
                <div className="stat-card">
                  <h3>Total Customers</h3>
                  <span className="stat-value">{customers.length}</span>
                </div>
                <div className="stat-card">
                  <h3>Active Fleets</h3>
                  <span className="stat-value">{customers.filter(c => c.fleet_config).length}</span>
                </div>
                <div className="stat-card">
                  <h3>Total Robots</h3>
                  <span className="stat-value">
                    {customers.reduce((sum, c) => sum + (c.fleet_config?.configuration_data.robot_count || 0), 0)}
                  </span>
                </div>
              </div>
              
              <div className="recent-customers">
                <h3>Recent Customers</h3>
                {customers.map(customer => (
                  <div 
                    key={customer.id} 
                    className="customer-card"
                    onClick={() => handleSelectCustomer(customer)}
                  >
                    <div className="customer-info">
                      <h4>{customer.company}</h4>
                      <p>{customer.name}</p>
                      <span className={`status ${customer.status}`}>{customer.status}</span>
                    </div>
                    <div className="customer-meta">
                      <span>{customer.industry}</span>
                      <span>{new Date(customer.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {currentView === 'customers' && (
          <CustomerOnboardingAdmin 
            onSelectCustomer={handleSelectCustomer}
            onCancel={() => setCurrentView('dashboard')}
          />
        )}

        {currentView === 'fleet-detail' && selectedCustomer && (
          <FleetDetailView
            customer={selectedCustomer}
            fleetConfig={selectedCustomer.fleet_config}
            onEditRobot={(robotId) => console.log('Edit robot:', robotId)}
            onRemoveRobot={(robotId) => console.log('Remove robot:', robotId)}
          />
        )}

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
      </div>
    </main>
  )
}

export default App
