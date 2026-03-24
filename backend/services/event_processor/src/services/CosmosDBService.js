const { CosmosClient } = require('@azure/cosmos');
const bcrypt = require('bcryptjs');
const logger = require('../utils/logger');
const TelemetryValidator = require('../utils/TelemetryValidator');

class CosmosDBService {
  constructor() {
    this.client = null;
    this.database = null;
    this.telemetryContainer = null;
    this.usersContainer = null;
    this.sessionsContainer = null;
    this.auditLogsContainer = null;
    this.isConnected = false;
  }
  
  async connect() {
    try {
      const endpoint = process.env.COSMOS_DB_ENDPOINT;
      const key = process.env.COSMOS_DB_KEY;
      const databaseName = process.env.COSMOS_DB_DATABASE;
      const telemetryContainerName = process.env.COSMOS_DB_CONTAINER;
      
      this.client = new CosmosClient({ endpoint, key });
      this.database = this.client.database(databaseName);
      this.telemetryContainer = this.database.container(telemetryContainerName);
      
      // Test connection
      await this.telemetryContainer.read();
      this.isConnected = true;
      
      logger.info('Connected to Cosmos DB', { 
        database: databaseName, 
        telemetryContainer: telemetryContainerName 
      });
      
    } catch (error) {
      logger.error('Failed to connect to Cosmos DB', { error: error.message });
      throw error;
    }
  }
  
  async storeTelemetry(telemetry) {
    if (!this.isConnected) {
      logger.error('Cosmos DB not connected');
      return false;
    }
    
    try {
      // Validate telemetry
      const validation = TelemetryValidator.validate(telemetry);
      if (!validation.valid) {
        logger.error('Invalid telemetry data', { error: validation.error });
        return false;
      }
      
      // Sanitize telemetry
      const sanitized = TelemetryValidator.sanitizeTelemetry(validation.data);
      
      // Create document with partition key and metadata
      const document = {
        id: `${sanitized.robotId}-${Date.now()}`,
        robotId: sanitized.robotId,
        timestamp: sanitized.timestamp,
        type: 'telemetry',
        data: sanitized,
        processedAt: new Date().toISOString(),
        partitionKey: sanitized.robotId
      };
      
      // Store in Cosmos DB
      const { resource } = await this.telemetryContainer.items.create(document);
      
      logger.debug('Telemetry stored in Cosmos DB', { 
        robotId: sanitized.robotId,
        timestamp: sanitized.timestamp,
        documentId: resource.id 
      });
      
      return true;
      
    } catch (error) {
      logger.error('Failed to store telemetry in Cosmos DB', { 
        error: error.message,
        telemetry 
      });
      return false;
    }
  }
  
  async storeBatchTelemetry(telemetryBatch) {
    if (!this.isConnected || telemetryBatch.length === 0) {
      return false;
    }
    
    try {
      const documents = telemetryBatch.map(telemetry => {
        const validation = TelemetryValidator.validate(telemetry);
        if (!validation.valid) {
          logger.warn('Skipping invalid telemetry in batch', { 
            error: validation.error,
            robotId: telemetry.robotId 
          });
          return null;
        }
        
        const sanitized = TelemetryValidator.sanitizeTelemetry(validation.data);
        
        return {
          id: `${sanitized.robotId}-${Date.now()}-${Math.random()}`,
          robotId: sanitized.robotId,
          timestamp: sanitized.timestamp,
          type: 'telemetry',
          data: sanitized,
          processedAt: new Date().toISOString(),
          partitionKey: sanitized.robotId
        };
      }).filter(doc => doc !== null);
      
      if (documents.length === 0) {
        logger.warn('No valid telemetry in batch to store');
        return false;
      }
      
      // Batch operations
      const operations = documents.map(doc => ({
        type: 'Create',
        resource: doc
      }));
      
      // Execute batch (simplified approach - create individually)
      const results = await Promise.allSettled(
        documents.map(doc => this.telemetryContainer.items.create(doc))
      );
      
      const successful = results.filter(r => r.status === 'fulfilled').length;
      const failed = results.filter(r => r.status === 'rejected').length;
      
      logger.info('Batch telemetry stored in Cosmos DB', { 
        total: documents.length,
        successful,
        failed 
      });
      
      return successful > 0;
      
    } catch (error) {
      logger.error('Failed to store batch telemetry in Cosmos DB', { 
        error: error.message,
        batchSize: telemetryBatch.length 
      });
      return false;
    }
  }
  
