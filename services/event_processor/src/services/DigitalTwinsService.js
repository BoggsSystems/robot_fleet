const { DigitalTwinsClient } = require('@azure/digital-twins-core');
const { DefaultAzureCredential } = require('@azure/identity');
const logger = require('../utils/logger');
const TelemetryValidator = require('../utils/TelemetryValidator');

class DigitalTwinsService {
  constructor() {
    this.client = null;
    this.endpoint = process.env.DIGITAL_TWINS_ENDPOINT;
    this.isConnected = false;
    this.twinModels = new Map();
    this.twinInstances = new Map();
  }
  
  async connect() {
    try {
      const credential = new DefaultAzureCredential();
      this.client = new DigitalTwinsClient(this.endpoint, credential);
      
      // Test connection
      await this.client.queryTwins('SELECT TOP 1 * FROM digitaltwins');
      this.isConnected = true;
      
      logger.info('Connected to Digital Twins', { endpoint: this.endpoint });
      
      // Initialize models and instances
      await this.initializeModels();
      await this.initializeTwinInstances();
      
    } catch (error) {
      logger.error('Failed to connect to Digital Twins', { error: error.message });
      throw error;
    }
  }
  
  async initializeModels() {
    try {
      // Robot model
      const robotModel = {
        '@id': 'dtmi:robotfleet:Robot;1',
        '@type': 'Interface',
        '@context': 'dtmi:dtdl:context;2',
        'displayName': 'Robot',
        'contents': [
          {
            '@type': 'Property',
            'name': 'batteryLevel',
            'schema': 'double',
            'writable': false
          },
          {
            '@type': 'Property',
            'name': 'status',
            'schema': 'string',
            'writable': false
          },
          {
            '@type': 'Property',
            'name': 'temperature',
            'schema': 'double',
            'writable': false
          },
          {
            '@type': 'Property',
            'name': 'currentTask',
            'schema': 'string',
            'writable': false
          },
          {
            '@type': 'Property',
            'name': 'lastSeen',
            'schema': 'dateTime',
            'writable': false
          },
          {
            '@type': 'Relationship',
            'name': 'locatedIn',
            'target': 'dtmi:robotfleet:Zone;1'
          },
          {
            '@type': 'Relationship',
            'name': 'assignedTask',
            'target': 'dtmi:robotfleet:Task;1'
          }
        ]
      };
      
      // Zone model
      const zoneModel = {
        '@id': 'dtmi:robotfleet:Zone;1',
        '@type': 'Interface',
        '@context': 'dtmi:dtdl:context;2',
        'displayName': 'Zone',
        'contents': [
          {
            '@type': 'Property',
            'name': 'name',
            'schema': 'string',
            'writable': false
          },
          {
            '@type': 'Property',
            'name': 'coordinates',
            'schema': {
              '@type': 'Map',
              'mapKey': {'name': 'x', 'schema': 'double'},
              'mapValue': {'name': 'y', 'schema': 'double'}
            }
          },
          {
            '@type': 'Property',
            'name': 'capacity',
            'schema': 'integer',
            'writable': false
          },
          {
            '@type': 'Property',
            'name': 'currentOccupancy',
            'schema': 'integer',
            'writable': false
          }
        ]
      };
      
      // Task model
      const taskModel = {
        '@id': 'dtmi:robotfleet:Task;1',
        '@type': 'Interface',
        '@context': 'dtmi:dtdl:context;2',
        'displayName': 'Task',
        'contents': [
          {
            '@type': 'Property',
            'name': 'taskId',
            'schema': 'string',
            'writable': false
          },
          {
            '@type': 'Property',
            'name': 'type',
            'schema': 'string',
            'writable': false
          },
          {
            '@type': 'Property',
            'name': 'status',
            'schema': 'string',
            'writable': false
          },
          {
            '@type': 'Property',
            'name': 'priority',
            'schema': 'integer',
            'writable': false
          },
          {
            '@type': 'Property',
            'name': 'createdAt',
            'schema': 'dateTime',
            'writable': false
          }
        ]
      };
      
      // Try to create models (they might already exist)
      const models = [robotModel, zoneModel, taskModel];
      
      for (const model of models) {
        try {
          const modelId = await this.client.createModels([model]);
          logger.info('Created Digital Twin model', { modelId: modelId[0] });
          this.twinModels.set(model['@id'], model);
        } catch (error) {
          if (error.message.includes('already exists')) {
            logger.info('Digital Twin model already exists', { modelId: model['@id'] });
            this.twinModels.set(model['@id'], model);
          } else {
            logger.warn('Failed to create Digital Twin model', { 
              modelId: model['@id'], 
              error: error.message 
            });
          }
        }
      }
      
    } catch (error) {
      logger.error('Failed to initialize Digital Twin models', { error: error.message });
    }
  }
  
