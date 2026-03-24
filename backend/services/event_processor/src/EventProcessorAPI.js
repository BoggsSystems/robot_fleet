const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const logger = require('./utils/logger');
const IoTHubEventProcessor = require('./services/IoTHubEventProcessor');
const AuthService = require('./services/AuthService');
const UserSetupService = require('./services/UserSetupService');
const { authenticateToken, requirePermission, authRateLimiter, validateRequest, errorHandler, requestLogger } = require('./middleware/auth');
const { loginSchema, refreshTokenSchema, robotCommandSchema, alertAcknowledgeSchema, taskTwinSchema } = require('./middleware/validation');

class EventProcessorAPI {
  constructor() {
    this.app = express();
    this.port = process.env.PORT || 3001;
    this.eventProcessor = new IoTHubEventProcessor();
    this.authService = null;
    this.userSetupService = null;
    
    this.setupMiddleware();
    this.setupRoutes();
  }
  
  setupMiddleware() {
    // Security middleware
    this.app.use(helmet());
    
    // CORS middleware
    this.app.use(cors({
      origin: process.env.ALLOWED_ORIGINS || '*',
      methods: ['GET', 'POST', 'PUT', 'DELETE'],
      allowedHeaders: ['Content-Type', 'Authorization']
    }));
    
    // Body parsing middleware
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true }));
    
    // Request logging middleware
    this.app.use(requestLogger);
    
    // Error handling middleware
    this.app.use(errorHandler);
  }
  
  setupRoutes() {
    // Initialize auth services
    this.initializeAuthServices();
    
    // Authentication routes
    this.setupAuthRoutes();
    
    // Protected API routes
    this.setupProtectedRoutes();
    
    // Public routes (health check)
    this.setupPublicRoutes();
  }
  
  async initializeAuthServices() {
    try {
      this.authService = new AuthService(this.eventProcessor.cosmosDBService);
      this.userSetupService = new UserSetupService(this.eventProcessor.cosmosDBService);
      logger.info('Authentication services initialized');
    } catch (error) {
      logger.error('Failed to initialize authentication services', { error: error.message });
    }
  }
  
  setupAuthRoutes() {
    // Initialize user management system
    this.app.post('/api/auth/setup', async (req, res) => {
      try {
        const success = await this.userSetupService.setupComplete();
        res.json({ 
          success: success,
          message: success ? 'User management system initialized successfully' : 'Failed to initialize user management system'
        });
      } catch (error) {
        logger.error('Auth setup failed', { error: error.message });
        res.status(500).json({ error: 'Failed to setup authentication' });
      }
    });
    
    // Login endpoint
    this.app.post('/api/auth/login', authRateLimiter, validateRequest(loginSchema), async (req, res) => {
      try {
        const { username, password } = req.validatedBody;
        const deviceInfo = {
          userAgent: req.get('User-Agent'),
          ip: req.ip,
          platform: req.get('Sec-Ch-Ua-Platform') || 'unknown',
          browser: req.get('Sec-Ch-Ua') || 'unknown'
        };
        
        const result = await this.authService.login(username, password, deviceInfo);
        
        res.json({
          success: true,
          user: result.user,
          tokens: result.tokens
        });
      } catch (error) {
        logger.error('Login failed', { error: error.message });
        res.status(401).json({ error: error.message });
      }
    });
    
    // Refresh token endpoint
    this.app.post('/api/auth/refresh', validateRequest(refreshTokenSchema), async (req, res) => {
      try {
        const { refreshToken } = req.validatedBody;
        const tokens = await this.authService.refreshToken(refreshToken);
        
        res.json({
          success: true,
          tokens
        });
      } catch (error) {
        logger.error('Token refresh failed', { error: error.message });
        res.status(401).json({ error: error.message });
      }
    });
    
    // Logout endpoint
    this.app.post('/api/auth/logout', authenticateToken, validateRequest(refreshTokenSchema), async (req, res) => {
      try {
        const { refreshToken } = req.validatedBody;
        await this.authService.logout(refreshToken, req.user.userId);
        
        res.json({
          success: true,
          message: 'Logged out successfully'
        });
      } catch (error) {
        logger.error('Logout failed', { error: error.message });
        res.status(500).json({ error: 'Failed to logout' });
      }
    });
    
    // Get current user
    this.app.get('/api/auth/me', authenticateToken, (req, res) => {
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
  }
  
  setupProtectedRoutes() {
    // Robot management routes
    this.app.get('/api/robots', authenticateToken, requirePermission('robots.read'), (req, res) => {
      try {
        const status = this.eventProcessor.getAllRobotStatus();
        res.json(status);
      } catch (error) {
        logger.error('Error getting robot status', { error: error.message });
        res.status(500).json({ error: 'Failed to get robot status' });
      }
    });
    
    this.app.get('/api/robots/:robotId', authenticateToken, requirePermission('robots.read'), (req, res) => {
      try {
        const { robotId } = req.params;
        const status = this.eventProcessor.getRobotStatus(robotId);
        res.json(status);
      } catch (error) {
        logger.error('Error getting robot status', { error: error.message, robotId: req.params.robotId });
        res.status(500).json({ error: 'Failed to get robot status' });
      }
    });
    
    this.app.post('/api/robots/:robotId/commands', 
      authenticateToken, 
      requirePermission('robots.command'), 
      validateRequest(robotCommandSchema), 
      async (req, res) => {
        try {
          const { robotId } = req.params;
          const command = req.validatedBody;
          
          const result = await this.eventProcessor.sendCommandToRobot(robotId, command);
          
          if (result.success) {
            res.json({
              success: true,
              commandId: result.commandId,
              robotId,
              command,
              timestamp: new Date().toISOString()
            });
          } else {
            res.status(500).json({
              success: false,
              error: result.error,
              robotId,
              command
            });
          }
        } catch (error) {
          logger.error('Error sending command to robot', { 
            error: error.message,
            robotId: req.params.robotId 
          });
          res.status(500).json({ error: 'Failed to send command to robot' });
        }
      }
    );
    
    // Alert management routes
    this.app.get('/api/alerts', authenticateToken, requirePermission('alerts.read'), (req, res) => {
      try {
        const { robotId } = req.query;
        const alerts = this.eventProcessor.alertEngine.getActiveAlerts(robotId);
        res.json(alerts);
      } catch (error) {
        logger.error('Error getting alerts', { error: error.message });
        res.status(500).json({ error: 'Failed to get alerts' });
      }
    });
    
    this.app.post('/api/alerts/:alertId/acknowledge', 
      authenticateToken, 
      requirePermission('alerts.acknowledge'), 
      validateRequest(alertAcknowledgeSchema),
      (req, res) => {
        try {
          const { alertId } = req.params;
          const { acknowledged, notes } = req.validatedBody;
          
          if (acknowledged) {
            const success = this.eventProcessor.alertEngine.acknowledgeAlert(alertId);
            if (success) {
              res.json({ success: true, alertId, acknowledged: true, notes });
            } else {
              res.status(404).json({ error: 'Alert not found' });
            }
          } else {
            res.status(400).json({ error: 'Acknowledgment must be true' });
          }
        } catch (error) {
          logger.error('Error acknowledging alert', { error: error.message, alertId: req.params.alertId });
          res.status(500).json({ error: 'Failed to acknowledge alert' });
        }
      }
    );
    
    this.app.post('/api/alerts/:alertId/resolve', 
      authenticateToken, 
      requirePermission('alerts.resolve'),
      (req, res) => {
        try {
          const { alertId } = req.params;
          const success = this.eventProcessor.alertEngine.resolveAlert(alertId);
          
          if (success) {
            res.json({ success: true, alertId, resolved: true });
          } else {
            res.status(404).json({ error: 'Alert not found' });
          }
        } catch (error) {
          logger.error('Error resolving alert', { error: error.message, alertId: req.params.alertId });
          res.status(500).json({ error: 'Failed to resolve alert' });
        }
      }
    );
    
    this.app.get('/api/alerts/statistics', authenticateToken, requirePermission('alerts.read'), (req, res) => {
      try {
        const stats = this.eventProcessor.alertEngine.getAlertStatistics();
        res.json(stats);
      } catch (error) {
        logger.error('Error getting alert statistics', { error: error.message });
        res.status(500).json({ error: 'Failed to get alert statistics' });
      }
    });
    
    // Digital Twins routes
    this.app.get('/api/digitaltwins/robots', authenticateToken, requirePermission('robots.read'), async (req, res) => {
      try {
        const twins = await this.eventProcessor.digitalTwinsService.getAllRobotTwins();
        res.json(twins);
      } catch (error) {
        logger.error('Error getting robot twins', { error: error.message });
        res.status(500).json({ error: 'Failed to get robot twins' });
      }
    });
    
    this.app.get('/api/digitaltwins/zones', authenticateToken, requirePermission('robots.read'), async (req, res) => {
      try {
        const twins = await this.eventProcessor.digitalTwinsService.getZoneTwins();
        res.json(twins);
      } catch (error) {
        logger.error('Error getting zone twins', { error: error.message });
        res.status(500).json({ error: 'Failed to get zone twins' });
      }
    });
    
    this.app.get('/api/digitaltwins/zones/:zoneId/robots', authenticateToken, requirePermission('robots.read'), async (req, res) => {
      try {
        const { zoneId } = req.params;
        const robots = await this.eventProcessor.digitalTwinsService.getRobotsInZone(zoneId);
        res.json(robots);
      } catch (error) {
        logger.error('Error getting robots in zone', { 
          error: error.message,
          zoneId: req.params.zoneId 
        });
        res.status(500).json({ error: 'Failed to get robots in zone' });
      }
    });
    
    this.app.post('/api/digitaltwins/tasks', 
      authenticateToken, 
      requirePermission('robots.write'),
      validateRequest(taskTwinSchema),
      async (req, res) => {
        try {
          const { taskId, taskType, priority } = req.validatedBody;
          
          const success = await this.eventProcessor.digitalTwinsService.createTaskTwin(
            taskId, 
            taskType, 
            priority
          );
          
          if (success) {
            res.json({
              success: true,
              taskId,
              taskType,
              priority,
              timestamp: new Date().toISOString()
            });
          } else {
            res.status(500).json({ error: 'Failed to create task twin' });
          }
        } catch (error) {
          logger.error('Error creating task twin', { error: error.message });
          res.status(500).json({ error: 'Failed to create task twin' });
        }
      }
    );
    
    // System monitoring routes
    this.app.get('/api/stats', authenticateToken, requirePermission('system.read'), (req, res) => {
      try {
        const stats = this.eventProcessor.getProcessingStats();
        res.json(stats);
      } catch (error) {
        logger.error('Error getting stats', { error: error.message });
        res.status(500).json({ error: 'Failed to get statistics' });
      }
    });
  }
  
  setupPublicRoutes() {
    // Health check endpoint
    this.app.get('/health', (req, res) => {
      const stats = this.eventProcessor.getProcessingStats();
      
      res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        version: '1.0.0',
        processing: stats
      });
    });
    
    // 404 handler
    this.app.use('*', (req, res) => {
      res.status(404).json({
        error: 'Not found',
        message: `Route ${req.method} ${req.originalUrl} not found`
      });
    });
  }
  
  async start() {
    try {
      // Start the event processor
      await this.eventProcessor.start();
      
      // Start the API server
      this.app.listen(this.port, () => {
        logger.info(`Event Processor API started on port ${this.port}`);
      });
      
      // Setup graceful shutdown
      this.setupGracefulShutdown();
      
    } catch (error) {
      logger.error('Failed to start Event Processor API', { error: error.message });
      process.exit(1);
    }
  }
  
  async stop() {
    try {
      logger.info('Stopping Event Processor API');
      
      // Stop the event processor
      await this.eventProcessor.stop();
      
      logger.info('Event Processor API stopped');
    } catch (error) {
      logger.error('Error stopping Event Processor API', { error: error.message });
    }
  }
  
  setupGracefulShutdown() {
    const gracefulShutdown = async (signal) => {
      logger.info(`Received ${signal}, shutting down gracefully`);
      await this.stop();
      process.exit(0);
    };
    
    process.on('SIGINT', () => gracefulShutdown('SIGINT'));
    process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
  }
}

module.exports = EventProcessorAPI;
