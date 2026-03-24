# Robot Simulator Service

Multi-robot fleet simulator for Azure IoT Hub integration.

## Features

- **5 Virtual Robots**: Simulated robots with realistic telemetry
- **Azure IoT Hub Integration**: Real-time device-to-cloud communication
- **Command Handling**: Cloud-to-device command processing
- **Realistic Simulation**: Battery drain, movement, task execution, fault simulation
- **Real-time Telemetry**: Position, orientation, status, temperature, task data

## Quick Start

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Update with your Azure IoT Hub connection strings
   ```

3. **Start Simulator**
   ```bash
   npm start
   ```

## Robot Telemetry

Each robot sends telemetry every 3 seconds including:

```json
{
  "robotId": "robot-001",
  "timestamp": "2026-03-22T20:15:00Z",
  "battery_level": 85.5,
  "position": {"x": 10.5, "y": 20.3, "z": 0.0},
  "orientation": {"roll": 0.0, "pitch": 0.0, "yaw": 45.0},
  "joint_angles": {"joint1": 0.5, "joint2": -0.3, "joint3": 1.2},
  "status": "moving",
  "temperature": 42.1,
  "task_id": "task-123",
  "errors": []
}
```

## Supported Commands

Send commands to robots via IoT Hub cloud-to-device messages:

### Move to Position
```json
{
  "command": "move_to",
  "parameters": {"x": 15.0, "y": 25.0, "z": 0.0}
}
```

### Perform Pose
```json
{
  "command": "perform_pose",
  "parameters": {"pose_id": "pose-001"}
}
```

### Start Task
```json
{
  "command": "start_task",
  "parameters": {"task_id": "task-123"}
}
```

### Stop Task
```json
{
  "command": "stop_task"
}
```

### Simulate Fault
```json
{
  "command": "simulate_fault",
  "parameters": {"type": "battery_low"}
}
```

## Robot States

- **idle**: Robot is waiting for commands
- **moving**: Robot is moving to target position
- **performing_task**: Robot is executing a task
- **charging**: Robot is charging battery
- **error**: Robot has encountered an error

## Simulation Behaviors

### Battery Management
- **Drain Rate**: 0.1-0.3% per second when active
- **Idle Drain**: 0.01% per second when idle
- **Auto-charge**: Starts charging when battery < 20%
- **Charge Rate**: 2% per second

### Movement Simulation
- **Speed**: 0.5-2.0 m/s per robot
- **Path Planning**: Direct line movement to target
- **Orientation**: Updates to face movement direction

### Fault Simulation
- **Probability**: 1% chance per update cycle
- **Types**: battery_low, overheating, sensor_error, motor_failure
- **Recovery**: Manual command required

## Environment Variables

```bash
# Azure IoT Hub Configuration
IOT_HUB_CONNECTION_STRING="your-connection-string"

# Robot Configuration
ROBOT_COUNT=5
TELEMETRY_INTERVAL_MS=3000
SIMULATION_SPEED=1.0

# Warehouse Configuration
WAREHOUSE_WIDTH=100
WAREHOUSE_HEIGHT=100
WAREHOUSE_ZONES=4

# Simulation Parameters
BATTERY_DRAIN_RATE=0.1
BATTERY_CHARGE_RATE=2.0
TEMPERATURE_RANGE_MIN=35
TEMPERATURE_RANGE_MAX=65
FAULT_PROBABILITY=0.01

# Logging
LOG_LEVEL=info
LOG_FILE=logs/robot-simulator.log
```

## Docker Deployment

```bash
# Build image
npm run docker:build

# Run container
npm run docker:run
```

## Monitoring

- **Logs**: Check `logs/combined.log` for detailed logs
- **Console**: Real-time status updates
- **IoT Hub**: Monitor device telemetry in Azure Portal

## Troubleshooting

### Connection Issues
1. Verify IoT Hub connection strings
2. Check network connectivity
3. Ensure device is provisioned in IoT Hub

### Low Battery
1. Robots auto-charge when battery < 20%
2. Monitor charging status in logs
3. Adjust drain rates if needed

### Command Not Working
1. Verify command format
2. Check robot connection status
3. Review error logs

## Architecture

```
Robot Simulator → Azure IoT Hub → Event Processor → Cosmos DB → Digital Twins
                                    ↓
                              Commands ← Cloud Services
```

## Next Steps

1. **Deploy to Azure Container Apps**
2. **Integrate with Digital Twins**
3. **Add advanced simulation behaviors**
4. **Implement fleet coordination algorithms**
