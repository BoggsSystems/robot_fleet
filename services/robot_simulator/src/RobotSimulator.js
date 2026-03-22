const Robot = require('./models/Robot');
const logger = require('./utils/logger');

class RobotSimulator {
  constructor() {
    this.robots = new Map();
    this.isRunning = false;
    this.telemetryInterval = null;
    this.simulationInterval = null;
    
    // Robot device configurations from Azure IoT Hub
    this.robotConfigs = [
      {
        id: 'robot-001',
        connectionString: "HostName=robot-fleet-hub.azure-devices.net;DeviceId=robot-001;SharedAccessKey=Ixy5Un+A7jku5hF+wRFvO78EghV5Qoaf8uzbTgAyRUs="
      },
      {
        id: 'robot-002',
        connectionString: "HostName=robot-fleet-hub.azure-devices.net;DeviceId=robot-002;SharedAccessKey=QwF/7QXRQr8sCkWt/iBb8ny+RqFfQsQqDMQ8psEhVOU="
      },
      {
        id: 'robot-003',
        connectionString: "HostName=robot-fleet-hub.azure-devices.net;DeviceId=robot-003;SharedAccessKey=ThfiVR4oteElr65sPIdBB63/Y0QvVB2oQBb+E60Asbs="
      },
      {
        id: 'robot-004',
        connectionString: "HostName=robot-fleet-hub.azure-devices.net;DeviceId=robot-004;SharedAccessKey=8sDKRVrLIlPx/WvhvVCa/2V5emIoghSZ/CXywWYMxuU="
      },
      {
        id: 'robot-005',
        connectionString: "HostName=robot-fleet-hub.azure-devices.net;DeviceId=robot-005;SharedAccessKey=wH7kcOiNsllSE8+i6xCclRM8GFs7e4P1FHVGiJYWzv4="
      }
    ];
  }
  
  async initialize() {
    logger.info('Initializing Robot Simulator');
    
    try {
      // Create robot instances
      for (const config of this.robotConfigs) {
        const robot = new Robot(config.id, config.connectionString);
        this.robots.set(config.id, robot);
        logger.info(`Robot ${config.id} created`, { robotId: config.id });
      }
      
      // Connect all robots to IoT Hub
      const connectPromises = Array.from(this.robots.values()).map(robot => robot.connect());
      await Promise.all(connectPromises);
      
      logger.info(`All ${this.robots.size} robots connected to IoT Hub`);
      
    } catch (error) {
      logger.error('Failed to initialize robot simulator', { error: error.message });
      throw error;
    }
  }
  
  async start() {
    if (this.isRunning) {
      logger.warn('Robot simulator is already running');
      return;
    }
    
    try {
      await this.initialize();
      
      this.isRunning = true;
      
      // Start telemetry transmission
      const telemetryIntervalMs = parseInt(process.env.TELEMETRY_INTERVAL_MS) || 3000;
      this.telemetryInterval = setInterval(() => {
        this.sendTelemetryFromAllRobots();
      }, telemetryIntervalMs);
      
      // Start simulation updates
      this.simulationInterval = setInterval(() => {
        this.updateSimulation();
      }, 100); // 10 Hz simulation rate
      
      logger.info('Robot Simulator started', {
        robotCount: this.robots.size,
        telemetryInterval: telemetryIntervalMs
      });
      
      // Send initial telemetry
      setTimeout(() => {
        this.sendTelemetryFromAllRobots();
      }, 1000);
      
    } catch (error) {
      logger.error('Failed to start robot simulator', { error: error.message });
      throw error;
    }
  }
  
  sendTelemetryFromAllRobots() {
    const telemetryPromises = Array.from(this.robots.values()).map(robot => {
      return robot.sendTelemetry().catch(error => {
        logger.error(`Failed to send telemetry from robot ${robot.robotId}`, {
          robotId: robot.robotId,
          error: error.message
        });
      });
    });
    
    Promise.allSettled(telemetryPromises);
  }
  
  updateSimulation() {
    for (const robot of this.robots.values()) {
      robot.updateSimulation();
    }
  }
  
  async stop() {
    if (!this.isRunning) {
      logger.warn('Robot simulator is not running');
      return;
    }
    
    logger.info('Stopping Robot Simulator');
    
    // Clear intervals
    if (this.telemetryInterval) {
      clearInterval(this.telemetryInterval);
      this.telemetryInterval = null;
    }
    
    if (this.simulationInterval) {
      clearInterval(this.simulationInterval);
      this.simulationInterval = null;
    }
    
    // Disconnect all robots
    const disconnectPromises = Array.from(this.robots.values()).map(robot => {
      return robot.disconnect().catch(error => {
        logger.error(`Failed to disconnect robot ${robot.robotId}`, {
          robotId: robot.robotId,
          error: error.message
        });
      });
    });
    
    await Promise.allSettled(disconnectPromises);
    
    this.isRunning = false;
    logger.info('Robot Simulator stopped');
  }
  
  getRobotStatus() {
    const status = {};
    for (const [robotId, robot] of this.robots) {
      status[robotId] = {
        connected: robot.isConnected,
        status: robot.state.status,
        battery_level: robot.state.battery_level,
        position: robot.state.position,
        temperature: robot.state.temperature,
        task_id: robot.state.task_id,
        errors: robot.state.errors
      };
    }
    return status;
  }
  
  async sendCommandToRobot(robotId, command) {
    const robot = this.robots.get(robotId);
    if (!robot) {
      logger.error(`Robot ${robotId} not found`, { robotId });
      return false;
    }
    
    try {
      robot.handleCloudCommand({ data: JSON.stringify(command) });
      logger.info(`Command sent to robot ${robotId}`, { robotId, command });
      return true;
    } catch (error) {
      logger.error(`Failed to send command to robot ${robotId}`, { 
        robotId, 
        command, 
        error: error.message 
      });
      return false;
    }
  }
  
  // Graceful shutdown
  async shutdown() {
    logger.info('Shutting down Robot Simulator');
    
    // Handle process signals
    process.on('SIGINT', async () => {
      logger.info('Received SIGINT, shutting down gracefully');
      await this.stop();
      process.exit(0);
    });
    
    process.on('SIGTERM', async () => {
      logger.info('Received SIGTERM, shutting down gracefully');
      await this.stop();
      process.exit(0);
    });
  }
}

module.exports = RobotSimulator;