  async initializeTwinInstances() {
    try {
      // Create zone instances
      const zones = [
        { id: 'zone-charging', name: 'Charging Station', x: 0, y: 0, capacity: 5 },
        { id: 'zone-warehouse-a', name: 'Warehouse Zone A', x: 25, y: 25, capacity: 10 },
        { id: 'zone-warehouse-b', name: 'Warehouse Zone B', x: 75, y: 25, capacity: 10 },
        { id: 'zone-warehouse-c', name: 'Warehouse Zone C', x: 25, y: 75, capacity: 10 },
        { id: 'zone-warehouse-d', name: 'Warehouse Zone D', x: 75, y: 75, capacity: 10 }
      ];
      
      for (const zone of zones) {
        const zoneTwin = {
          '$dtId': zone.id,
          '$metadata': {
            $model: 'dtmi:robotfleet:Zone;1'
          },
          name: zone.name,
          coordinates: { x: zone.x, y: zone.y },
          capacity: zone.capacity,
          currentOccupancy: 0
        };
        
        try {
          await this.client.upsertDigitalTwin(zone.id, zoneTwin);
          logger.info('Created zone twin', { zoneId: zone.id });
          this.twinInstances.set(zone.id, zoneTwin);
        } catch (error) {
          if (error.message.includes('already exists')) {
            logger.info('Zone twin already exists', { zoneId: zone.id });
            this.twinInstances.set(zone.id, zoneTwin);
          } else {
            logger.warn('Failed to create zone twin', { zoneId: zone.id, error: error.message });
          }
        }
      }
      
      // Create robot twins for all robots
      const robotIds = ['robot-001', 'robot-002', 'robot-003', 'robot-004', 'robot-005'];
      
      for (const robotId of robotIds) {
        const robotTwin = {
          '$dtId': robotId,
          '$metadata': {
            $model: 'dtmi:robotfleet:Robot;1'
          },
          batteryLevel: 100,
          status: 'idle',
          temperature: 40,
          currentTask: null,
          lastSeen: new Date().toISOString()
        };
        
        try {
          await this.client.upsertDigitalTwin(robotId, robotTwin);
          logger.info('Created robot twin', { robotId });
          this.twinInstances.set(robotId, robotTwin);
        } catch (error) {
          if (error.message.includes('already exists')) {
            logger.info('Robot twin already exists', { robotId });
            this.twinInstances.set(robotId, robotTwin);
          } else {
            logger.warn('Failed to create robot twin', { robotId, error: error.message });
          }
        }
      }
      
    } catch (error) {
      logger.error('Failed to initialize Digital Twin instances', { error: error.message });
    }
  }
  
