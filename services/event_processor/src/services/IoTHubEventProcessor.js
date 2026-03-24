const { EventHubConsumerClient } = require('@azure/event-hubs');
const logger = require('../utils/logger');
const CosmosDBService = require('./CosmosDBService');
const DigitalTwinsService = require('./DigitalTwinsService');
const AlertEngine = require('./AlertEngine');

class IoTHubEventProcessor {
  constructor() {
    this.consumerClient = null;
    this.isRunning = false;
    this.batchSize = parseInt(process.env.TELEMETRY_BATCH_SIZE) || 10;
    this.batchTimeout = parseInt(process.env.TELEMETRY_BATCH_TIMEOUT_MS) || 5000;
    
    // Services
    this.cosmosDBService = new CosmosDBService();
    this.digitalTwinsService = new DigitalTwinsService();
    this.alertEngine = new AlertEngine();
    
    // Batching
    this.telemetryBatch = [];
    this.batchTimer = null;
    this.processingStats = {
      totalMessages: 0,
      successfulProcessing: 0,
      failedProcessing: 0,
      alertsGenerated: 0,
      lastProcessed: null
    };
  }
  
  async initialize() {
    try {
      logger.info('Initializing IoT Hub Event Processor');
      
      // Connect to services
      await this.cosmosDBService.connect();
      await this.digitalTwinsService.connect();
      
      // Setup Event Hub consumer
      const connectionString = process.env.IOT_HUB_CONNECTION_STRING;
      const eventHubName = process.env.IOT_HUB_EVENT_HUB_NAME;
      
      this.consumerClient = new EventHubConsumerClient(
        EventHubConsumerClient.defaultConsumerGroupName,
        connectionString,
        eventHubName
      );
      
      logger.info('IoT Hub Event Processor initialized successfully');
      
    } catch (error) {
      logger.error('Failed to initialize IoT Hub Event Processor', { error: error.message });
      throw error;
    }
  }
  
  async start() {
    if (this.isRunning) {
      logger.warn('IoT Hub Event Processor is already running');
      return;
    }
    
    try {
      await this.initialize();
      
      this.isRunning = true;
      
      // Start processing events
      await this.processEvents();
      
      logger.info('IoT Hub Event Processor started');
      
    } catch (error) {
      logger.error('Failed to start IoT Hub Event Processor', { error: error.message });
      throw error;
    }
  }
  
  async processEvents() {
    try {
      const partitionIds = await this.consumerClient.getPartitionIds();
      logger.info('Processing events from partitions', { partitionCount: partitionIds.length });
      
      // Process each partition
      const processingPromises = partitionIds.map(partitionId => 
        this.processPartition(partitionId)
      );
      
      await Promise.all(processingPromises);
      
    } catch (error) {
      logger.error('Error in event processing', { error: error.message });
      throw error;
    }
  }
  
  async processPartition(partitionId) {
    logger.info('Starting to process partition', { partitionId });
    
    try {
      while (this.isRunning) {
        const events = await this.consumerClient.receiveBatch(partitionId, {
          maxWaitTimeInSeconds: 5,
          maxMessageCount: this.batchSize
        });
        
        if (events.length > 0) {
          await this.processEventBatch(events);
        }
      }
    } catch (error) {
      logger.error('Error processing partition', { partitionId, error: error.message });
    }
  }
  
  async processEventBatch(events) {
    const telemetryBatch = [];
    
    for (const event of events) {
      try {
        // Parse event body
        const telemetry = JSON.parse(event.body.toString());
        
        // Validate telemetry
        if (this.validateTelemetry(telemetry)) {
          telemetryBatch.push(telemetry);
          this.processingStats.totalMessages++;
        } else {
          this.processingStats.failedProcessing++;
        }
      } catch (error) {
        logger.error('Error parsing event', { error: error.message });
        this.processingStats.failedProcessing++;
      }
    }
    
    if (telemetryBatch.length > 0) {
      await this.processTelemetryBatch(telemetryBatch);
    }
  }
  
  validateTelemetry(telemetry) {
    if (!telemetry || !telemetry.robotId || !telemetry.timestamp) {
      logger.warn('Invalid telemetry received', { telemetry });
      return false;
    }
    
    // Additional validation can be added here
    return true;
  }
  
