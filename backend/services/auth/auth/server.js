const express = require('express');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// In-memory user storage (in production, use a database)
const users = [];
const adminUsers = []; // Separate storage for admin users

// Admin roles and permissions
const ADMIN_ROLES = {
  superadmin: ['*'], // All permissions
  support: ['client:read', 'fleet:read', 'user:read', 'system:read'],
  billing: ['client:read', 'client:write', 'billing:read', 'billing:write'],
  technical: ['fleet:read', 'fleet:write', 'system:read', 'system:admin']
};

// Default superadmin user (create on startup)
const createDefaultSuperAdmin = async () => {
  const existingSuperAdmin = adminUsers.find(u => u.username === 'admin');
  if (!existingSuperAdmin) {
    const hashedPassword = await bcrypt.hash('admin123', 10);
    adminUsers.push({
      id: 1,
      username: 'admin',
      email: 'admin@robotfleet.com',
      password: hashedPassword,
      role: 'superadmin',
      permissions: ADMIN_ROLES.superadmin,
      profile: {
        firstName: 'Super',
        lastName: 'Admin',
        department: 'Management',
        phone: '+1-555-0100'
      },
      createdAt: new Date(),
      lastLogin: null
    });
    console.log('Default superadmin created: admin/admin123');
  }
};

// JWT Secret (in production, use environment variable)
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';
const ADMIN_JWT_SECRET = process.env.ADMIN_JWT_SECRET || 'admin-secret-key';

// Authentication middleware
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid token' });
    }
    req.user = user;
    next();
  });
};

// Admin authentication middleware
const authenticateAdminToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Admin access token required' });
  }

  jwt.verify(token, ADMIN_JWT_SECRET, (err, admin) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid admin token' });
    }
    req.admin = admin;
    next();
  });
};

// Check permission middleware
const requirePermission = (permission) => {
  return (req, res, next) => {
    if (!req.admin) {
      return res.status(401).json({ error: 'Admin authentication required' });
    }
    
    const hasPermission = req.admin.permissions.includes('*') || 
                         req.admin.permissions.includes(permission);
    
    if (!hasPermission) {
      return res.status(403).json({ error: 'Permission denied' });
    }
    
    next();
  };
};

// Routes
app.post('/auth/register', async (req, res) => {
  try {
    const { username, password, email } = req.body;

    // Check if user already exists
    const existingUser = users.find(u => u.username === username);
    if (existingUser) {
      return res.status(400).json({ error: 'Username already exists' });
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Create user
    const user = {
      id: users.length + 1,
      username,
      email,
      password: hashedPassword,
      createdAt: new Date()
    };

    users.push(user);

    // Generate JWT token
    const token = jwt.sign({ userId: user.id, username: user.username }, JWT_SECRET);

    res.status(201).json({
      message: 'User created successfully',
      token,
      user: { id: user.id, username: user.username, email: user.email }
    });
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
});

app.post('/auth/login', async (req, res) => {
  try {
    const { username, password } = req.body;

    // Find user
    const user = users.find(u => u.username === username);
    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Verify password
    const validPassword = await bcrypt.compare(password, user.password);
    if (!validPassword) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Generate JWT token
    const token = jwt.sign({ userId: user.id, username: user.username }, JWT_SECRET);

    res.json({
      message: 'Login successful',
      token,
      user: { id: user.id, username: user.username, email: user.email }
    });
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
});

app.get('/auth/profile', authenticateToken, (req, res) => {
  const user = users.find(u => u.id === req.user.userId);
  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }

  res.json({
    user: { id: user.id, username: user.username, email: user.email, createdAt: user.createdAt }
  });
});

app.post('/auth/logout', authenticateToken, (req, res) => {
  // In a real implementation, you might want to invalidate the token
  // For now, we'll just return a success message
  res.json({ message: 'Logout successful' });
});

// Admin Authentication Endpoints
app.post('/auth/admin/login', async (req, res) => {
  try {
    const { username, password } = req.body;

    // Find admin user
    const admin = adminUsers.find(u => u.username === username);
    if (!admin) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Verify password
    const validPassword = await bcrypt.compare(password, admin.password);
    if (!validPassword) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Update last login
    admin.lastLogin = new Date();

    // Generate admin JWT token
    const token = jwt.sign({ 
      adminId: admin.id, 
      username: admin.username,
      role: admin.role,
      permissions: admin.permissions
    }, ADMIN_JWT_SECRET, { expiresIn: '8h' });

    res.json({
      message: 'Admin login successful',
      token,
      admin: {
        id: admin.id,
        username: admin.username,
        email: admin.email,
        role: admin.role,
        permissions: admin.permissions,
        profile: admin.profile,
        lastLogin: admin.lastLogin
      }
    });
  } catch (error) {
    console.error('Admin login error:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

app.get('/auth/admin/profile', authenticateAdminToken, (req, res) => {
  const admin = adminUsers.find(u => u.id === req.admin.adminId);
  if (!admin) {
    return res.status(404).json({ error: 'Admin user not found' });
  }

  res.json({
    admin: {
      id: admin.id,
      username: admin.username,
      email: admin.email,
      role: admin.role,
      permissions: admin.permissions,
      profile: admin.profile,
      lastLogin: admin.lastLogin,
      createdAt: admin.createdAt
    }
  });
});

app.post('/auth/admin/logout', authenticateAdminToken, (req, res) => {
  res.json({ message: 'Admin logout successful' });
});

// Admin User Management (superadmin only)
app.post('/auth/admin/users', authenticateAdminToken, requirePermission('user:write'), async (req, res) => {
  try {
    const { username, password, email, role, profile } = req.body;

    // Validate role
    if (!ADMIN_ROLES[role]) {
      return res.status(400).json({ error: 'Invalid role' });
    }

    // Check if username already exists
    const existingAdmin = adminUsers.find(u => u.username === username);
    if (existingAdmin) {
      return res.status(400).json({ error: 'Username already exists' });
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Create admin user
    const newAdmin = {
      id: adminUsers.length + 1,
      username,
      email,
      password: hashedPassword,
      role,
      permissions: ADMIN_ROLES[role],
      profile: profile || {},
      createdAt: new Date(),
      lastLogin: null,
      createdBy: req.admin.adminId
    };

    adminUsers.push(newAdmin);

    res.status(201).json({
      message: 'Admin user created successfully',
      admin: {
        id: newAdmin.id,
        username: newAdmin.username,
        email: newAdmin.email,
        role: newAdmin.role,
        permissions: newAdmin.permissions,
        profile: newAdmin.profile
      }
    });
  } catch (error) {
    console.error('Create admin error:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

app.get('/auth/admin/users', authenticateAdminToken, requirePermission('user:read'), (req, res) => {
  const adminList = adminUsers.map(admin => ({
    id: admin.id,
    username: admin.username,
    email: admin.email,
    role: admin.role,
    profile: admin.profile,
    lastLogin: admin.lastLogin,
    createdAt: admin.createdAt
  }));

  res.json({ users: adminList });
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date() });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

// Start server
app.listen(PORT, async () => {
  console.log(`Auth server running on port ${PORT}`);
  await createDefaultSuperAdmin();
});

module.exports = { 
  app, 
  authenticateToken, 
  authenticateAdminToken, 
  requirePermission 
};
