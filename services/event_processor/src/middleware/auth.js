const jwt = require('jsonwebtoken');
const logger = require('../utils/logger');

const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN
  
  if (!token) {
    logger.warn('Access denied - no token provided', { 
      ip: req.ip,
      userAgent: req.get('User-Agent')
    });
    return res.status(401).json({ 
      error: 'Access token required',
      code: 'TOKEN_MISSING'
    });
  }
  
  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) {
      logger.warn('Access denied - invalid token', { 
        error: err.message,
        ip: req.ip,
        userAgent: req.get('User-Agent')
      });
      return res.status(403).json({ 
        error: 'Invalid or expired token',
        code: 'TOKEN_INVALID'
      });
    }
    
    req.user = user;
    next();
  });
};

const requirePermission = (permission) => {
  return (req, res, next) => {
    if (!req.user || !req.user.permissions) {
      logger.warn('Access denied - no user permissions', { 
        userId: req.user?.userId,
        permission 
      });
      return res.status(403).json({ 
        error: 'Insufficient permissions',
        code: 'PERMISSION_DENIED'
      });
    }
    
    if (!req.user.permissions.includes(permission)) {
      logger.warn('Access denied - permission not granted', { 
        userId: req.user.userId,
        userPermissions: req.user.permissions,
        requiredPermission: permission 
      });
      return res.status(403).json({ 
        error: 'Insufficient permissions',
        code: 'PERMISSION_DENIED',
        requiredPermission: permission
      });
    }
    
    next();
  };
};

const requireRole = (role) => {
  return (req, res, next) => {
    if (!req.user || !req.user.role) {
      logger.warn('Access denied - no user role', { 
        userId: req.user?.userId,
        role 
      });
      return res.status(403).json({ 
        error: 'Insufficient role privileges',
        code: 'ROLE_DENIED'
      });
    }
    
    if (req.user.role !== role) {
      logger.warn('Access denied - role not authorized', { 
        userId: req.user.userId,
        userRole: req.user.role,
        requiredRole: role 
      });
      return res.status(403).json({ 
        error: 'Insufficient role privileges',
        code: 'ROLE_DENIED',
        requiredRole: role
      });
    }
    
    next();
  };
};

const optionalAuth = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];
  
  if (!token) {
    // No token provided, continue without authentication
    req.user = null;
    return next();
  }
  
  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) {
      // Invalid token, continue without authentication
      req.user = null;
      return next();
    }
    
    req.user = user;
    next();
  });
};

const rateLimiter = (windowMs = 15 * 60 * 1000, max = 100) => {
  const requests = new Map();
  
  return (req, res, next) => {
    const key = req.ip;
    const now = Date.now();
    const windowStart = now - windowMs;
    
    // Clean old entries
    if (requests.has(key)) {
      const userRequests = requests.get(key).filter(time => time > windowStart);
      requests.set(key, userRequests);
    }
    
    // Check current requests
    const userRequests = requests.get(key) || [];
    
    if (userRequests.length >= max) {
      logger.warn('Rate limit exceeded', { 
        ip: req.ip,
        requests: userRequests.length,
        max,
        windowMs
      });
      return res.status(429).json({
        error: 'Too many requests',
        code: 'RATE_LIMIT_EXCEEDED'
      });
    }
    
    // Add current request
    userRequests.push(now);
    requests.set(key, userRequests);
    
    next();
  };
};

const authRateLimiter = rateLimiter(15 * 60 * 1000, 100); // 100 requests per 15 minutes for auth endpoints (development)

const validateRequest = (schema) => {
  return (req, res, next) => {
    const { error, value } = schema.validate(req.body);
    
    if (error) {
      logger.warn('Request validation failed', { 
        error: error.details[0].message,
        body: req.body 
      });
      return res.status(400).json({
        error: 'Invalid request data',
        code: 'VALIDATION_ERROR',
        details: error.details[0].message
      });
    }
    
    req.validatedBody = value;
    next();
  };
};

const errorHandler = (err, req, res, next) => {
  logger.error('Unhandled error', {
    error: err.message,
    stack: err.stack,
    method: req.method,
    url: req.url,
    userId: req.user?.userId
  });
  
  // Don't expose error details in production
  const isDevelopment = process.env.NODE_ENV !== 'production';
  
  res.status(500).json({
    error: 'Internal server error',
    code: 'INTERNAL_ERROR',
    ...(isDevelopment && { details: err.message, stack: err.stack })
  });
};

const requestLogger = (req, res, next) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    
    logger.info('API request completed', {
      method: req.method,
      url: req.url,
      statusCode: res.statusCode,
      duration: `${duration}ms`,
      ip: req.ip,
      userAgent: req.get('User-Agent'),
      userId: req.user?.userId
    });
  });
  
  next();
};

module.exports = {
  authenticateToken,
  requirePermission,
  requireRole,
  optionalAuth,
  rateLimiter,
  authRateLimiter,
  validateRequest,
  errorHandler,
  requestLogger
};
