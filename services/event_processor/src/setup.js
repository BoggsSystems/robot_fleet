require('dotenv').config();
const UserSetupService = require('./services/UserSetupService');
const CosmosDBService = require('./services/CosmosDBService');
const logger = require('./utils/logger');

async function setup() {
  try {
    logger.info('🚀 Starting user management system setup...');
    
    // Initialize Cosmos DB service
    const cosmosDBService = new CosmosDBService();
    await cosmosDBService.connect();
    
    // Initialize user setup service
    const userSetupService = new UserSetupService(cosmosDBService);
    
    // Run complete setup
    const success = await userSetupService.setupComplete();
    
    if (success) {
      logger.info('✅ User management system setup completed successfully!');
      logger.info('');
      logger.info('📋 Setup Summary:');
      logger.info('   ✓ Cosmos DB connected');
      logger.info('   ✓ User containers created');
      logger.info('   ✓ Fleet manager user seeded');
      logger.info('');
      logger.info('🔑 Default Login Credentials:');
      logger.info('   Username: fleet_manager');
      logger.info('   Password: FleetManager123!');
      logger.info('');
      logger.info('🌐 Next Steps:');
      logger.info('   1. Start the event processor: npm start');
      logger.info('   2. Test authentication: POST /api/auth/login');
      logger.info('   3. Access protected endpoints with JWT token');
      logger.info('   4. Create React dashboard application');
      
      process.exit(0);
    } else {
      logger.error('❌ User management system setup failed');
      process.exit(1);
    }
  } catch (error) {
    logger.error('💥 Setup failed with error', { 
      error: error.message, 
      stack: error.stack 
    });
    process.exit(1);
  }
}

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  logger.error('Uncaught Exception', { 
    error: error.message, 
    stack: error.stack 
  });
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled Rejection', { 
    reason: reason.message || reason, 
    promise: promise.toString() 
  });
  process.exit(1);
});

// Start the setup
if (require.main === module) {
  setup();
}

module.exports = { setup };
