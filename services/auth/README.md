# Robot Fleet Backend

Authentication server for the robot fleet management system.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Update `.env` with your configuration (especially the JWT_SECRET).

4. Start the server:
```bash
# Development mode with auto-restart
npm run dev

# Production mode
npm start
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login user
- `GET /auth/profile` - Get user profile (requires auth)
- `POST /auth/logout` - Logout user (requires auth)

### Health Check
- `GET /health` - Server health check

## Usage Examples

### Register
```bash
curl -X POST http://localhost:3001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123", "email": "test@example.com"}'
```

### Login
```bash
curl -X POST http://localhost:3001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}'
```

### Get Profile (with token)
```bash
curl -X GET http://localhost:3001/auth/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Security Notes

- In production, use a proper database instead of in-memory storage
- Store secrets in environment variables
- Use HTTPS in production
- Implement rate limiting for authentication endpoints
- Consider using a more sophisticated token management system