  async updateRobotTwin(telemetry) {
    if (!this.isConnected) {
      logger.error('Digital Twins not connected');
      return false;
    }
    
    try {
      const robotId = telemetry.robotId;
      
      // Update twin properties
      const updatePayload = {
        batteryLevel: telemetry.battery_level,
        status: telemetry.status,
        temperature: telemetry.temperature,
        currentTask: telemetry.task_id,
        lastSeen: new Date().toISOString()
      };
      
      // Create patch operations
      const patch = [];
      for (const [key, value] of Object.entries(updatePayload)) {
        patch.push({
          op: 'Replace',
          path: `/${key}`,
          value: value
        });
      }
      
      // Update twin
      await this.client.updateDigitalTwin(robotId, patch);
      
      logger.debug('Updated robot twin', { 
        robotId, 
        batteryLevel: telemetry.battery_level,
        status: telemetry.status 
      });
      
      return true;
      
    } catch (error) {
      logger.error('Failed to update robot twin', { 
        error: error.message,
        robotId: telemetry.robotId 
      });
      return false;
    }
  }
  
  async getRobotTwin(robotId) {
    if (!this.isConnected) {
      logger.error('Digital Twins not connected');
      return null;
    }
    
    try {
      const twin = await this.client.getDigitalTwin(robotId);
      return twin;
    } catch (error) {
      logger.error('Failed to get robot twin', { 
        error: error.message,
        robotId 
      });
      return null;
    }
  }
  
  async getAllRobotTwins() {
    if (!this.isConnected) {
      logger.error('Digital Twins not connected');
      return [];
    }
    
    try {
      const query = 'SELECT * FROM DigitalTwins T WHERE IS_OF_MODEL(T, \'dtmi:robotfleet:Robot;1\')';
      const twins = await this.client.queryTwins(query);
      
      return twins;
    } catch (error) {
      logger.error('Failed to get all robot twins', { error: error.message });
      return [];
    }
  }
  
  async getZoneTwins() {
    if (!this.isConnected) {
      logger.error('Digital Twins not connected');
      return [];
    }
    
    try {
      const query = 'SELECT * FROM DigitalTwins T WHERE IS_OF_MODEL(T, \'dtmi:robotfleet:Zone;1\')';
      const twins = await this.client.queryTwins(query);
      
      return twins;
    } catch (error) {
      logger.error('Failed to get zone twins', { error: error.message });
      return [];
    }
  }
  
  async getRobotsInZone(zoneId) {
    if (!this.isConnected) {
      logger.error('Digital Twins not connected');
      return [];
    }
    
    try {
      const query = `SELECT * FROM DigitalTwins T WHERE IS_OF_MODEL(T, 'dtmi:robotfleet:Robot;1') AND EXISTS(SELECT REL(R, Target) FROM RELATIONSHIPS R WHERE IS_OF_MODEL(R, 'dtmi:robotfleet:Robot;1') AND Target = '${zoneId}')`;
      const twins = await this.client.queryTwins(query);
      
      return twins;
    } catch (error) {
      logger.error('Failed to get robots in zone', { 
        error: error.message,
        zoneId 
      });
      return [];
    }
  }
  
  async createTaskTwin(taskId, taskType, priority = 1) {
    if (!this.isConnected) {
      logger.error('Digital Twins not connected');
      return false;
    }
    
    try {
      const taskTwin = {
        '$dtId': taskId,
        '$metadata': {
          $model: 'dtmi:robotfleet:Task;1'
        },
        taskId: taskId,
        type: taskType,
        status: 'pending',
        priority: priority,
        createdAt: new Date().toISOString()
      };
      
      await this.client.upsertDigitalTwin(taskId, taskTwin);
      
      logger.info('Created task twin', { taskId, taskType });
      return true;
      
    } catch (error) {
      logger.error('Failed to create task twin', { 
        error: error.message,
        taskId 
      });
      return false;
    }
  }
  
  async disconnect() {
    try {
      if (this.client) {
        // Digital Twins client doesn't have explicit disconnect
        this.isConnected = false;
        logger.info('Disconnected from Digital Twins');
      }
    } catch (error) {
      logger.error('Error disconnecting from Digital Twins', { error: error.message });
    }
  }
}

module.exports = DigitalTwinsService;
