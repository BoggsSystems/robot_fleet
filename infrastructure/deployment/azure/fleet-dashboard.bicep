@description('Name of the Container App')
param containerAppName string = 'robot-fleet-dashboard'

@description('Resource group name')
param resourceGroupName string = 'robot-fleet-simulator-rg'

@description('Location for all resources')
param location string = resourceGroup().location

@description('Container registry name')
param acrName string = 'kindmoss-6eac8399'

@description('Container image tag')
param imageTag string = 'latest'

@description('Environment name')
param environmentName string = 'robot-fleet-env'

@description('Application Insights name')
param appInsightsName string = '${containerAppName}-insights'

@description('Minimum replicas')
param minReplicas int = 1

@description('Maximum replicas')
param maxReplicas int = 3

@description('CPU cores')
param cpuCores string = '0.5'

@description('Memory in GB')
param memoryGi string = '1'

// Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    ApplicationId: containerAppName
  }
  tags: {
    app: containerAppName
    environment: 'production'
  }
}

// Container App
resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: containerAppName
  location: location
  properties: {
    managedEnvironmentId: resourceId('Microsoft.App/managedEnvironments', environmentName)
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 80
        allowInsecure: false
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
      }
      registries: [
        {
          server: '${acrName}.azurecr.io'
          username: acrUsername
          passwordSecretRef: 'acr-password'
        }
      ]
      secrets: [
        {
          name: 'acr-password'
          value: acrPassword
        }
        {
          name: 'app-insights-connection-string'
          value: appInsights.properties.ConnectionString
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'fleet-dashboard'
          image: '${acrName}.azurecr.io/fleet-dashboard:${imageTag}'
          resources: {
            cpu: json(cpuCores)
            memory: '${memoryGi}Gi'
          }
          env: [
            {
              name: 'NODE_ENV'
              value: 'production'
            }
            {
              name: 'REACT_APP_AUTH_URL'
              value: 'https://robotfleet-auth.kindmoss-6eac8399.eastus.azurecontainerapps.io'
            }
            {
              name: 'REACT_APP_API_URL'
              value: 'https://robotfleet-ai.kindmoss-6eac8399.eastus.azurecontainerapps.io'
            }
            {
              name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
              secretRef: 'app-insights-connection-string'
            }
          ]
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/'
                port: 80
              }
              initialDelaySeconds: 30
              periodSeconds: 10
              timeoutSeconds: 5
              failureThreshold: 3
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/'
                port: 80
              }
              initialDelaySeconds: 5
              periodSeconds: 5
              timeoutSeconds: 3
              failureThreshold: 3
            }
            {
              type: 'Startup'
              httpGet: {
                path: '/'
                port: 80
              }
              initialDelaySeconds: 10
              periodSeconds: 10
              timeoutSeconds: 5
              failureThreshold: 30
            }
          ]
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
        rules: [
          {
            name: 'http-scaling'
            custom: {
              type: 'http'
              metadata: {
                concurrentRequests: '10'
                concurrentRequestsPerInstance: '5'
              }
            }
          }
        ]
      }
    }
  }
  tags: {
    app: containerAppName
    environment: 'production'
    team: 'robot-fleet'
  }
}

@secure()
@description('ACR username')
param acrUsername string

@secure()
@description('ACR password')
param acrPassword string

// Output the Container App URL
output containerAppUrl string = containerApp.properties.configuration.ingress.fqdn

// Output the Application Insights Instrumentation Key
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey
