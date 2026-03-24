# 🔗 Azure OpenAI Setup Guide

## 🎯 Current Status
- ✅ Azure OpenAI Resource Created: `warehouse-ai-openai`
- ✅ API Key Configured: Secure secret management
- ✅ AI Engine Integration: Ready with fallback
- ⚠️ Model Deployment: Needs quota request
- ✅ Fallback System: Pattern matching working

## 🚀 Step-by-Step Setup

### Step 1: Request Quota (Required for GPT Models)

#### Option A: Azure Portal (Recommended)
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Azure OpenAI resource
3. Click "Deployments" → "Create new deployment"
4. Select model:
   - **GPT-5.1-chat** (Latest, most capable)
   - **GPT-35-turbo** (Faster, cheaper)
5. Set capacity to 1-10 tokens/minute
6. Submit quota request (usually approved within hours)

#### Option B: CLI Command
```bash
# Request quota for GPT-5
az cognitiveservices account deployment create \
  --name warehouse-ai-openai \
  --resource-group robot-fleet-simulator-rg \
  --deployment-name gpt-5-chat \
  --model-name gpt-5.1-chat \
  --model-version "2025-11-13" \
  --model-format OpenAI \
  --sku-name "GlobalStandard" \
  --capacity 1

# Alternative: GPT-35-turbo (more likely to be approved)
az cognitiveservices account deployment create \
  --name warehouse-ai-openai \
  --resource-group robot-fleet-simulator-rg \
  --deployment-name gpt-35-turbo \
  --model-name gpt-35-turbo \
  --model-version "1106" \
  --model-format OpenAI \
  --sku-name "Standard" \
  --capacity 1
```

### Step 2: Update Deployment Configuration

Once model is deployed, update the container app:
```bash
# Update deployment name in environment
az containerapp update \
  --name warehouse-ai-engine \
  --resource-group robot-fleet-simulator-rg \
  --set-env-vars AZURE_OPENAI_DEPLOYMENT=gpt-5-chat
```

### Step 3: Verify AI Integration

Test the AI-powered DTDL generator:
```bash
# Test with complex natural language
curl -X POST "https://warehouse-ai-engine.kindmoss-6eac8399.eastus.azurecontainerapps.io/api/dtdl/conversation" \
-H "Content-Type: application/json" \
-d '{
  "user_input": "Create a sophisticated warehouse digital twin that tracks inventory levels, monitors environmental conditions, manages robot fleet operations with predictive maintenance capabilities, and provides real-time analytics for operational efficiency.",
  "model_type": "warehouse"
}' | jq '.ai_method, .validation.valid'
```

## 🎯 Alternative AI Services

If Azure OpenAI quota is delayed, consider these options:

### Option 1: Azure AI Language Service
```bash
# Create Azure AI Language Service
az cognitiveservices account create \
  --name warehouse-language-service \
  --resource-group robot-fleet-simulator-rg \
  --kind TextAnalytics \
  --sku S0 \
  --location eastus

# Get API key
az cognitiveservices account keys list \
  --name warehouse-language-service \
  --resource-group robot-fleet-simulator-rg
```

### Option 2: Azure AI Studio
1. Go to [Azure AI Studio](https://ai.azure.com)
2. Create a new project
3. Deploy GPT models directly
4. Get endpoint and key
5. Update container app configuration

### Option 3: Enhanced Pattern Matching
Improve the existing pattern-based system:
```python
# Add more sophisticated patterns
enhanced_patterns = {
    "inventory": ["inventory", "stock", "items", "products"],
    "monitoring": ["monitor", "track", "observe", "measure"],
    "robot_fleet": ["robot fleet", "robots", "automation", "fleet"],
    "predictive": ["predictive", "forecast", "anticipate"],
    "maintenance": ["maintenance", "upkeep", "service", "repair"]
}
```

## 🔧 Configuration Details

### Current Azure OpenAI Resource
- **Name**: warehouse-ai-openai
- **Endpoint**: https://warehouse-ai-openai.openai.azure.com/
- **Location**: East US
- **SKU**: S0 (Standard)
- **Status**: Active

### API Configuration
```json
{
  "AZURE_OPENAI_API_KEY": "a78082c44a6e48fcb3fdfba3d0c0350f",
  "AZURE_OPENAI_ENDPOINT": "https://warehouse-ai-openai.openai.azure.com/",
  "AZURE_OPENAI_DEPLOYMENT": "gpt-5-chat" (to be set)
}
```

### Container App Environment
```bash
# Current configuration
az containerapp show \
  --name warehouse-ai-engine \
  --resource-group robot-fleet-simulator-rg \
  --query "properties.configuration.env"
```

## 🧪 Testing the System

### 1. Test Pattern Matching (Working Now)
```bash
# Simple pattern that works
curl -X POST "https://warehouse-ai-engine.kindmoss-6eac8399.eastus.azurecontainerapps.io/api/dtdl/conversation" \
-H "Content-Type: application/json" \
-d '{
  "user_input": "warehouse should have name property and total area property. warehouse contains zones.",
  "model_type": "warehouse"
}'
```

### 2. Test AI Integration (After Model Deployment)
```bash
# Complex natural language
curl -X POST "https://warehouse-ai-engine.kindmoss-6eac8399.eastus.azurecontainerapps.io/api/dtdl/conversation" \
-H "Content-Type: application/json" \
-d '{
  "user_input": "Design an advanced warehouse digital twin with real-time inventory tracking, environmental monitoring, predictive maintenance, and AI-driven optimization.",
  "model_type": "warehouse"
}'
```

## 🎯 Expected Results

### With AI (GPT-5):
- **Natural Language Understanding**: Complex descriptions
- **Intelligent Entity Extraction**: Context-aware parsing
- **Smart DTDL Generation**: Complete models
- **AI Suggestions**: Intelligent improvements
- **Best Practices**: Industry standards

### With Pattern Matching (Current):
- **Structured Input**: Specific patterns required
- **Basic Entity Extraction**: Limited complexity
- **Template Generation**: Predefined models
- **Rule-Based Suggestions**: Simple recommendations

## 🚀 Next Steps

1. **Request Quota**: Use Azure Portal or CLI
2. **Deploy Model**: GPT-5.1-chat recommended
3. **Update Configuration**: Set deployment name
4. **Test Integration**: Verify AI functionality
5. **Enhance Patterns**: Improve fallback system

## 📞 Support

For quota issues:
- **Azure Support**: Create support ticket in Azure Portal
- **Documentation**: [Azure OpenAI Quota Guide](https://learn.microsoft.com/en-us/azure/ai-services/openai/quotas-limits)
- **Community**: [Microsoft Q&A](https://learn.microsoft.com/en-us/answers/questions/)

The system is ready to use AI as soon as quota is approved! 🎉
