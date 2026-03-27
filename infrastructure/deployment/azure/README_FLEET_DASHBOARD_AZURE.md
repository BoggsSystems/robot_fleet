# Fleet Dashboard Azure Deployment Guide

## Overview

This guide covers deploying the Fleet Dashboard to Azure Container Apps with full CI/CD pipeline, monitoring, and auto-scaling capabilities.

## Prerequisites

### Azure Resources Required
- Azure Container Registry (ACR)
- Container Apps Environment
- Application Insights
- Resource Group

### Tools Required
- Azure CLI (latest version)
- Docker
- Git

### Authentication
```bash
# Login to Azure
az login

# Set subscription (if multiple)
az account set --subscription "your-subscription-id"

# Login to ACR
az acr login --name kindmoss-6eac8399
```

## Deployment Options

### Option 1: Automated Script (Recommended)

#### Simple Deployment
```bash
cd infrastructure/deployment/azure
./deploy_fleet_dashboard_azure.sh
```

#### Infrastructure as Code (Bicep)
```bash
cd infrastructure/deployment/azure
./deploy_fleet_dashboard_bicep.sh
```

### Option 2: Manual Azure CLI Commands

#### Step 1: Build and Push Image
```bash
cd frontend/web/fleet_dashboard
docker build -t fleet-dashboard:latest .
docker tag fleet-dashboard:latest kindmoss-6eac8399.azurecr.io/fleet-dashboard:latest
docker push kindmoss-6eac8399.azurecr.io/fleet-dashboard:latest
```

#### Step 2: Create Container App
```bash
az containerapp create \
  --name robot-fleet-dashboard \
  --resource-group robot-fleet-simulator-rg \
  --image kindmoss-6eac8399.azurecr.io/fleet-dashboard:latest \
  --environment robot-fleet-env \
  --ingress external \
  --target-port 80 \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 0.5 \
  --memory 1Gi \
  --env-vars \
    NODE_ENV=production \
    REACT_APP_AUTH_URL=https://robotfleet-auth.kindmoss-6eac8399.eastus.azurecontainerapps.io \
    REACT_APP_API_URL=https://robotfleet-ai.kindmoss-6eac8399.eastus.azurecontainerapps.io
```

### Option 3: Bicep Infrastructure as Code

```bash
cd infrastructure/deployment/azure
az deployment group create \
  --resource-group robot-fleet-simulator-rg \
  --template-file fleet-dashboard.bicep \
  --parameters acrUsername=<acr-username> acrPassword=<acr-password>
```

## Configuration

### Environment Variables
- `NODE_ENV`: Set to `production`
- `REACT_APP_AUTH_URL`: Authentication service URL
- `REACT_APP_API_URL`: Backend API service URL
- `APPLICATIONINSIGHTS_CONNECTION_STRING`: Application Insights connection string

### Scaling Configuration
- **Min Replicas**: 1
- **Max Replicas**: 3
- **CPU**: 0.5 cores per replica
- **Memory**: 1Gi per replica
- **Auto-scaling**: HTTP-based (10 concurrent requests per replica)

## CI/CD Pipeline

### GitHub Actions Setup

1. **Repository Secrets**:
   - `ACR_USERNAME`: Azure Container Registry username
   - `ACR_PASSWORD`: Azure Container Registry password
   - `AZURE_CREDENTIALS`: Azure service principal credentials

2. **Workflow Triggers**:
   - Push to `main` branch
   - Changes in `frontend/web/fleet_dashboard/` directory
   - Manual workflow dispatch

3. **Pipeline Steps**:
   - Build Docker image
   - Push to ACR
   - Deploy to Container Apps
   - Health check
   - Notification

### Setting up GitHub Secrets

```bash
# ACR Credentials
az acr credential show --name kindmoss-6eac8399 --query username --output tsv
az acr credential show --name kindmoss-6eac8399 --query passwords[0].value --output tsv

# Azure Service Principal
az ad sp create-for-rbac --name "github-actions-fleet-dashboard" --role contributor --scopes /subscriptions/<subscription-id>/resourceGroups/robot-fleet-simulator-rg
```

## Monitoring and Observability

### Application Insights
- **Automatic instrumentation**: Enabled by default
- **Custom metrics**: Performance, user interactions
- **Alerts**: Error rate, response time
- **Dashboards**: Custom monitoring views

### Log Analytics
```bash
# View container app logs
az containerapp logs show \
  --name robot-fleet-dashboard \
  --resource-group robot-fleet-simulator-rg \
  --follow

# View specific log stream
az containerapp revision show \
  --name robot-fleet-dashboard \
  --resource-group robot-fleet-simulator-rg
```