  async processTelemetryBatch(telemetryBatch) {
    try {
      // Process each telemetry message
      const processingPromises = telemetryBatch.map(telemetry => 
        this.processSingleTelemetry(telemetry)
      );
      
      const results = await Promise.allSettled(processingPromises);
      
      // Count successful processing
      const successful = results.filter(r => r.status === 'fulfilled').length;
      const failed = results.filter(r => r.status === 'rejected').length;
      
      this.processingStats.successfulProcessing += successful;
      this.processingStats.failedProcessing += failed;
      this.processingStats.lastProcessed = new Date().toISOString();
      
      logger.debug('Telemetry batch processed', { 
        batchSize: telemetryBatch.length,
        successful,
        failed 
      });
      
    } catch (error) {
      logger.error('Error processing telemetry batch', { error: error.message });
    }
  }
  
  async processSingleTelemetry(telemetry) {
    try {
      // Store in Cosmos DB
      const cosmosSuccess = await this.cosmosDBService.storeTelemetry(telemetry);
      
      // Update Digital Twins
      const twinsSuccess = await this.digitalTwinsService.updateRobotTwin(telemetry);
      
      // Generate alerts
      const alerts = this.alertEngine.processTelemetry(telemetry);
      this.processingStats.alertsGenerated += alerts.length;
      
      // Log alerts
      if (alerts.length > 0) {
        logger.info('Alerts generated for telemetry', { 
          robotId: telemetry.robotId,
          alertCount: alerts.length,
          alertTypes: alerts.map(a => a.type)
        });
      }
      
      // Send alerts to intent pipeline (if configured)
      if (alerts.length > 0) {
        await this.sendAlertsToIntentPipeline(alerts);
      }
      
      logger.debug('Telemetry processed successfully', { 
        robotId: telemetry.robotId,
        cosmosSuccess,
        twinsSuccess,
        alertCount: alerts.length
      });
      
    } catch (error) {
      logger.error('Error processing single telemetry', { 
        error: error.message,
        robotId: telemetry.robotId 
      });
      throw error;
    }
  }
  
  async sendAlertsToIntentPipeline(alerts) {
    try {
      const intentPipelineUrl = process.env.INTENT_PIPELINE_URL;
      if (!intentPipelineUrl) {
        logger.debug('Intent pipeline URL not configured, skipping alert sending');
        return;
      }
      
      // This would be implemented to send alerts to your intent pipeline
      // For now, just log the alerts
      logger.info('Would send alerts to intent pipeline', { 
        alertCount: alerts.length,
        intentPipelineUrl 
      });
      
    } catch (error) {
      logger.error('Error sending alerts to intent pipeline', { error: error.message });
    }
  }
  
  async sendCommandToRobot(robotId, command) {
    try {
      // This would be implemented to send commands to robots via IoT Hub
      // For now, just log the command
      logger.info('Command to be sent to robot', { 
        robotId, 
        command 
      });
      
      return { success: true, commandId: `cmd-${Date.now()}` };
      
    } catch (error) {
      logger.error('Error sending command to robot', { 
        error: error.message,
        robotId,
        command 
      });
      return { success: false, error: error.message };
    }
  }
  
  getProcessingStats() {
    return {
      ...this.processingStats,
      isRunning: this.isRunning,
      batchSize: this.batchSize,
      batchTimeout: this.batchTimeout,
      alertStats: this.alertEngine.getAlertStatistics()
    };
  }
  
  getRobotStatus(robotId) {
    return {
      alerts: this.alertEngine.getActiveAlerts(robotId),
      healthScore: this.alertEngine.getRobotHealthScore(robotId),
      lastSeen: this.alertEngine.robotLastSeen.get(robotId)
    };
  }
  
  getAllRobotStatus() {
    const robotIds = ['robot-001', 'robot-002', 'robot-003', 'robot-004', 'robot-005'];
    const status = {};
    
    for (const robotId of robotIds) {
      status[robotId] = this.getRobotStatus(robotId);
    }
    
    return status;
  }
  
  async stop() {
    if (!this.isRunning) {
      logger.warn('IoT Hub Event Processor is not running');
      return;
    }
    
    logger.info('Stopping IoT Hub Event Processor');
    
    this.isRunning = false;
    
    // Clear batch timer
    if (this.batchTimer) {
      clearTimeout(this.batchTimer);
      this.batchTimer = null;
    }
    
    // Close consumer client
    if (this.consumerClient) {
      await this.consumerClient.close();
      this.consumerClient = null;
    }
    
    // Disconnect services
    await this.cosmosDBService.disconnect();
    await this.digitalTwinsService.disconnect();
    
    logger.info('IoT Hub Event Processor stopped');
  }
  
  // Graceful shutdown
  async shutdown() {
    logger.info('Shutting down IoT Hub Event Processor');
    
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

module.exports = IoTHubEventProcessor;