  async getLatestTelemetry(robotId, limit = 10) {
    if (!this.isConnected) {
      logger.error('Cosmos DB not connected');
      return [];
    }
    
    try {
      const querySpec = {
        query: 'SELECT TOP @limit * FROM c WHERE c.robotId = @robotId AND c.type = "telemetry" ORDER BY c.timestamp DESC',
        parameters: [
          { name: '@robotId', value: robotId },
          { name: '@limit', value: limit }
        ]
      };
      
      const { resources } = await this.telemetryContainer.items.query(querySpec).fetchAll();
      
      logger.debug('Retrieved latest telemetry', { 
        robotId, 
        count: resources.length 
      });
      
      return resources;
      
    } catch (error) {
      logger.error('Failed to get latest telemetry', { 
        error: error.message,
        robotId 
      });
      return [];
    }
  }
  
  async getTelemetryByTimeRange(robotId, startTime, endTime) {
    if (!this.isConnected) {
      logger.error('Cosmos DB not connected');
      return [];
    }
    
    try {
      const querySpec = {
        query: 'SELECT * FROM c WHERE c.robotId = @robotId AND c.type = "telemetry" AND c.timestamp >= @startTime AND c.timestamp <= @endTime ORDER BY c.timestamp DESC',
        parameters: [
          { name: '@robotId', value: robotId },
          { name: '@startTime', value: startTime },
          { name: '@endTime', value: endTime }
        ]
      };
      
      const { resources } = await this.telemetryContainer.items.query(querySpec).fetchAll();
      
      logger.debug('Retrieved telemetry by time range', { 
        robotId, 
        startTime,
        endTime,
        count: resources.length 
      });
      
      return resources;
      
    } catch (error) {
      logger.error('Failed to get telemetry by time range', { 
        error: error.message,
        robotId,
        startTime,
        endTime 
      });
      return [];
    }
  }
  
  async getAllRobotStatus() {
    if (!this.isConnected) {
      logger.error('Cosmos DB not connected');
      return {};
    }
    
    try {
      const querySpec = {
        query: 'SELECT c.robotId, c.data.battery_level, c.data.status, c.data.position, c.data.temperature, c.timestamp FROM c WHERE c.type = "telemetry" ORDER BY c.timestamp DESC'
      };
      
      const { resources } = await this.telemetryContainer.items.query(querySpec).fetchAll();
      
      // Get latest status for each robot
      const robotStatus = {};
      for (const doc of resources) {
        if (!robotStatus[doc.robotId]) {
          robotStatus[doc.robotId] = {
            robotId: doc.robotId,
            battery_level: doc.data.battery_level,
            status: doc.data.status,
            position: doc.data.position,
            temperature: doc.data.temperature,
            lastSeen: doc.timestamp
          };
        }
      }
      
      logger.debug('Retrieved all robot status', { 
        robotCount: Object.keys(robotStatus).length 
      });
      
      return robotStatus;
      
    } catch (error) {
      logger.error('Failed to get all robot status', { error: error.message });
      return {};
    }
  }
  
  async disconnect() {
    try {
      if (this.client) {
        // Cosmos DB client doesn't have explicit disconnect
        this.isConnected = false;
        logger.info('Disconnected from Cosmos DB');
      }
    } catch (error) {
      logger.error('Error disconnecting from Cosmos DB', { error: error.message });
    }
  }
  
  // ==================== USER MANAGEMENT METHODS ====================
  
  async createUser(userData) {
    if (!this.isConnected) {
      logger.error('Cosmos DB not connected');
      return null;
    }
    
    try {
      // Hash password
      const hashedPassword = await bcrypt.hash(userData.password, 12);
      
      const user = {
        id: userData.username,
        username: userData.username,
        email: userData.email,
        password: hashedPassword,
        role: userData.role || 'fleet_manager',
        profile: userData.profile || {
          firstName: '',
          lastName: '',
          department: 'Operations',
          phone: '',
          timezone: 'America/New_York',
          preferences: {
            theme: 'dark',
            notifications: true,
            autoRefresh: 30,
            language: 'en'
          }
        },
        permissions: this.getPermissionsForRole(userData.role || 'fleet_manager'),
        security: {
          lastLogin: null,
          loginAttempts: 0,
          lockedUntil: null,
          isActive: true
        },
        metadata: {
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          createdBy: 'system',
          isActive: true
        },
        partitionKey: userData.username
      };
      
      const { resource } = await this.usersContainer.items.create(user);
      
      logger.info('User created successfully', { 
        userId: user.id,
        role: user.role 
      });
      
      return resource;
      
    } catch (error) {
      logger.error('Failed to create user', { 
        error: error.message,
        username: userData.username 
      });
      throw error;
    }
  }
  
