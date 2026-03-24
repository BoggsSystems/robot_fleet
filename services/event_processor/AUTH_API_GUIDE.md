# Event Processor Authentication API

## Authentication Endpoints

### Setup User Management System
```bash
POST /api/auth/setup
```
Initializes the user management system, creates containers, and seeds the fleet manager user.

### Login
```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "fleet_manager",
  "password": "FleetManager123!"
}
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": "fleet_manager",
    "username": "fleet_manager",
    "email": "manager@robotfleet.com",
    "role": "fleet_manager",
    "profile": {
      "firstName": "John",
      "lastName": "Doe",
      "department": "Operations"
    },
    "permissions": [
      "robots.read",
      "robots.write",
      "robots.command",
      "alerts.read",
      "alerts.write",
      "alerts.acknowledge",
      "alerts.resolve",
      "system.read",
      "system.health",
      "reports.read",
      "reports.export"
    ]
  },
  "tokens": {
    "accessToken": "eyJhbGciOiJIUzI1NiIs...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIs..."
  }
}
```

### Refresh Token
```bash
POST /api/auth/refresh
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "refreshToken": "eyJhbGciOiJIUzI1NiIs..."
}
```

### Logout
```bash
POST /api/auth/logout
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "refreshToken": "eyJhbGciOiJIUzI1NiIs..."
}
```

### Get Current User
```bash
GET /api/auth/me
Authorization: Bearer <access_token>
```

## Protected API Endpoints

All endpoints below require authentication via `Authorization: Bearer <access_token>` header.

### Robot Management

#### Get All Robots
```bash
GET /api/robots
Authorization: Bearer <access_token>
```

#### Get Specific Robot
```bash
GET /api/robots/robot-001
Authorization: Bearer <access_token>
```

#### Send Command to Robot
```bash
POST /api/robots/robot-001/commands
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "command": "move_to",
  "parameters": {
    "x": 10.0,
    "y": 20.0,
    "z": 0.0
  }
}
```

### Alert Management

#### Get All Alerts
```bash
GET /api/alerts
Authorization: Bearer <access_token>
```

#### Get Alerts for Specific Robot
```bash
GET /api/alerts?robotId=robot-001
Authorization: Bearer <access_token>
```

#### Acknowledge Alert
```bash
POST /api/alerts/alert-123/acknowledge
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "acknowledged": true,
  "notes": "Investigating battery issue"
}
```

#### Resolve Alert
```bash
POST /api/alerts/alert-123/resolve
Authorization: Bearer <access_token>
```

#### Get Alert Statistics
```bash
GET /api/alerts/statistics
Authorization: Bearer <access_token>
```

### Digital Twins

#### Get All Robot Twins
```bash
GET /api/digitaltwins/robots
Authorization: Bearer <access_token>
```

#### Get All Zone Twins
```bash
GET /api/digitaltwins/zones
Authorization: Bearer <access_token>
```

#### Get Robots in Zone
```bash
GET /api/digitaltwins/zone-charging/robots
Authorization: Bearer <access_token>
```

#### Create Task Twin
```bash
POST /api/digitaltwins/tasks
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "taskId": "task-001",
  "taskType": "pickup_package",
  "priority": 1
}
```

### System Monitoring

#### Get Processing Statistics
```bash
GET /api/stats
Authorization: Bearer <access_token>
```

## Error Responses

### Authentication Errors
```json
{
  "error": "Invalid credentials",
  "code": "TOKEN_INVALID"
}
```

### Permission Errors
```json
{
  "error": "Insufficient permissions",
  "code": "PERMISSION_DENIED",
  "requiredPermission": "robots.command"
}
```

### Validation Errors
```json
{
  "error": "Invalid request data",
  "code": "VALIDATION_ERROR",
  "details": "Username must be at least 3 characters long"
}
```

### Rate Limiting
```json
{
  "error": "Too many requests",
  "code": "RATE_LIMIT_EXCEEDED"
}
```

## Testing the Authentication Flow

### 1. Setup User Management
```bash
curl -X POST http://localhost:3001/api/auth/setup
```

### 2. Login
```bash
curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "fleet_manager",
    "password": "FleetManager123!"
  }'
```

### 3. Use Access Token
```bash
# Store the access token from login response
ACCESS_TOKEN="eyJhbGciOiJIUzI1NiIs..."

# Get robots
curl -X GET http://localhost:3001/api/robots \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### 4. Refresh Token
```bash
curl -X POST http://localhost:3001/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refreshToken": "eyJhbGciOiJIUzI1NiIs..."
  }'
```

### 5. Logout
```bash
curl -X POST http://localhost:3001/api/auth/logout \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "refreshToken": "eyJhbGciOiJIUzI1NiIs..."
  }'
```

## Security Features

### JWT Token Configuration
- **Access Token**: 15 minutes expiration
- **Refresh Token**: 7 days expiration
- **Algorithm**: HS256
- **Secret**: Configurable via environment variables

### Rate Limiting
- **Login Endpoint**: 5 requests per 15 minutes
- **General API**: 100 requests per 15 minutes

### Permission-Based Access Control
- **fleet_manager**: Full access to all features
- **technical_engineer**: Read/write access to robots and alerts
- **warehouse_manager**: Read/command access to robots

### Audit Logging
- All authentication events logged
- Failed login attempts tracked
- Account lockout after 5 failed attempts
- Session management and tracking

## Default Credentials

```
Username: fleet_manager
Password: FleetManager123!
Role: fleet_manager
```

**Important**: Change the default password in production!
