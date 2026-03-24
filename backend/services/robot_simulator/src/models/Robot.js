const { v4: uuidv4 } = require('uuid');
const logger = require('../utils/logger');

class Robot {
  constructor(robotId, connectionString) {
    this.robotId = robotId;
    this.connectionString = connectionString;
    this.deviceClient = null;
    this.isConnected = false;
    
    // Robot state
    this.state = {
      robotId: robotId,
      timestamp: new Date().toISOString(),
      battery_level: 100.0,
      position: { x: Math.random() * 100, y: Math.random() * 100, z: 0 },
      orientation: { roll: 0, pitch: 0, yaw: Math.random() * 360 },
      joint_angles: {
        joint1: 0,
        joint2: 0,
        joint3: 0,
        joint4: 0,
        joint5: 0,
        joint6: 0
      },
      status: 'idle', // idle, moving, charging, error, performing_task
      temperature: 40 + Math.random() * 20,
      task_id: null,
      errors: [],
      speed: 0.5 + Math.random() * 1.5 // m/s
    };
    
    // Simulation parameters
    this.targetPosition = null;
    this.currentTask = null;
    this.batteryDrainRate = 0.1 + Math.random() * 0.2;
    this.faultProbability = 0.01;
    
    logger.info(`Robot ${robotId} initialized`, { robotId, initialPosition: this.state.position });
  }
  
  async connect() {
    try {
      const { Client } = require('azure-iot-device');
      const { Mqtt } = require('azure-iot-device-mqtt');
      
      this.deviceClient = Client.fromConnectionString(this.connectionString, Mqtt);
      
      // Set up message handler for cloud-to-device messages
      this.deviceClient.on('message', (msg) => {
        this.handleCloudCommand(msg);
      });
      
      // Set up connection status handler
      this.deviceClient.on('connect', () => {
        this.isConnected = true;
        this.state.status = 'idle';
        logger.info(`Robot ${this.robotId} connected to IoT Hub`, { robotId: this.robotId });
      });
      
      this.deviceClient.on('disconnect', () => {
        this.isConnected = false;
        this.state.status = 'error';
        this.state.errors.push('Connection lost');
        logger.error(`Robot ${this.robotId} disconnected from IoT Hub`, { robotId: this.robotId });
      });
      
      await this.deviceClient.open();
      logger.info(`Robot ${this.robotId} connection established`, { robotId: this.robotId });
      
    } catch (error) {
      logger.error(`Failed to connect robot ${this.robotId}`, { robotId: this.robotId, error: error.message });
      throw error;
    }
  }
  
  handleCloudCommand(message) {
    try {
      const command = JSON.parse(message.getData());
      logger.info(`Robot ${this.robotId} received command`, { robotId: this.robotId, command });
      
      switch (command.command) {
        case 'move_to':
          this.moveTo(command.parameters);
          break;
        case 'perform_pose':
          this.performPose(command.parameters);
          break;
        case 'start_task':
          this.startTask(command.parameters);
          break;
        case 'stop_task':
          this.stopTask();
          break;
        case 'simulate_fault':
          this.simulateFault(command.parameters);
          break;
        default:
          logger.warn(`Unknown command received`, { robotId: this.robotId, command: command.command });
      }
      
      // Send command acknowledgment
      this.sendCommandAck(command);
      
    } catch (error) {
      logger.error(`Error processing command`, { robotId: this.robotId, error: error.message });
    }
  }
  
  async sendCommandAck(command) {
    const ack = {
      robotId: this.robotId,
      commandId: command.commandId || uuidv4(),
      command: command.command,
      status: 'acknowledged',
      timestamp: new Date().toISOString()
    };
    
    try {
      const Message = require('azure-iot-device').Message;
      await this.deviceClient.sendEvent(new Message(JSON.stringify(ack)));
    } catch (error) {
      logger.error(`Failed to send command acknowledgment from robot ${this.robotId}`, {
        robotId: this.robotId,
        error: error.message
      });
    }
  }
  
  moveTo(parameters) {
    if (!parameters || !parameters.x || !parameters.y) {
      logger.warn(`Invalid move_to parameters`, { robotId: this.robotId, parameters });
      return;
    }
    
    this.targetPosition = { x: parameters.x, y: parameters.y, z: parameters.z || 0 };
    this.state.status = 'moving';
    logger.info(`Robot ${this.robotId} moving to position`, { 
      robotId: this.robotId, 
      from: this.state.position, 
      to: this.targetPosition 
    });
  }
  
  performPose(parameters) {
    if (!parameters || !parameters.pose_id) {
      logger.warn(`Invalid perform_pose parameters`, { robotId: this.robotId, parameters });
      return;
    }
    
    this.state.status = 'performing_task';
    this.currentTask = {
      type: 'pose',
      pose_id: parameters.pose_id,
      startTime: new Date().toISOString()
    };
    
    // Simulate joint movements
    this.state.joint_angles = {
      joint1: Math.random() * Math.PI * 2,
      joint2: Math.random() * Math.PI,
      joint3: Math.random() * Math.PI * 2,
      joint4: Math.random() * Math.PI,
      joint5: Math.random() * Math.PI * 2,
      joint6: Math.random() * Math.PI
    };
    
    logger.info(`Robot ${this.robotId} performing pose`, { 
      robotId: this.robotId, 
      poseId: parameters.pose_id 
    });
  }
  