  async findUserByUsername(username) {
    if (!this.isConnected) {
      logger.error('Cosmos DB not connected');
      return null;
    }
    
    try {
      const querySpec = {
        query: 'SELECT * FROM c WHERE c.username = @username AND c.security.isActive = true',
        parameters: [{ name: '@username', value: username }]
      };
      
      const { resources } = await this.usersContainer.items.query(querySpec).fetchAll();
      return resources[0] || null;
      
    } catch (error) {
      logger.error('Failed to find user by username', { 
        error: error.message,
        username 
      });
      return null;
    }
  }
  
  async findUserById(userId) {
    if (!this.isConnected) {
      logger.error('Cosmos DB not connected');
      return null;
    }
    
    try {
      const { resource } = await this.usersContainer.item(userId, userId).read();
      return resource;
    } catch (error) {
      logger.error('Failed to find user by ID', { 
        error: error.message,
        userId 
      });
      return null;
    }
  }
  
  async createSession(sessionData) {
    if (!this.isConnected) {
      logger.error('Cosmos DB not connected');
      return null;
    }
    
    try {
      const session = {
        id: sessionData.sessionId,
        userId: sessionData.userId,
        refreshToken: sessionData.refreshToken,
        deviceInfo: sessionData.deviceInfo || {
          userAgent: '',
          ip: '',
          platform: '',
          browser: '',
          version: ''
        },
        sessionData: {
          loginTime: new Date().toISOString(),
          lastActivity: new Date().toISOString(),
          expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 days
          isActive: true
        },
        security: {
          ipAddress: sessionData.ipAddress || '',
          riskScore: 0.1,
          suspiciousActivity: false
        },
        partitionKey: sessionData.userId
      };
      
      const { resource } = await this.sessionsContainer.items.create(session);
      
      logger.info('Session created successfully', { 
        sessionId: session.id,
        userId: session.userId 
      });
      
      return resource;
      
    } catch (error) {
      logger.error('Failed to create session', { 
        error: error.message,
        userId: sessionData.userId 
      });
      throw error;
    }
  }
  
  async findSession(refreshToken) {
    if (!this.isConnected) {
      logger.error('Cosmos DB not connected');
      return null;
    }
    
    try {
      const querySpec = {
        query: 'SELECT * FROM c WHERE c.refreshToken = @token AND c.sessionData.isActive = true',
        parameters: [{ name: '@token', value: refreshToken }]
      };
      
      const { resources } = await this.sessionsContainer.items.query(querySpec).fetchAll();
      return resources[0] || null;
      
    } catch (error) {
      logger.error('Failed to find session', { 
        error: error.message 
      });
      return null;
    }
  }
  
  async updateSession(sessionId, updates) {
    if (!this.isConnected) {
      logger.error('Cosmos DB not connected');
      return false;
    }
    
    try {
      const session = await this.sessionsContainer.item(sessionId, sessionId).read();
      if (!session.resource) {
        return false;
      }
      
      const updatedSession = { ...session.resource, ...updates };
      await this.sessionsContainer.item(sessionId, sessionId).replace(updatedSession);
      
      logger.info('Session updated successfully', { sessionId });
      return true;
      
    } catch (error) {
      logger.error('Failed to update session', { 
        error: error.message,
        sessionId 
      });
      return false;
    }
  }
  
