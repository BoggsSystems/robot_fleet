import { useState, useEffect } from 'react'
import { Activity, Battery, Plus, LogOut, User, Settings, Package, Activity as ActivityIcon, Sparkles } from 'lucide-react'
import { LoginScreen } from './components/auth/LoginScreen'
import { OnboardingWizard } from './components/onboarding/OnboardingWizard'
import { FleetManager } from './components/fleet/FleetManager'
import { ClientManager } from './components/clients/ClientManager'
import { ProvisioningDashboard } from './components/provisioning/ProvisioningDashboard'
import { OperationsCenter } from './components/operations/OperationsCenter'
import { SalesFunnel } from './components/sales/SalesFunnel'
import { LeadManager } from './components/leads/LeadManager'
import type { RobotConfig, Fleet } from './components/onboarding/OnboardingWizard'
import './App.css'

interface User {
  email: string
  name: string
  role: string
}

interface FleetStatus {
  robots: Array<{
    robot_id: string;
    fleet_status: string;
    battery: number;
    pose: { x: number; y: number; theta: number };
    robot_type?: string;
    robot_category?: string;
    vendor?: string;
    zone?: string;
  }>;
  active_tasks: Array<{
    robot_id: string;
    task_id: string;
  }>;
  completed_tasks: Array<{
    robot_id: string;
    task_id: string;
    result?: { scanned_items?: string[] };
  }>;
}