### Health Monitoring
- **Liveness Probe**: Every 10 seconds
- **Readiness Probe**: Every 5 seconds
- **Startup Probe**: Every 10 seconds (30 failures threshold)

## Security

### Network Security
- **HTTPS**: Enabled by default
- **Ingress**: External only
- **Private Networking**: Optional VNet integration

### Container Security
- **Non-root user**: Configured in Dockerfile
- **Minimal base image**: nginx:alpine
- **Security scanning**: Integrated in CI/CD

### Secrets Management
- **Environment Variables**: Sensitive data in Container App settings
- **Key Vault**: Recommended for production secrets
- **RBAC**: Principle of least privilege

## Performance Optimization

### CDN Integration
```bash
# Configure Azure Front Door
az network front-door create \
  --name fleet-dashboard-cdn \
  --resource-group robot-fleet-simulator-rg \
  --backend-address robot-fleet-dashboard.eastus.azurecontainerapps.io
```

### Static Asset Optimization
- **Compression**: Gzip enabled in nginx
- **Caching**: Browser cache headers configured
- **Bundle Size**: Optimized React build

## Custom Domain and SSL

### Custom Domain Setup
```bash
# Add custom domain
az containerapp hostname add \
  --hostname fleet-dashboard.yourdomain.com \
  --name robot-fleet-dashboard \
  --resource-group robot-fleet-simulator-rg

# Verify domain ownership
az containerapp hostname bind \
  --hostname fleet-dashboard.yourdomain.com \
  --name robot-fleet-dashboard \
  --resource-group robot-fleet-simulator-rg
```

### SSL Certificate
- **Managed Certificate**: Auto-provisioned by Azure
- **Custom Certificate**: Upload your own certificate
- **Certificate Renewal**: Automatic for managed certificates

## Troubleshooting

### Common Issues

1. **Deployment Fails**
   ```bash
   # Check resource group exists
   az group show --name robot-fleet-simulator-rg
   
   # Check Container App logs
   az containerapp logs show --name robot-fleet-dashboard --resource-group robot-fleet-simulator-rg
   ```

2. **Image Pull Errors**
   ```bash
   # Verify ACR login
   az acr login --name kindmoss-6eac8399
   
   # Check image exists
   az acr repository show --name kindmoss-6eac8399 --repository fleet-dashboard
   ```

3. **High Memory Usage**
   ```bash
   # Scale up resources
   az containerapp update \
     --name robot-fleet-dashboard \
     --resource-group robot-fleet-simulator-rg \
     --cpu 1.0 \
     --memory 2Gi
   ```

### Debug Commands
```bash
# Get Container App details
az containerapp show --name robot-fleet-dashboard --resource-group robot-fleet-simulator-rg

# Get revision details
az containerapp revision list --name robot-fleet-dashboard --resource-group robot-fleet-simulator-rg

# Get metrics
az monitor metrics list \
  --resource $(az containerapp show --name robot-fleet-dashboard --resource-group robot-fleet-simulator-rg --query id --output tsv) \
  --metrics CPUUsage MemoryUsage
```

## Cost Optimization

### Resource Recommendations
- **Right-sizing**: Monitor actual usage and adjust CPU/memory
- **Scaling**: Configure appropriate min/max replicas
- **Scheduling**: Consider dev/staging environments with lower resources

### Cost Monitoring
```bash
# View cost analysis
az costmanagement query \
  --resource-group robot-fleet-simulator-rg \
  --dataset "ActualCost" \
  --timeframe "MonthToDate"
```

## Backup and Disaster Recovery

### Configuration Backup
```bash
# Export Container App configuration
az containerapp show \
  --name robot-fleet-dashboard \
  --resource-group robot-fleet-simulator-rg \
  --output yaml > fleet-dashboard-backup.yaml
```

### Recovery Procedures
1. **Recreate from backup**: Use exported YAML configuration
2. **Image rollback**: Deploy previous image tag
3. **DNS failover**: Configure traffic manager

## Next Steps

1. **Production Hardening**:
   - Implement Key Vault integration
   - Set up Azure Policy compliance
   - Configure network security groups

2. **Advanced Monitoring**:
   - Custom metrics and alerts
   - Log analytics workspace
   - Performance baseline establishment

3. **Multi-region Deployment**:
   - Azure Traffic Manager
   - Geo-redundant storage
   - Cross-region replication

4. **Automation**:
   - Infrastructure as Code (Terraform/Bicep)
   - GitOps with Azure DevOps
   - Automated testing pipeline

## Support

For issues and questions:
- Azure Portal: Container Apps blade
- Azure CLI: `az containerapp --help`
- Documentation: [Azure Container Apps Documentation](https://docs.microsoft.com/en-us/azure/container-apps/)
- Support: Create Azure support request
