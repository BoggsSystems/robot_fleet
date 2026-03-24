const logger = require('../utils/logger');
const CosmosDBService = require('./CosmosDBService');

class UserSetupService {
  constructor(cosmosDBService) {
    this.cosmosDBService = cosmosDBService;
  }
  
  async initializeUserContainers() {
    try {
      logger.info('Initializing user management containers...');
      
      const success = await this.cosmosDBService.ensureUserContainers();
      
      if (success) {
        logger.info('User management containers initialized successfully');
        return true;
      } else {
        logger.error('Failed to initialize user management containers');
        return false;
      }
    } catch (error) {
      logger.error('Error initializing user containers', { error: error.message });
      return false;
    }
  }
  
  async seedFleetManager() {
    try {
      logger.info('Seeding fleet manager user...');
      
      const fleetManagerData = {
        username: "fleet_manager",
        email: "manager@robotfleet.com",
        password: "FleetManager123!",
        role: "fleet_manager",
        profile: {
          firstName: "John",
          lastName: "Doe",
          department: "Operations",
          phone: "+1-555-0123",
          timezone: "America/New_York"
        }
      };
      
      try {
        const user = await this.cosmosDBService.createUser(fleetManagerData);
        logger.info('Fleet manager user seeded successfully', { 
          userId: user.id,
          username: user.username,
          role: user.role 
        });
        
        // Log audit event for user creation
        await this.cosmosDBService.logAuditEvent({
          userId: user.id,
          action: 'user_created',
          resource: 'user_management',
          details: {
            username: user.username,
            role: user.role,
            createdBy: 'system'
          },
          severity: 'info',
          category: 'administration'
        });
        
        return true;
      } catch (error) {
        if (error.message.includes('already exists')) {
          logger.info('Fleet manager user already exists');
          return true;
        }
        throw error;
      }
    } catch (error) {
      logger.error('Failed to seed fleet manager', { error: error.message });
      return false;
    }
  }
  
  async setupComplete() {
    try {
      logger.info('Starting complete user management setup...');
      
      // Step 1: Initialize containers
      const containersReady = await this.initializeUserContainers();
      if (!containersReady) {
        throw new Error('Failed to initialize containers');
      }
      
      // Step 2: Seed fleet manager
      const userSeeded = await this.seedFleetManager();
      if (!userSeeded) {
        throw new Error('Failed to seed fleet manager');
      }
      
      logger.info('✅ User management system setup complete!');
      logger.info('📝 Default credentials: fleet_manager / FleetManager123!');
      
      return true;
    } catch (error) {
      logger.error('❌ User management setup failed', { error: error.message });
      return false;
    }
  }
  
  async verifySetup() {
    try {
      logger.info('Verifying user management setup...');
      
      // Check if fleet manager exists
      const fleetManager = await this.cosmosDBService.findUserByUsername('fleet_manager');
      
      if (fleetManager) {
        logger.info('✅ Fleet manager user verified', { 
          userId: fleetManager.id,
          role: fleetManager.role,
          permissions: fleetManager.permissions.length 
        });
        return true;
      } else {
        logger.error('❌ Fleet manager user not found');
        return false;
      }
    } catch (error) {
      logger.error('Error verifying setup', { error: error.message });
      return false;
    }
  }
}

module.exports = UserSetupService;
