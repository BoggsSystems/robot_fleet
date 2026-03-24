require('dotenv').config();
const EventProcessorAPI = require('./EventProcessorAPI');
const logger = require('./utils/logger');

async function main() {
  try {
    logger.info('Starting Event Processor Service');
    
    // Create and start the API
    const api = new EventProcessorAPI();
    await api.start();
    
    logger.info('Event Processor Service is running');
    
  } catch (error) {
    logger.error('Failed to start Event Processor Service', { 
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

// Start the application
if (require.main === module) {
  main();
}

module.exports = { main };
