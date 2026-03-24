const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

const app = express();
const port = process.env.PORT || 3001;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Demo data
const demoUsers = [
  {
    id: 'fleet_manager',
    username: 'fleet_manager',
    email: 'manager@robotfleet.com',
    password: 'FleetManager123!', // Plain text for demo
    role: 'fleet_manager',
    profile: {
      firstName: 'John',
      lastName: 'Doe',
      department: 'Operations'
    },
    permissions: [
      'robots.read', 'robots.write', 'robots.command',
      'alerts.read', 'alerts.write', 'alerts.acknowledge', 'alerts.resolve',
      'system.read', 'system.health', 'reports.read', 'reports.export'
    ]
  }
];

const demoRobots = {
  'robot-001': {
    robotId: 'robot-001',
    battery_level: 85,
    status: 'active',
    temperature: 45,
    position: { x: 10.5, y: 20.3, z: 0.0 },
    lastSeen: new Date().toISOString()
  },
  'robot-002': {
    robotId: 'robot-002',
    battery_level: 92,
    status: 'idle',
    temperature: 38,
    position: { x: 5.2, y: 15.8, z: 0.0 },
    lastSeen: new Date().toISOString()
  },
  'robot-003': {
    robotId: 'robot-003',
    battery_level: 15,
    status: 'maintenance',
    temperature: 52,
    position: { x: 25.1, y: 8.7, z: 0.0 },
    lastSeen: new Date().toISOString()
  },
  'robot-004': {
    robotId: 'robot-004',
    battery_level: 67,
    status: 'active',
    temperature: 41,
    position: { x: 18.3, y: 12.1, z: 0.0 },
    lastSeen: new Date().toISOString()
  },
  'robot-005': {
    robotId: 'robot-005',
    battery_level: 78,
    status: 'charging',
    temperature: 35,
    position: { x: 2.8, y: 3.4, z: 0.0 },
    lastSeen: new Date().toISOString()
  }
};

const demoAlerts = [
  {
    id: 'alert-001',
    robotId: 'robot-003',
    type: 'battery_low',
    severity: 'high',
    message: 'Battery level critically low',
    timestamp: new Date().toISOString(),
    acknowledged: false,
    resolved: false
  },
  {
    id: 'alert-002',
    robotId: 'robot-003',
    type: 'maintenance_required',
    severity: 'medium',
    message: 'Robot requires maintenance',
    timestamp: new Date().toISOString(),
    acknowledged: true,
    resolved: false
  },
  {
    id: 'alert-003',
    robotId: 'robot-005',
    type: 'charging_complete',
    severity: 'low',
    message: 'Robot charging completed',
    timestamp: new Date().toISOString(),
    acknowledged: false,
    resolved: false
  }
];

// JWT Secret
const JWT_SECRET = process.env.JWT_SECRET || 'demo-secret-key';

// Authentication middleware
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid or expired token' });
    }
    req.user = user;
    next();
  });
};

// Routes
app.post('/api/auth/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    
    const user = demoUsers.find(u => u.username === username);
    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Simple password check for demo
    const isValidPassword = user.password === password;
    if (!isValidPassword) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const accessToken = jwt.sign(
      { 
        userId: user.id, 
        username: user.username, 
        role: user.role,
        permissions: user.permissions 
      },
      JWT_SECRET,
      { expiresIn: '15m' }
    );

    const refreshToken = jwt.sign(
      { userId: user.id },
      JWT_SECRET,
      { expiresIn: '7d' }
    );

    res.json({
      success: true,
      user: {
        id: user.id,
        username: user.username,
        email: user.email,
        role: user.role,
        profile: user.profile,
        permissions: user.permissions
      },
      tokens: { accessToken, refreshToken }
    });
  } catch (error) {
    res.status(500).json({ error: 'Login failed' });
  }
});

app.get('/api/auth/me', authenticateToken, (req, res) => {
  res.json({
    success: true,
    user: {
      id: req.user.userId,
      username: req.user.username,
      role: req.user.role,
      permissions: req.user.permissions
    }
  });
});

