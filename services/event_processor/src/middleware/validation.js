const Joi = require('joi');

// Login validation schema
const loginSchema = Joi.object({
  username: Joi.string()
    .alphanum()
    .min(3)
    .max(30)
    .required()
    .messages({
      'string.alphanum': 'Username must only contain alphanumeric characters',
      'string.min': 'Username must be at least 3 characters long',
      'string.max': 'Username must not exceed 30 characters',
      'any.required': 'Username is required'
    }),
  password: Joi.string()
    .min(6)
    .max(128)
    .required()
    .messages({
      'string.min': 'Password must be at least 6 characters long',
      'string.max': 'Password must not exceed 128 characters',
      'any.required': 'Password is required'
    })
});

// Refresh token validation schema
const refreshTokenSchema = Joi.object({
  refreshToken: Joi.string()
    .required()
    .messages({
      'any.required': 'Refresh token is required',
      'string.empty': 'Refresh token cannot be empty'
    })
});

// User creation validation schema
const createUserSchema = Joi.object({
  username: Joi.string()
    .alphanum()
    .min(3)
    .max(30)
    .required()
    .messages({
      'string.alphanum': 'Username must only contain alphanumeric characters',
      'string.min': 'Username must be at least 3 characters long',
      'string.max': 'Username must not exceed 30 characters',
      'any.required': 'Username is required'
    }),
  email: Joi.string()
    .email()
    .required()
    .messages({
      'string.email': 'Email must be a valid email address',
      'any.required': 'Email is required'
    }),
  password: Joi.string()
    .min(8)
    .max(128)
    .pattern(new RegExp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]'))
    .required()
    .messages({
      'string.min': 'Password must be at least 8 characters long',
      'string.max': 'Password must not exceed 128 characters',
      'string.pattern.base': 'Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character',
      'any.required': 'Password is required'
    }),
  role: Joi.string()
    .valid('fleet_manager', 'technical_engineer', 'warehouse_manager')
    .default('fleet_manager')
    .messages({
      'any.only': 'Role must be one of: fleet_manager, technical_engineer, warehouse_manager'
    }),
  profile: Joi.object({
    firstName: Joi.string()
      .min(1)
      .max(50)
      .default('')
      .messages({
        'string.min': 'First name cannot be empty',
        'string.max': 'First name must not exceed 50 characters'
      }),
    lastName: Joi.string()
      .min(1)
      .max(50)
      .default('')
      .messages({
        'string.min': 'Last name cannot be empty',
        'string.max': 'Last name must not exceed 50 characters'
      }),
    department: Joi.string()
      .min(1)
      .max(50)
      .default('Operations')
      .messages({
        'string.min': 'Department cannot be empty',
        'string.max': 'Department must not exceed 50 characters'
      }),
    phone: Joi.string()
      .pattern(new RegExp('^\\+?[1-9]\\d{1,14}$'))
      .optional()
      .allow('')
      .messages({
        'string.pattern.base': 'Phone number must be a valid international phone number'
      }),
    timezone: Joi.string()
      .default('America/New_York')
      .messages({
        'any.default': 'Default timezone will be used'
      })
  }).default()
});

