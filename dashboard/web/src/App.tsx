import { useState, useEffect } from 'react'
import { Activity, Battery, CheckCircle, Clock } from 'lucide-react'
import './App.css'

function App() {
  const [fleetStatus, setFleetStatus] = useState(null)
  const [connecting, setConnecting] = useState(true)

  useEffect(() => {
    // Connect to the FastAPI WebSocket server
    const ws = new WebSocket('ws://localhost:8000/ws')

    ws.onopen = () => {
      setConnecting(false)
      console.log('Connected to Fleet Telemetry')
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        setFleetStatus(data)
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
  }, [])

  if (connecting || !fleetStatus) {
    return (
      <div className="loading-container">
        <Activity className="spinner" size={48} />
        <h2>Connecting to Fleet Simulator...</h2>
      </div>
    )
  }

  // Group active tasks by robot for easier display
  const tasksByRobot = {}
  fleetStatus.active_tasks.forEach(t => {
    tasksByRobot[t.robot_id] = t
  })

  // Normalize MuJoCo coordinates (-3 to 3) to SVG percentages (0% to 100%)
  // SVG origin is top-left. Our simulator warehouse is basically 6x6 meters.
  // x=-3 -> 0%, x=0 -> 50%, x=3 -> 100%
  // y=-3 -> 0%, y=0 -> 50%, y=3 -> 100%
  const toMapCoordX = (x) => `${((x + 3) / 6) * 100}%`
  const toMapCoordY = (y) => `${((y + 3) / 6) * 100}%`

  return (
    <div className="dashboard">
      <header className="header">
        <h1>Unitree R1 Fleet Dashboard</h1>
        <div className="status-badge live">
          <span className="dot"></span> LIVE TELEMETRY
        </div>
      </header>

      <div className="grid">
        {/* Left Column: Fleet Overview */}
        <div className="panel fleet-panel">
          <h2>Active Fleet</h2>
          <div className="robot-cards">
            {fleetStatus.robots.map(robot => {
              const task = tasksByRobot[robot.robot_id]
              return (
                <div key={robot.robot_id} className={`robot-card ${robot.fleet_status}`}>
                  <div className="card-header">
                    <h3>{robot.robot_id}</h3>
                    <span className={`status ${robot.fleet_status}`}>
                      {robot.fleet_status.toUpperCase()}
                    </span>
                  </div>
                  
                  <div className="metrics">
                    <div className="metric">
                      <Battery size={16} />
                      <span>{robot.battery}%</span>
                    </div>
                    {task && (
                      <div className="metric task">
                        <Clock size={16} />
                        <span>{task.task_id}</span>
                      </div>
                    )}
                  </div>
                  
                  <div className="pose-stats">
                    <small>X: {(robot.pose?.x || 0).toFixed(2)}</small>
                    <small>Y: {(robot.pose?.y || 0).toFixed(2)}</small>
                    <small>Heading: {(robot.pose?.theta || 0).toFixed(0)}°</small>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Center: Live Warehouse Map */}
        <div className="panel map-panel">
          <h2>Warehouse Layout</h2>
          <div className="map-container">
            {/* Dark grid background */}
            <div className="map-grid">
               {/* Fixed Shelves from our MuJoCo XML */}
               {/* Shelf 1: center x=-2.0, size=0.5x3 */}
               <div className="shelf" style={{ left: '12.5%', top: '25%', width: '8.3%', height: '50%' }}></div>
               {/* Shelf 2: center x=2.0, size=0.5x3 */}
               <div className="shelf" style={{ left: '79.1%', top: '25%', width: '8.3%', height: '50%' }}></div>
               
               {/* Real-time robot markers */}
               {fleetStatus.robots.map(robot => (
                 <div 
                   key={robot.robot_id}
                   className="robot-marker"
                   style={{
                     left: toMapCoordX(robot.pose.x),
                     top: toMapCoordY(robot.pose.y),
                     transform: `translate(-50%, -50%) rotate(${-(robot.pose.theta - 90)}deg)` // Note: DOM rot is clockwise, sim theta may differ
                   }}
                 >
                   <div className="robot-dot"></div>
                   <span className="robot-label">{robot.robot_id}</span>
                 </div>
               ))}
            </div>
          </div>
        </div>

        {/* Right Column: Task Log */}
        <div className="panel log-panel">
          <h2>Completion Log</h2>
          <div className="log-list">
            {fleetStatus.completed_tasks.length === 0 ? (
              <p className="empty-log">Awaiting completions...</p>
            ) : (
              fleetStatus.completed_tasks.map((task, i) => (
                <div key={i} className="log-entry">
                  <CheckCircle size={16} color="#10b981" />
                  <div className="log-content">
                    <strong>{task.robot_id}</strong> completed <em>{task.task_id}</em>
                    <br/>
                    <small>{task.result?.scanned_items?.length || 0} zones audited</small>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

      </div>
    </div>
  )
}

export default App
