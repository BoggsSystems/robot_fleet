require('dotenv').config();
const RobotSimulator = require('./RobotSimulator');
const logger = require('./utils/logger');

async function main() {
  try {
    logger.info('Starting Robot Fleet Simulator');
    
    // Create and start simulator
    const simulator = new RobotSimulator();
    
    // Setup graceful shutdown
    await simulator.shutdown();
    
    // Start the simulator
    await simulator.start();
    
    // Keep the process running
    logger.info('Robot Fleet Simulator is running. Press Ctrl+C to stop.');
    
  } catch (error) {
    logger.error('Failed to start Robot Fleet Simulator', { 
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