// Robot command validation schema
const robotCommandSchema = Joi.object({
  command: Joi.string()
    .valid('move_to', 'perform_pose', 'start_task', 'stop_task', 'simulate_fault')
    .required()
    .messages({
      'any.only': 'Command must be one of: move_to, perform_pose, start_task, stop_task, simulate_fault',
      'any.required': 'Command is required'
    }),
  parameters: Joi.object()
    .when('command', {
      is: 'move_to',
      then: Joi.object({
        x: Joi.number()
          .required()
          .messages({
            'any.required': 'X coordinate is required for move_to command'
          }),
        y: Joi.number()
          .required()
          .messages({
            'any.required': 'Y coordinate is required for move_to command'
          }),
        z: Joi.number()
          .default(0)
          .messages({
            'any.default': 'Z coordinate will default to 0'
          })
      }).required(),
      otherwise: Joi.when('command', {
        is: 'perform_pose',
        then: Joi.object({
          pose_id: Joi.string()
            .required()
            .messages({
              'any.required': 'Pose ID is required for perform_pose command'
            })
        }).required(),
        otherwise: Joi.when('command', {
          is: 'start_task',
          then: Joi.object({
            task_id: Joi.string()
              .required()
              .messages({
                'any.required': 'Task ID is required for start_task command'
              })
          }).required(),
          otherwise: Joi.when('command', {
            is: 'simulate_fault',
            then: Joi.object({
              type: Joi.string()
                .valid('battery_low', 'overheating', 'sensor_error', 'motor_failure')
                .required()
                .messages({
                  'any.only': 'Fault type must be one of: battery_low, overheating, sensor_error, motor_failure',
                  'any.required': 'Fault type is required for simulate_fault command'
                })
          }).required(),
          otherwise: Joi.object().optional()
        })
      })
    })
  }).optional(),
  commandId: Joi.string()
    .optional()
    .messages({
      'string.base': 'Command ID must be a string'
    }),
  timestamp: Joi.string()
    .isoDate()
    .optional()
    .messages({
      'string.isoDate': 'Timestamp must be a valid ISO date'
    })
});

// Alert acknowledgment validation schema
const alertAcknowledgeSchema = Joi.object({
  acknowledged: Joi.boolean()
    .required()
    .messages({
      'any.required': 'Acknowledged status is required'
    }),
  notes: Joi.string()
    .max(500)
    .optional()
    .allow('')
    .messages({
      'string.max': 'Notes must not exceed 500 characters'
    })
});

// Digital Twins task creation validation schema
const taskTwinSchema = Joi.object({
  taskId: Joi.string()
    .required()
    .messages({
      'any.required': 'Task ID is required'
    }),
  taskType: Joi.string()
    .required()
    .messages({
      'any.required': 'Task type is required'
    }),
  priority: Joi.number()
    .integer()
    .min(1)
    .max(10)
    .default(1)
    .messages({
      'number.base': 'Priority must be a number',
      'number.integer': 'Priority must be an integer',
      'number.min': 'Priority must be at least 1',
      'number.max': 'Priority must not exceed 10'
    })
});

// Query parameter validation schemas
const robotIdSchema = Joi.object({
  robotId: Joi.string()
    .pattern(/^robot-\d{3}$/)
    .required()
    .messages({
      'string.pattern.base': 'Robot ID must be in format robot-XXX (e.g., robot-001)',
      'any.required': 'Robot ID is required'
    })
});

const paginationSchema = Joi.object({
  page: Joi.number()
    .integer()
    .min(1)
    .default(1)
    .messages({
      'number.base': 'Page must be a number',
      'number.integer': 'Page must be an integer',
      'number.min': 'Page must be at least 1'
    }),
  limit: Joi.number()
    .integer()
    .min(1)
    .max(100)
    .default(10)
    .messages({
      'number.base': 'Limit must be a number',
      'number.integer': 'Limit must be an integer',
      'number.min': 'Limit must be at least 1',
      'number.max': 'Limit must not exceed 100'
    })
});

const timeRangeSchema = Joi.object({
  startTime: Joi.string()
    .isoDate()
    .required()
    .messages({
      'string.isoDate': 'Start time must be a valid ISO date',
      'any.required': 'Start time is required'
    }),
  endTime: Joi.string()
    .isoDate()
    .required()
    .messages({
      'string.isoDate': 'End time must be a valid ISO date',
      'any.required': 'End time is required'
    })
});

module.exports = {
  loginSchema,
  refreshTokenSchema,
  createUserSchema,
  robotCommandSchema,
  alertAcknowledgeSchema,
  taskTwinSchema,
  robotIdSchema,
  paginationSchema,
  timeRangeSchema
};
