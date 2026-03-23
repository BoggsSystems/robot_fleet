# 🏭 Warehouse Digital Twin Management Service

## 📋 Overview

This C# service provides comprehensive Azure Digital Twins management for warehouse operations, including warehouse modeling, zone management, robot fleet coordination, and client configuration capabilities.

## 🏗️ Architecture

### **Core Components**
- **DigitalTwinManager**: Core Azure Digital Twins integration
- **ConfigurationService**: Client configuration and setup
- **Validators**: Comprehensive data validation using FluentValidation
- **Controllers**: REST API endpoints for all operations

### **Key Features**
- ✅ **Warehouse Modeling**: Complete warehouse digital twin creation
- ✅ **Zone Management**: Dynamic zone configuration and relationships
- ✅ **Robot Fleet**: Robot asset management and status tracking
- ✅ **Client Configuration**: Self-service warehouse setup
- ✅ **Business Rules**: Configurable operational rules
- ✅ **Real-time Updates**: Live state synchronization
- ✅ **Validation**: Comprehensive input validation
- ✅ **Monitoring**: Application Insights integration

## 🚀 Getting Started

### **Prerequisites**
- .NET 8.0 SDK
- Azure Digital Twins instance
- Azure Service Principal (for authentication)
- Application Insights (optional, for monitoring)

### **Configuration**

1. **Update appsettings.json**:
```json
{
  "AzureDigitalTwins": {
    "Endpoint": "https://your-digital-twin-instance.api.westus2.digitaltwins.azure.net"
  },
  "ApplicationInsights": {
    "InstrumentationKey": "your-app-insights-instrumentation-key"
  }
}
```

2. **Environment Variables**:
```bash
export AZURE_CLIENT_ID="your-service-principal-client-id"
export AZURE_CLIENT_SECRET="your-service-principal-secret"
export AZURE_TENANT_ID="your-tenant-id"
```

### **Installation**

```bash
cd services/digital_twin_management
dotnet restore
dotnet build
dotnet run
```

## 📚 API Documentation

### **Base URL**: `https://localhost:7000/api/DigitalTwin`

### **Endpoints**

#### **Warehouse Management**

**Create Warehouse Configuration**
```http
POST /api/DigitalTwin/warehouse/configuration
Content-Type: application/json

{
  "clientId": "warehouse-client-001",
  "warehouseName": "Main Distribution Center",
  "description": "Primary warehouse for client operations",
  "warehouseType": "Distribution",
  "totalArea": 50000,
  "zones": [
    {
      "name": "Receiving Zone",
      "zoneType": "Receiving",
      "area": 10000,
      "capacity": 100
    },
    {
      "name": "Picking Zone",
      "zoneType": "Picking",
      "area": 20000,
      "capacity": 200
    }
  ],
  "robots": [
    {
      "name": "Picker-001",
      "robotType": "Humanoid",
      "batteryPct": 100.0
    },
    {
      "name": "Transporter-001",
      "robotType": "AGV",
      "batteryPct": 95.0
    }
  ]
}
```

**Get Warehouse Configuration**
```http
GET /api/DigitalTwin/warehouse/{warehouseId}/configuration
```

**Update Warehouse Configuration**
```http
PUT /api/DigitalTwin/warehouse/{warehouseId}/configuration
Content-Type: application/json

{
  "clientId": "warehouse-client-001",
  "warehouseName": "Updated Distribution Center",
  "description": "Updated description",
  "warehouseType": "Distribution",
  "totalArea": 55000
}
```

#### **Zone Management**

**Create Zone**
```http
POST /api/DigitalTwin/warehouse/{warehouseId}/zones
Content-Type: application/json

{
  "id": "zone-new-001",
  "name": "Quality Control Zone",
  "zoneType": "QualityControl",
  "area": 5000,
  "capacity": 50
}
```

**Get Warehouse Zones**
```http
GET /api/DigitalTwin/warehouse/{warehouseId}/zones
```

**Get Zone Details**
```http
GET /api/DigitalTwin/warehouse/{warehouseId}/zones/{zoneId}
```

#### **Robot Management**

**Create Robot**
```http
POST /api/DigitalTwin/warehouse/{warehouseId}/zones/{zoneId}/robots
Content-Type: application/json

{
  "id": "robot-new-001",
  "name": "Inspector-001",
  "robotType": "Humanoid",
  "status": "Idle",
  "batteryPct": 85.0,
  "capabilities": ["inspection", "quality_control"],
  "location": {
    "x": 10.0,
    "y": 15.0,
    "z": 0.0,
    "floor": 1
  }
}
```

**Get Zone Robots**
```http
GET /api/DigitalTwin/warehouse/{warehouseId}/zones/{zoneId}/robots
```

**Update Robot Status**
```http
PUT /api/DigitalTwin/warehouse/{warehouseId}/zones/{zoneId}/robots/{robotId}/status
Content-Type: application/json

{
  "status": "Busy",
  "location": {
    "x": 25.0,
    "y": 30.0,
    "z": 0.0,
    "floor": 1
  }
}
```

#### **Query Operations**

**Custom Query**
```http
POST /api/DigitalTwin/query
Content-Type: application/json

"SELECT robot.* FROM DigitalTwins robot WHERE IS_OF_MODEL(robot, 'dtmi:boggssystems:warehouse:robot;1') AND robot.status = 'Idle'"
```