  startTask(parameters) {
    if (!parameters || !parameters.task_id) {
      logger.warn(`Invalid start_task parameters`, { robotId: this.robotId, parameters });
      return;
    }
    
    this.state.status = 'performing_task';
    this.state.task_id = parameters.task_id;
    this.currentTask = {
      type: 'task',
      task_id: parameters.task_id,
      startTime: new Date().toISOString()
    };
    
    logger.info(`Robot ${this.robotId} starting task`, { 
      robotId: this.robotId, 
      taskId: parameters.task_id 
    });
  }
  
  stopTask() {
    this.state.status = 'idle';
    this.state.task_id = null;
    this.currentTask = null;
    
    logger.info(`Robot ${this.robotId} stopped current task`, { robotId: this.robotId });
  }
  
  simulateFault(parameters) {
    const faultType = parameters?.type || 'random';
    
    switch (faultType) {
      case 'battery_low':
        this.state.battery_level = 5;
        break;
      case 'overheating':
        this.state.temperature = 85;
        break;
      case 'sensor_error':
        this.state.errors.push('Sensor malfunction detected');
        break;
      case 'motor_failure':
        this.state.errors.push('Motor failure detected');
        this.state.speed = 0;
        break;
      default:
        // Random fault
        const faults = ['battery_low', 'overheating', 'sensor_error', 'motor_failure'];
        const randomFault = faults[Math.floor(Math.random() * faults.length)];
        this.simulateFault({ type: randomFault });
        return;
    }
    
    this.state.status = 'error';
    logger.warn(`Robot ${this.robotId} fault simulated`, { 
      robotId: this.robotId, 
      faultType,
      state: this.state 
    });
  }
  
  updateSimulation() {
    // Update position if moving
    if (this.state.status === 'moving' && this.targetPosition) {
      const dx = this.targetPosition.x - this.state.position.x;
      const dy = this.targetPosition.y - this.state.position.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      
      if (distance > 0.5) { // Not at target yet
        const moveDistance = Math.min(this.state.speed * 0.1, distance); // 0.1s time step
        const ratio = moveDistance / distance;
        
        this.state.position.x += dx * ratio;
        this.state.position.y += dy * ratio;
        
        // Update orientation to face movement direction
        this.state.orientation.yaw = Math.atan2(dy, dx) * 180 / Math.PI;
        
        // Drain battery while moving
        this.state.battery_level -= this.batteryDrainRate * 2;
      } else {
        // Reached target
        this.state.position = { ...this.targetPosition };
        this.state.status = 'idle';
        this.targetPosition = null;
        logger.info(`Robot ${this.robotId} reached target position`, { 
          robotId: this.robotId, 
          position: this.state.position 
        });
      }
    }
    
    // Update temperature
    const tempChange = (Math.random() - 0.5) * 2; // Random fluctuation
    this.state.temperature = Math.max(20, Math.min(80, this.state.temperature + tempChange));
    
    // Battery drain
    if (this.state.status === 'moving' || this.state.status === 'performing_task') {
      this.state.battery_level -= this.batteryDrainRate;
    } else if (this.state.status === 'idle') {
      this.state.battery_level -= this.batteryDrainRate * 0.1;
    }
    
    // Auto-charge if battery is low
    if (this.state.battery_level < 20 && this.state.status !== 'charging') {
      this.state.status = 'charging';
      this.state.position = { x: 0, y: 0, z: 0 }; // Move to charging station
      logger.info(`Robot ${this.robotId} started charging`, { 
        robotId: this.robotId, 
        batteryLevel: this.state.battery_level 
      });
    }
    
    if (this.state.status === 'charging') {
      this.state.battery_level = Math.min(100, this.state.battery_level + 2.0);
      if (this.state.battery_level >= 95) {
        this.state.status = 'idle';
        logger.info(`Robot ${this.robotId} finished charging`, { 
          robotId: this.robotId, 
          batteryLevel: this.state.battery_level 
        });
      }
    }
    
    // Random fault simulation
    if (Math.random() < this.faultProbability && this.state.status !== 'error') {
      this.simulateFault({ type: 'random' });
    }
    
    // Update timestamp
    this.state.timestamp = new Date().toISOString();
  }
  
  async sendTelemetry() {
    if (!this.isConnected) {
      logger.warn(`Cannot send telemetry - robot ${this.robotId} not connected`, { robotId: this.robotId });
      return;
    }
    
    try {
      const Message = require('azure-iot-device').Message;
      const telemetry = JSON.stringify(this.state);
      const message = new Message(telemetry);
      
      await this.deviceClient.sendEvent(message);
      logger.debug(`Telemetry sent from robot ${this.robotId}`, { 
        robotId: this.robotId, 
        batteryLevel: this.state.battery_level,
        status: this.state.status 
      });
      
    } catch (error) {
      logger.error(`Failed to send telemetry from robot ${this.robotId}`, { 
        robotId: this.robotId, 
        error: error.message 
      });
    }
  }
  
  async disconnect() {
    if (this.deviceClient) {
      await this.deviceClient.close();
      this.isConnected = false;
      logger.info(`Robot ${this.robotId} disconnected`, { robotId: this.robotId });
    }
  }
}

module.exports = Robot;
