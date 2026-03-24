const Joi = require('joi');
const logger = require('../utils/logger');

// Telemetry validation schema
const telemetrySchema = Joi.object({
  robotId: Joi.string().required(),
  timestamp: Joi.string().isoDate().required(),
  battery_level: Joi.number().min(0).max(100).required(),
  position: Joi.object({
    x: Joi.number().required(),
    y: Joi.number().required(),
    z: Joi.number().default(0)
  }).required(),
  orientation: Joi.object({
    roll: Joi.number().required(),
    pitch: Joi.number().required(),
    yaw: Joi.number().required()
  }).required(),
  joint_angles: Joi.object({
    joint1: Joi.number().required(),
    joint2: Joi.number().required(),
    joint3: Joi.number().required(),
    joint4: Joi.number().required(),
    joint5: Joi.number().required(),
    joint6: Joi.number().required()
  }).required(),
  status: Joi.string().valid('idle', 'moving', 'charging', 'error', 'performing_task').required(),
  temperature: Joi.number().min(-50).max(150).required(),
  task_id: Joi.string().allow(null),
  errors: Joi.array().items(Joi.string()).required(),
  speed: Joi.number().min(0).max(10).required()
});

// Command validation schema
const commandSchema = Joi.object({
  robotId: Joi.string().required(),
  command: Joi.string().valid('move_to', 'perform_pose', 'start_task', 'stop_task', 'simulate_fault').required(),
  parameters: Joi.object().when('command', {
    is: 'move_to',
    then: Joi.object({
      x: Joi.number().required(),
      y: Joi.number().required(),
      z: Joi.number().default(0)
    }).required(),
    otherwise: Joi.when('command', {
      is: 'perform_pose',
      then: Joi.object({
        pose_id: Joi.string().required()
      }).required(),
      otherwise: Joi.when('command', {
        is: 'start_task',
        then: Joi.object({
          task_id: Joi.string().required()
        }).required(),
        otherwise: Joi.when('command', {
          is: 'simulate_fault',
          then: Joi.object({
            type: Joi.string().valid('battery_low', 'overheating', 'sensor_error', 'motor_failure').required()
          }).required(),
          otherwise: Joi.object().optional()
        })
      })
    })
  }),
  commandId: Joi.string().optional(),
  timestamp: Joi.string().isoDate().optional()
});

class TelemetryValidator {
  static validate(telemetry) {
    const { error, value } = telemetrySchema.validate(telemetry);
    
    if (error) {
      logger.error('Telemetry validation failed', { 
        error: error.details[0].message, 
        telemetry 
      });
      return { valid: false, error: error.details[0].message };
    }
    
    return { valid: true, data: value };
  }
  
  static validateCommand(command) {
    const { error, value } = commandSchema.validate(command);
    
    if (error) {
      logger.error('Command validation failed', { 
        error: error.details[0].message, 
        command 
      });
      return { valid: false, error: error.details[0].message };
    }
    
    return { valid: true, data: value };
  }
  
  static sanitizeTelemetry(telemetry) {
    // Remove any sensitive or unnecessary fields
    const sanitized = {
      robotId: telemetry.robotId,
      timestamp: telemetry.timestamp,
      battery_level: telemetry.battery_level,
      position: telemetry.position,
      orientation: telemetry.orientation,
      status: telemetry.status,
      temperature: telemetry.temperature,
      task_id: telemetry.task_id,
      errors: telemetry.errors,
      // Include joint angles only if robot is performing task
      joint_angles: telemetry.status === 'performing_task' ? telemetry.joint_angles : undefined,
      speed: telemetry.speed
    };
    
    // Remove undefined values
    Object.keys(sanitized).forEach(key => {
      if (sanitized[key] === undefined) {
        delete sanitized[key];
      }
    });
    
    return sanitized;
  }
}

module.exports = TelemetryValidator;
