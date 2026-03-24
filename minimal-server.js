const http = require('http');
const url = require('url');

const PORT = process.env.PORT || 3001;
const JWT_SECRET = process.env.JWT_SECRET || 'robot-fleet-jwt-secret-2024';

// Mock users
const users = [
  {
    id: 1,
    username: "admin",
    password: "admin123",
    role: "admin"
  }
];

// Simple HTTP server
const server = http.createServer((req, res) => {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  const parsedUrl = url.parse(req.url, true);
  const path = parsedUrl.pathname;

  // Health check endpoint
  if (path === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      status: "healthy",
      timestamp: new Date().toISOString(),
      service: "robot-fleet-api",
      version: "1.0.0",
      processing: {
        totalMessages: 0,
        successfulProcessing: 0,
        failedProcessing: 0,
        alertsGenerated: 0,
        lastProcessed: null,
        isRunning: true,
        batchSize: 10,
        batchTimeout: 5000
      }
    }));
    return;
  }

  // Login endpoint
  if (path === '/api/auth/login' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => {
      body += chunk.toString();
    });
    req.on('end', () => {
      try {
        const { username, password } = JSON.parse(body);
        const user = users.find(u => u.username === username && u.password === password);
        
        if (user) {
          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({
            success: true,
            user: {
              id: user.id,
              username: user.username,
              role: user.role
            },
            tokens: {
              accessToken: "mock-access-token-" + Date.now(),
              refreshToken: "mock-refresh-token-" + Date.now()
            }
          }));
        } else {
          res.writeHead(401, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: "Invalid credentials" }));
        }
      } catch (error) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: "Internal server error" }));
      }
    });
    return;
  }

  // Logout endpoint
  if (path === '/api/auth/logout' && req.method === 'POST') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ success: true }));
    return;
  }

  // Auth me endpoint
  if (path === '/api/auth/me' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      success: true,
      user: {
        id: 1,
        username: "admin",
        role: "admin"
      }
    }));
    return;
  }

  // Robots endpoint
  if (path === '/api/robots' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      success: true,
      robots: [
        {
          id: "robot-001",
          name: "Robot 1",
          status: "active",
          battery: 85,
          location: { x: 10, y: 20 },
          lastSeen: new Date().toISOString()
        },
        {
          id: "robot-002",
          name: "Robot 2",
          status: "idle",
          battery: 92,
          location: { x: 15, y: 25 },
          lastSeen: new Date().toISOString()
        }
      ]
    }));
    return;
  }

  // 404 for other routes
  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: "Not found" }));
});

server.listen(PORT, () => {
  console.log(`🚀 Robot Fleet API running on port ${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
  console.log(`🔐 Login endpoint: http://localhost:${PORT}/api/auth/login`);
  console.log(`👤 Default user: admin / admin123`);
});