app.post('/api/auth/logout', authenticateToken, (req, res) => {
  res.json({ success: true, message: 'Logged out successfully' });
});

app.post('/api/auth/refresh', (req, res) => {
  const { refreshToken } = req.body;
  
  try {
    const decoded = jwt.verify(refreshToken, JWT_SECRET);
    const user = demoUsers.find(u => u.id === decoded.userId);
    
    if (!user) {
      return res.status(401).json({ error: 'Invalid refresh token' });
    }

    const accessToken = jwt.sign(
      { 
        userId: user.id, 
        username: user.username, 
        role: user.role,
        permissions: user.permissions 
      },
      JWT_SECRET,
      { expiresIn: '15m' }
    );

    res.json({
      success: true,
      tokens: { accessToken, refreshToken }
    });
  } catch (error) {
    res.status(401).json({ error: 'Invalid refresh token' });
  }
});

// Protected API routes
app.get('/api/robots', authenticateToken, (req, res) => {
  res.json(demoRobots);
});

app.get('/api/robots/:robotId', authenticateToken, (req, res) => {
  const robot = demoRobots[req.params.robotId];
  if (!robot) {
    return res.status(404).json({ error: 'Robot not found' });
  }
  res.json(robot);
});

app.post('/api/robots/:robotId/commands', authenticateToken, (req, res) => {
  const { command, parameters } = req.body;
  const robot = demoRobots[req.params.robotId];
  
  if (!robot) {
    return res.status(404).json({ error: 'Robot not found' });
  }

  // Simulate command execution
  console.log(`Command sent to ${req.params.robotId}:`, { command, parameters });

  res.json({
    success: true,
    commandId: `cmd-${Date.now()}`,
    robotId: req.params.robotId,
    command: { command, parameters },
    timestamp: new Date().toISOString()
  });
});

app.get('/api/alerts', authenticateToken, (req, res) => {
  res.json(demoAlerts);
});

app.post('/api/alerts/:alertId/acknowledge', authenticateToken, (req, res) => {
  const alert = demoAlerts.find(a => a.id === req.params.alertId);
  if (!alert) {
    return res.status(404).json({ error: 'Alert not found' });
  }
  
  alert.acknowledged = true;
  res.json({ success: true, alertId: req.params.alertId, acknowledged: true });
});

app.post('/api/alerts/:alertId/resolve', authenticateToken, (req, res) => {
  const alertIndex = demoAlerts.findIndex(a => a.id === req.params.alertId);
  if (alertIndex === -1) {
    return res.status(404).json({ error: 'Alert not found' });
  }
  
  demoAlerts.splice(alertIndex, 1);
  res.json({ success: true, alertId: req.params.alertId, resolved: true });
});

app.get('/api/alerts/statistics', authenticateToken, (req, res) => {
  const stats = {
    total: demoAlerts.length,
    active: demoAlerts.filter(a => !a.resolved).length,
    acknowledged: demoAlerts.filter(a => a.acknowledged).length,
    resolved: 0,
    bySeverity: {
      low: demoAlerts.filter(a => a.severity === 'low').length,
      medium: demoAlerts.filter(a => a.severity === 'medium').length,
      high: demoAlerts.filter(a => a.severity === 'high').length,
      critical: demoAlerts.filter(a => a.severity === 'critical').length
    },
    byType: {}
  };

  demoAlerts.forEach(alert => {
    stats.byType[alert.type] = (stats.byType[alert.type] || 0) + 1;
  });

  res.json(stats);
});

app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: '1.0.0-demo'
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Not found',
    message: `Route ${req.method} ${req.originalUrl} not found`
  });
});

app.listen(port, () => {
  console.log(`🚀 Demo Event Processor API running on port ${port}`);
  console.log(`📊 Demo Fleet Dashboard available at http://localhost:3000`);
  console.log(`🔑 Default credentials: fleet_manager / FleetManager123!`);
  console.log(`🤖 Demo robots: ${Object.keys(demoRobots).length} robots available`);
  console.log(`⚠️  Demo alerts: ${demoAlerts.length} alerts available`);
});