## 🏗️ Data Models

### **WarehouseDigitalTwin**
```csharp
public class WarehouseDigitalTwin
{
    public string Id { get; set; }
    public string Name { get; set; }
    public string Description { get; set; }
    public WarehouseType WarehouseType { get; set; }
    public WarehouseStatus Status { get; set; }
    public double TotalArea { get; set; }
    public List<Zone> Zones { get; set; }
    public List<RobotAsset> Robots { get; set; }
    // ... additional properties
}
```

### **Zone**
```csharp
public class Zone
{
    public string Id { get; set; }
    public string Name { get; set; }
    public WarehouseZoneType ZoneType { get; set; }
    public ZoneStatus Status { get; set; }
    public double Area { get; set; }
    public int Capacity { get; set; }
    public int CurrentOccupancy { get; set; }
    public List<BusinessRule> BusinessRules { get; set; }
    // ... additional properties
}
```

### **RobotAsset**
```csharp
public class RobotAsset
{
    public string Id { get; set; }
    public string Name { get; set; }
    public RobotType RobotType { get; set; }
    public RobotStatus Status { get; set; }
    public double BatteryPct { get; set; }
    public List<string> Capabilities { get; set; }
    public Location Location { get; set; }
    // ... additional properties
}
```

## 🔧 Development

### **Project Structure**
```
services/digital_twin_management/
├── Controllers/
│   └── DigitalTwinController.cs
├── Models/
│   └── WarehouseModels.cs
├── Services/
│   ├── DigitalTwinManager.cs
│   └── ConfigurationService.cs
├── Validators/
│   └── WarehouseValidators.cs
├── Program.cs
├── WarehouseDigitalTwin.csproj
├── appsettings.json
└── README.md
```

### **Running Locally**

```bash
# Install dependencies
dotnet restore

# Run the service
dotnet run

# View Swagger UI
open http://localhost:7000/swagger
```

### **Testing**

```bash
# Run unit tests
dotnet test

# Run with coverage
dotnet test --collect:"XPlat Code Coverage"
```

## 🔍 Monitoring & Logging

### **Application Insights**
- Automatic telemetry collection
- Performance monitoring
- Error tracking
- Dependency tracking

### **Serilog**
- Structured logging
- Console output
- Application Insights integration
- Log levels: Debug, Information, Warning, Error

### **Health Checks**
```http
GET /api/DigitalTwin/health
GET /health
```

## 🚀 Deployment

### **Docker**
```dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 80
EXPOSE 443

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["WarehouseDigitalTwin.csproj", "."]
RUN dotnet restore "./WarehouseDigitalTwin.csproj"
COPY . .
WORKDIR "/src/."
RUN dotnet build "WarehouseDigitalTwin.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "WarehouseDigitalTwin.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "WarehouseDigitalTwin.dll"]
```

### **Azure Container Apps**
```bash
# Build and push to Azure Container Registry
az acr build --registry your-registry --image warehouse-digital-twin .

# Deploy to Azure Container Apps
az containerapp create \
  --name warehouse-digital-twin \
  --resource-group your-resource-group \
  --image your-registry/warehouse-digital-twin:latest \
  --environment-vars AzureDigitalTwins__Endpoint=https://your-digital-twin-instance.api.westus2.digitaltwins.azure.net
```

## 🔧 Configuration

### **Environment Variables**
- `AzureDigitalTwins__Endpoint`: Azure Digital Twins instance URL
- `ApplicationInsights__InstrumentationKey`: Application Insights key
- `Logging__LogLevel__Default`: Default log level
- `AllowedHosts`: Allowed hostnames

### **Azure Authentication**
The service uses `DefaultAzureCredential` which supports multiple authentication methods:
- Environment variables
- Managed identity
- Visual Studio Code
- Azure CLI

## 📚 Integration Examples

### **Python Integration**
```python
import requests

# Create warehouse configuration
response = requests.post(
    "http://localhost:7000/api/DigitalTwin/warehouse/configuration",
    json={
        "clientId": "client-001",
        "warehouseName": "Test Warehouse",
        "warehouseType": "Distribution",
        "totalArea": 10000,
        "zones": [...],
        "robots": [...]
    }
)

result = response.json()
print(f"Warehouse created: {result['warehouseId']}")
```

### **JavaScript Integration**
```javascript
const response = await fetch('/api/DigitalTwin/warehouse/warehouse-001/configuration');
const configuration = await response.json();
console.log('Warehouse configuration:', configuration);
```

## 🎯 Next Steps

1. **Telemetry Processing**: Implement real-time telemetry ingestion
2. **Fleet Coordination**: Add robot orchestration capabilities
3. **Enterprise Integration**: Connect to WMS/ERP systems
4. **Python AI Integration**: Connect to Python AI services
5. **Advanced Analytics**: Add predictive maintenance and optimization

## 📞 Support

For questions or issues:
- Check the [API documentation](http://localhost:7000/swagger)
- Review the [implementation plan](../../IMPLEMENTATION_PLAN.md)
- Consult the [architecture documentation](../../WAREHOUSE_ARCHITECTURE.md)

---

*Service Version: 1.0.0*  
*Last Updated: 2026-03-23*
