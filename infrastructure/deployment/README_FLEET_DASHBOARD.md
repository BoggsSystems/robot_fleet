# Fleet Dashboard Deployment Guide

## Overview

This guide covers the deployment of the Fleet Dashboard, which provides real-time monitoring and management capabilities for the robot fleet.

## Prerequisites

- Docker installed and running
- Node.js 18+ (for local development)
- Access to the robot fleet codebase

## Deployment Options

### Option 1: Automated Deployment Script

The easiest way to deploy the Fleet Dashboard is using the automated script:

```bash
cd infrastructure
./deployment/deploy_fleet_dashboard.sh
```

This script will:
- Build the Docker image
- Stop any existing container
- Start a new container with production settings
- Perform a health check

### Option 2: Docker Compose

Deploy using Docker Compose with the frontend-specific configuration:

```bash
cd infrastructure
docker-compose -f docker-compose.frontend.yml up -d fleet-dashboard
```

### Option 3: Manual Docker Deployment

Build and run the container manually:

```bash
cd frontend/web/fleet_dashboard
docker build -t fleet-dashboard .
docker run -d \
  --name fleet-dashboard-prod \
  -p 3000:80 \
  -e NODE_ENV=production \
  -e REACT_APP_AUTH_URL=https://robotfleet-auth.kindmoss-6eac8399.eastus.azurecontainerapps.io \
  -e REACT_APP_API_URL=https://robotfleet-ai.kindmoss-6eac8399.eastus.azurecontainerapps.io \
  --restart unless-stopped \
  fleet-dashboard
```

## Configuration

### Environment Variables

- `NODE_ENV`: Set to `production` for production deployment
- `REACT_APP_AUTH_URL`: Authentication service URL
- `REACT_APP_API_URL`: Backend API service URL

### Port Configuration

- Default port: `3000`
- Container internal port: `80` (nginx)

## Access

Once deployed, the Fleet Dashboard is available at:
- Local: http://localhost:3000
- Production: Update the URL based on your deployment environment

## Health Check

To verify the deployment is working:

```bash
curl -I http://localhost:3000
```

Expected response: `HTTP/1.1 200 OK`

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using the port
   lsof -i :3000
   # Stop the conflicting service
   docker stop fleet-dashboard-prod
   ```

2. **Build failures**
   ```bash
   # Clean build
   cd frontend/web/fleet_dashboard
   rm -rf node_modules package-lock.json
   npm install --legacy-peer-deps
   npm run build
   ```

3. **Container not responding**
   ```bash
   # Check container logs
   docker logs fleet-dashboard-prod
   # Restart container
   docker restart fleet-dashboard-prod
   ```

### Logs

View container logs:
```bash
docker logs -f fleet-dashboard-prod
```

## Development

For local development:

```bash
cd frontend/web/fleet_dashboard
npm install --legacy-peer-deps
npm start
```

The development server will be available at http://localhost:3000.

## Architecture

The Fleet Dashboard uses:
- **React 18** with TypeScript
- **Material-UI** for components
- **Nginx** for production serving
- **Multi-stage Docker build** for optimization

## Security Considerations

- Environment variables contain sensitive URLs
- Use secrets management in production
- Regular security updates for dependencies
- HTTPS termination should be handled by reverse proxy

## Monitoring

Monitor the deployment using:
- Docker container health checks
- Application logs
- Performance metrics
- Error tracking

## Backup and Recovery

- Docker images are versioned
- Configuration is externalized via environment variables
- Static assets are built into the container
- No persistent data stored in the container

## Next Steps

1. Configure reverse proxy (nginx/traefik)
2. Set up SSL/TLS certificates
3. Implement CI/CD pipeline
4. Add monitoring and alerting
5. Configure backup strategies
