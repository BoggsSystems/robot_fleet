# 🚀 Azure Robot Fleet Simulator Setup Guide

## **📋 Prerequisites**
- ✅ Azure Account with $200+ credits
- ✅ Resource Group: `robot-fleet-simulator-rg` (created)
- ✅ IoT Hub: `robot-fleet-hub` (created)

## **🔧 Step 1: Azure Portal Setup**

### **1.1 Access Azure Portal**
1. Go to: https://portal.azure.com
2. Login with `jeff_boggs@hotmail.com`
3. Navigate to **Resource Groups**
4. Select `robot-fleet-simulator-rg`

### **1.2 Create Storage Account**
1. Click **+ Create** → **Storage Account**
2. **Basics tab**:
   - **Resource group**: `robot-fleet-simulator-rg`
   - **Storage account name**: `robotfleetstorage2024` (must be unique)
   - **Region**: `East US`
   - **Performance**: Standard
   - **Redundancy**: Locally-redundant storage (LRS)
3. Click **Review + Create** → **Create**

### **1.3 Create Cosmos DB**
1. Click **+ Create** → **Azure Cosmos DB**
2. Select **Azure Cosmos DB for NoSQL**
3. **Basics tab**:
   - **Resource group**: `robot-fleet-simulator-rg`
   - **Account name**: `robot-fleet-cosmos`
   - **Location**: `East US`
   - **Capacity mode**: **Serverless**
4. **Configuration tab**:
   - **Consistency level**: Session
5. Click **Review + Create** → **Create**

### **1.4 Create Container App**
1. Click **+ Create** → **Container App**
2. **Basics tab**:
   - **Resource group**: `robot-fleet-simulator-rg`
   - **Container app name**: `robot-fleet-processor`
   - **Region**: `East US`
3. **Container tab**:
   - **Image source**: Custom
   - **Image**: `mcr.microsoft.com/k8se/quickstart-jobs:latest`
   - **CPU**: 0.5 cores
   - **Memory**: 1 Gi
4. Click **Review + Create** → **Create**

### **1.5 Create Digital Twins**
1. Click **+ Create** → **Digital Twins**
2. **Basics tab**:
   - **Resource group**: `robot-fleet-simulator-rg`
   - **Digital twins name**: `robot-fleet-digital-twins`
   - **Region**: `East US`
3. Click **Review + Create** → **Create**

## **🔗 Step 2: Get Connection Strings**

### **2.1 IoT Hub Connection String**
1. Go to **IoT Hub** → `robot-fleet-hub`
2. Click **Shared access policies**
3. Click **+ Add** → **iothubowner**
4. Select **Device connect** permission
5. Click **Create**
6. Click on the policy → **Copy connection string** (primary key)

### **2.2 Storage Connection String**
1. Go to **Storage Accounts** → `robotfleetstorage2024`
2. Click **Access keys**
3. Show keys → **Copy connection string** (key1)

### **2.3 Cosmos DB Connection String**
1. Go to **Azure Cosmos DB** → `robot-fleet-cosmos`
2. Click **Keys**
3. Copy **URI** and **PRIMARY KEY**

### **2.4 Digital Twins Endpoint**
1. Go to **Digital Twins** → `robot-fleet-digital-twins`
2. Copy **Host name** URL

## **🤖 Step 3: Device Provisioning**

### **3.1 Create Robot Devices in IoT Hub**
1. Go to **IoT Hub** → `robot-fleet-hub`
2. Click **IoT devices** → **+ Add**
3. Create 5 devices:
   - **Device ID**: `robot-001`, `robot-002`, `robot-003`, `robot-004`, `robot-005`
   - **Authentication type**: Symmetric key
   - **Auto-generate keys**: ✅
   - **Connect device to IoT hub**: ✅
4. Click **Save** for each device

### **3.2 Download Device Connection Strings**
1. For each device, click on it
2. Copy **Primary connection string**
3. Save these for the robot simulator

## **📊 Step 4: Configure Services**

### **4.1 Create Environment File**
Create `.env` file with connection details:

```bash
# Azure IoT Hub
IOT_HUB_CONNECTION_STRING="HostName=robot-fleet-hub.azure-devices.net;DeviceId=robot-001;SharedAccessKeyName=iothubowner;SharedAccessKey=YOUR_KEY"

# Azure Storage
STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=robotfleetstorage2024;AccountKey=YOUR_KEY;EndpointSuffix=core.windows.net"

# Cosmos DB
COSMOS_DB_ENDPOINT="https://robot-fleet-cosmos.documents.azure.com:443/"
COSMOS_DB_KEY="YOUR_PRIMARY_KEY"

# Digital Twins
DIGITAL_TWINS_ENDPOINT="https://robot-fleet-digital-twins.api.eastus.digitaltwins.azure.net"
```

### **4.2 Test Connections**
1. Test IoT Hub connectivity
2. Test Storage account access
3. Test Cosmos DB connection
4. Test Digital Twins endpoint

## **📈 Expected Costs (Monthly)**

| Service | Tier | Estimated Cost |
|----------|------|---------------|
| IoT Hub | S1 | ~$10 |
| Storage | Standard LRS | ~$5 |
| Cosmos DB | Serverless | ~$8 |
| Container App | 0.5 CPU, 1GB RAM | ~$15 |
| Digital Twins | S2 | ~$12 |
| **Total** | | **~$50/month** |

## **✅ Verification Checklist**

- [ ] Resource group created
- [ ] IoT Hub provisioned with 5 devices
- [ ] Storage account accessible
- [ ] Cosmos DB database created
- [ ] Container App running
- [ ] Digital Twins instance ready
- [ ] All connection strings saved
- [ ] End-to-end connectivity tested

## **🚀 Next Steps**

After completing these steps:
1. **Deploy robot simulator** with connection strings
2. **Test telemetry flow** from robots to cloud
3. **Verify data storage** in Cosmos DB
4. **Test Digital Twins** updates
5. **Create dashboard** for visualization

## **🔧 Troubleshooting**

### **Common Issues**
- **Device name conflicts**: Ensure unique device IDs
- **Connection string format**: Copy entire string without spaces
- **Region mismatches**: Use same region for all services
- **Permission errors**: Ensure proper RBAC permissions

### **Debug Commands**
```bash
# Test IoT Hub connection
az iot hub show-connection-string --name robot-fleet-hub

# Test Storage account
az storage account show-connection-string --name robotfleetstorage2024

# Test Cosmos DB
az cosmosdb keys list --name robot-fleet-cosmos
```

This setup provides the foundation for your robot fleet simulator with all required Azure services! 🎯