  async logAuditEvent(eventData) {
    if (!this.isConnected) {
      logger.error('Cosmos DB not connected');
      return false;
    }
    
    try {
      const auditEvent = {
        id: `${eventData.userId}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        userId: eventData.userId,
        action: eventData.action,
        resource: eventData.resource,
        details: eventData.details || {},
        metadata: {
          timestamp: new Date().toISOString(),
          severity: eventData.severity || 'info',
          category: eventData.category || 'authentication'
        },
        partitionKey: eventData.userId
      };
      
      await this.auditLogsContainer.items.create(auditEvent);
      
      logger.debug('Audit event logged', { 
        userId: eventData.userId,
        action: eventData.action 
      });
      
      return true;
      
    } catch (error) {
      logger.error('Failed to log audit event', { 
        error: error.message,
        userId: eventData.userId 
      });
      return false;
    }
  }
  
  async updateUserLastLogin(userId) {
    if (!this.isConnected) {
      logger.error('Cosmos DB not connected');
      return false;
    }
    
    try {
      const user = await this.findUserById(userId);
      if (!user) {
        return false;
      }
      
      user.security.lastLogin = new Date().toISOString();
      user.security.loginAttempts = 0;
      user.metadata.updatedAt = new Date().toISOString();
      
      await this.usersContainer.item(userId, userId).replace(user);
      
      logger.info('User last login updated', { userId });
      return true;
      
    } catch (error) {
      logger.error('Failed to update user last login', { 
        error: error.message,
        userId 
      });
      return false;
    }
  }
  
  async handleFailedLogin(username) {
    if (!this.isConnected) {
      logger.error('Cosmos DB not connected');
      return false;
    }
    
    try {
      const user = await this.findUserByUsername(username);
      if (!user) {
        return false;
      }
      
      user.security.loginAttempts += 1;
      
      // Lock account after 5 failed attempts
      if (user.security.loginAttempts >= 5) {
        user.security.lockedUntil = new Date(Date.now() + 15 * 60 * 1000).toISOString(); // 15 minutes
        logger.warn('Account locked due to failed login attempts', { 
          username, 
          attempts: user.security.loginAttempts 
        });
      }
      
      user.metadata.updatedAt = new Date().toISOString();
      await this.usersContainer.item(username, username).replace(user);
      
      return true;
      
    } catch (error) {
      logger.error('Failed to handle failed login', { 
        error: error.message,
        username 
      });
      return false;
    }
  }
  
  getPermissionsForRole(role) {
    const permissions = {
      fleet_manager: [
        'robots.read',
        'robots.write', 
        'robots.command',
        'alerts.read',
        'alerts.write',
        'alerts.acknowledge',
        'alerts.resolve',
        'system.read',
        'system.health',
        'reports.read',
        'reports.export'
      ],
      technical_engineer: [
        'robots.read',
        'robots.write',
        'alerts.read',
        'alerts.write',
        'system.read',
        'system.health',
        'reports.read'
      ],
      warehouse_manager: [
        'robots.read',
        'robots.command',
        'alerts.read',
        'alerts.acknowledge',
        'reports.read'
      ]
    };
    
    return permissions[role] || permissions.fleet_manager;
  }
  
  // ==================== USER CONTAINER MANAGEMENT ====================
  
  async ensureUserContainers() {
    if (!this.isConnected) {
      logger.error('Cosmos DB not connected');
      return false;
    }
    
    try {
      // Create users container
      try {
        await this.database.containers.create({
          id: 'users',
          partitionKey: { paths: ['/username'] }
        });
        logger.info('Users container created');
      } catch (error) {
        if (error.code !== 409) { // 409 = Conflict (container already exists)
          throw error;
        }
        logger.info('Users container already exists');
      }
      
      // Create sessions container
      try {
        await this.database.containers.create({
          id: 'sessions',
          partitionKey: { paths: ['/userId'] }
        });
        logger.info('Sessions container created');
      } catch (error) {
        if (error.code !== 409) {
          throw error;
        }
        logger.info('Sessions container already exists');
      }
      
      // Create audit-logs container
      try {
        await this.database.containers.create({
          id: 'audit-logs',
          partitionKey: { paths: ['/userId'] }
        });
        logger.info('Audit logs container created');
      } catch (error) {
        if (error.code !== 409) {
          throw error;
        }
        logger.info('Audit logs container already exists');
      }
      
      // Set container references
      this.usersContainer = this.database.container('users');
      this.sessionsContainer = this.database.container('sessions');
      this.auditLogsContainer = this.database.container('audit-logs');
      
      return true;
      
    } catch (error) {
      logger.error('Failed to ensure user containers', { error: error.message });
      return false;
    }
  }
}

module.exports = CosmosDBService;