function App() {
  // Auth state
  const [user, setUser] = useState<User | null>(null)
  
  // Fleet state
  const [fleetStatus, setFleetStatus] = useState<FleetStatus | null>(null)
  const [connecting, setConnecting] = useState(true)
  const [showOnboarding, setShowOnboarding] = useState(false)
  const [showFleetManager, setShowFleetManager] = useState(false)
  const [showClientManager, setShowClientManager] = useState(false)
  const [showProvisioning, setShowProvisioning] = useState(false)
  const [showOperationsCenter, setShowOperationsCenter] = useState(false)
  const [showSalesFunnel, setShowSalesFunnel] = useState(false)
  const [showLeadManager, setShowLeadManager] = useState(false)
  const [selectedFleet, setSelectedFleet] = useState<Fleet | null>(null)
  const [existingRobots, setExistingRobots] = useState<string[]>([])

  // Check for stored session on mount
  useEffect(() => {
    const storedUser = localStorage.getItem('fleet_user')
    if (storedUser) {
      setUser(JSON.parse(storedUser))
    }
  }, [])

  // Connect to WebSocket when logged in
  useEffect(() => {
    if (!user) return

    const ws = new WebSocket('ws://localhost:8000/ws')

    ws.onopen = () => {
      setConnecting(false)
      console.log('Connected to Fleet Telemetry')
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        setFleetStatus(data)
        if (data.robots) {
          setExistingRobots(data.robots.map((r: any) => r.robot_id))
        }
      } catch (e) {
        console.error('Failed to parse telemetry', e)
      }
    }

    ws.onclose = () => {
      setConnecting(true)
    }

    return () => {
      ws.close()
    }
  }, [user])

  const handleLogin = (userData: User) => {
    setUser(userData)
    localStorage.setItem('fleet_user', JSON.stringify(userData))
  }

  const handleLogout = () => {
    setUser(null)
    localStorage.removeItem('fleet_user')
    setFleetStatus(null)
  }

  const handleOnboardingComplete = async (config: RobotConfig) => {
    // Register the new robot
    try {
      const response = await fetch('/api/robots/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      })
      
      if (response.ok) {
        setExistingRobots(prev => [...prev, config.robotId])
        setShowOnboarding(false)
      } else {
        console.error('Failed to register robot')
      }
    } catch (err) {
      console.error('Error registering robot:', err)
    }
  }

  const handleOnboardingCancel = () => {
    setShowOnboarding(false)
  }

  // Show Lead Manager
  if (showLeadManager) {
    return (
      <LeadManager 
        onLeadSelect={(lead) => {
          console.log('Lead selected:', lead)
          // Could navigate to lead details or open modal
        }}
        onConvertToClient={(lead) => {
          console.log('Lead converted to client:', lead)
          // Could add to client database
        }}
      />
    )
  }

  // Show Sales Funnel
  if (showSalesFunnel) {
    return (
      <SalesFunnel 
        onComplete={(lead) => {
          console.log('Lead completed:', lead)
          setShowSalesFunnel(false)
        }}
      />
    )
  }

  // Show Client Manager
  if (showClientManager) {
    return (
      <div className="dashboard">
        <header className="header">
          <div className="header-left">
            <h1>Robot Fleet Dashboard</h1>
          </div>
          <div className="header-right">
            <button className="btn-secondary" onClick={() => setShowClientManager(false)}>
              Back to Dashboard
            </button>
          </div>
        </header>
        <ClientManager onCancel={() => setShowClientManager(false)} />
      </div>
    )
  }

  // Show Provisioning Dashboard
  if (showProvisioning) {
    return (
      <div className="dashboard">
        <header className="header">
          <div className="header-left">
            <h1>Robot Fleet Dashboard</h1>
          </div>
          <div className="header-right">
            <button className="btn-secondary" onClick={() => setShowProvisioning(false)}>
              Back to Dashboard
            </button>
          </div>
        </header>
        <ProvisioningDashboard onCancel={() => setShowProvisioning(false)} />
      </div>
    )
  }

  // Show Operations Center
  if (showOperationsCenter) {
    return (
      <div className="dashboard">
        <header className="header">
          <div className="header-left">
            <h1>Robot Fleet Dashboard</h1>
          </div>
          <div className="header-right">
            <button className="btn-secondary" onClick={() => setShowOperationsCenter(false)}>
              Back to Dashboard
            </button>
          </div>
        </header>
        <OperationsCenter onCancel={() => setShowOperationsCenter(false)} />
      </div>
    )
  }

  // Show fleet manager
  if (showFleetManager) {
    return (
      <div className="dashboard">
        <header className="header">
          <div className="header-left">
            <h1>Robot Fleet Dashboard</h1>
          </div>
          <div className="header-right">
            <button className="btn-secondary" onClick={() => setShowFleetManager(false)}>
              Back to Dashboard
            </button>
          </div>
        </header>
        <FleetManager onCancel={() => setShowFleetManager(false)} />
      </div>
    )
  }

  // Show login screen if not authenticated
  if (!user) {
    return <LoginScreen onLogin={handleLogin} />
  }

  // Show onboarding wizard when triggered
  if (showOnboarding) {
    return (
      <OnboardingWizard
        onComplete={handleOnboardingComplete}
        onCancel={handleOnboardingCancel}
        existingRobots={existingRobots}
      />
    )
  }

  // Loading state
  if (connecting || !fleetStatus) {
    return (
      <div className="loading-container">
        <Activity className="spinner" size={48} />
        <h2>Connecting to Fleet Telemetry...</h2>
      </div>
    )
  }

  // Coordinate conversion (kept for future use)
  const toMapCoordX = (x: number) => `${((x + 3) / 6) * 100}%`
  const toMapCoordY = (y: number) => `${((y + 3) / 6) * 100}%`

  // Tasks by robot (kept for future use)
  const tasksByRobot: Record<string, {robot_id: string; task_id: string}> = {}
  fleetStatus.active_tasks.forEach(t => {
    tasksByRobot[t.robot_id] = t
  })

  return (
    <div className="dashboard">
      <header className="header">
        <div className="header-left">
          <h1>Robot Fleet Dashboard</h1>
          <div className="status-badge live">
            <span className="dot"></span> LIVE
          </div>
        </div>
        <div className="header-right">
          <div className="admin-menu">
            <button className="btn-admin" onClick={() => setShowLeadManager(true)}>
              <User size={16} />
              Leads
            </button>
            <button className="btn-admin" onClick={() => setShowSalesFunnel(true)}>
              <Sparkles size={16} />
              Sales Funnel
            </button>
            <button className="btn-admin" onClick={() => setShowClientManager(true)}>
              <User size={16} />
              Clients
            </button>
            <button className="btn-admin" onClick={() => setShowFleetManager(true)}>
              <Settings size={16} />
              Fleets
            </button>
            <button className="btn-admin" onClick={() => setShowProvisioning(true)}>
              <Package size={16} />
              Inventory
            </button>
            <button className="btn-admin" onClick={() => setShowOperationsCenter(true)}>
              <ActivityIcon size={16} />
              Operations
            </button>
          </div>
          <div className="user-info">
            <User size={16} />
            <span>{user.name}</span>
          </div>
          <button className="add-robot-btn" onClick={() => setShowOnboarding(true)}>
            <Plus size={16} />
            Add Robot
          </button>
          <button className="logout-btn" onClick={handleLogout}>
            <LogOut size={16} />
            Logout
          </button>
        </div>
      </header>

      <div className="dashboard-content">
        {fleetStatus.robots.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🤖</div>
            <h2>No Robots in Fleet</h2>
            <p>Get started by adding your first robot to the system.</p>
            <button className="btn-add-first" onClick={() => setShowOnboarding(true)}>
              <Plus size={24} />
              Add Your First Robot
            </button>
          </div>
        ) : (
          <div className="robot-table-container">
            <div className="table-header">
              <h2>Fleet Overview</h2>
              <span className="count">{fleetStatus.robots.length} robots registered</span>
            </div>
            <table className="robot-table">
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Robot ID</th>
                  <th>Category</th>
                  <th>Vendor</th>
                  <th>Status</th>
                  <th>Battery</th>
                  <th>Zone</th>
                </tr>
              </thead>
              <tbody>
                {fleetStatus.robots.map(robot => {
                  const typeIcon = robot.robot_category === 'Humanoid' ? '🤖' :
                                  robot.robot_category === 'Quadruped' ? '🐕' :
                                  robot.robot_category === 'Wheeled' ? '🔄' : '⚙️'
                  return (
                    <tr key={robot.robot_id}>
                      <td className="type-cell">
                        <span className="type-icon">{typeIcon}</span>
                      </td>
                      <td className="id-cell">{robot.robot_id}</td>
                      <td>
                        <span className="category-badge">{robot.robot_type || robot.robot_category}</span>
                      </td>
                      <td>
                        <span className="vendor-badge">{robot.vendor}</span>
                      </td>
                      <td>
                        <span className={`status-badge-table ${robot.fleet_status}`}>
                          {robot.fleet_status}
                        </span>
                      </td>
                      <td>
                        <div className="battery-cell">
                          <Battery size={14} />
                          <span>{robot.battery}%</span>
                        </div>
                      </td>
                      <td>{robot.zone || '—'}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
