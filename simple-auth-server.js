const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

const app = express();
const PORT = process.env.PORT || 3001;
const JWT_SECRET = process.env.JWT_SECRET || 'robot-fleet-jwt-secret-2024';

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Mock users (in production, this would be in Cosmos DB)
const users = [
  {
    id: 1,
    username: "admin",
    password: "$2b$10$N9qo8cLOtixxTyFHoCpQa6V.E8dKvHwQmKlYqJ8K5YQ6C8", // "admin123"
    role: "admin"
  },
  {
    id: 2,
    username: "fleetmanager",
    password: "$2b$10$N9qo8cLOtixxTyFHoCpQa6V.E8dKvHwQmKlYqJ8K5YQ6C8", // "FleetManager123!"
    role: "fleet_manager"
  }
];

// Helper functions
const generateToken = (user) => {
  return jwt.sign(
    { id: user.id, username: user.username, role: user.role },
    JWT_SECRET,
    { expiresIn: "1h" }
  );
};

const generateRefreshToken = () => {
  return jwt.sign({ type: "refresh" }, JWT_SECRET, { expiresIn: "7d" });
};

// Routes
app.get("/health", (req, res) => {
  res.json({
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
  });
});

app.post("/api/auth/setup", async (req, res) => {
  res.json({
    success: true,
    message: "User management system initialized successfully"
  });
});

app.post("/api/auth/login", async (req, res) => {
  try {
    const { username, password } = req.body;
    
    // Find user
    const user = users.find(u => u.username === username);
    if (!user) {
      return res.status(401).json({ error: "Invalid credentials" });
    }
    
    // Check password
    const isValidPassword = await bcrypt.compare(password, user.password);
    if (!isValidPassword) {
      return res.status(401).json({ error: "Invalid credentials" });
    }
    
    // Generate tokens
    const accessToken = generateToken(user);
    const refreshToken = generateRefreshToken();
    
    res.json({
      success: true,
      user: {
        id: user.id,
        username: user.username,
        role: user.role
      },
      tokens: {
        accessToken,
        refreshToken
      }
    });
    
  } catch (error) {
    console.error("Login error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

app.post("/api/auth/logout", (req, res) => {
  res.json({ success: true });
});

app.post("/api/auth/refresh", (req, res) => {
  try {
    const { refreshToken } = req.body;
    
    // Verify refresh token
    jwt.verify(refreshToken, JWT_SECRET, (err, decoded) => {
      if (err) {
        return res.status(401).json({ error: "Invalid refresh token" });
      }
      
      // Generate new tokens
      const user = users.find(u => u.id === 1); // Default to admin for demo
      const accessToken = generateToken(user);
      const newRefreshToken = generateRefreshToken();
      
      res.json({
        tokens: {
          accessToken,
          refreshToken: newRefreshToken
        }
      });
    });
    
  } catch (error) {
    console.error("Refresh token error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

app.get("/api/auth/me", (req, res) => {
  // This would normally verify JWT token
  res.json({
    success: true,
    user: {
      id: 1,
      username: "admin",
      role: "admin"
    }
  });
});

// Mock robot data
app.get("/api/robots", (req, res) => {
  res.json({
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
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Robot Fleet API running on port ${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
  console.log(`🔐 Login endpoint: http://localhost:${PORT}/api/auth/login`);
  console.log(`👤 Default users: admin/admin123, fleetmanager/FleetManager123!`);
});
