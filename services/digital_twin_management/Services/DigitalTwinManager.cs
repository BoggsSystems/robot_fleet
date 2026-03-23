using Azure;
using Azure.DigitalTwins.Core;
using Azure.Identity;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using System.Text.Json;
using WarehouseDigitalTwin.Models;

namespace WarehouseDigitalTwin.Services;

/// <summary>
/// Core service for managing Azure Digital Twins for warehouse operations
/// </summary>
public class DigitalTwinManager
{
    private readonly DigitalTwinsClient _digitalTwinsClient;
    private readonly ILogger<DigitalTwinManager> _logger;
    private readonly IConfiguration _configuration;
    private readonly string _adtEndpoint;

    public DigitalTwinManager(
        ILogger<DigitalTwinManager> logger,
        IConfiguration configuration)
    {
        _logger = logger;
        _configuration = configuration;
        _adtEndpoint = configuration["AzureDigitalTwins:Endpoint"] 
            ?? throw new ArgumentNullException("Azure Digital Twins endpoint not configured");

        try
        {
            var credential = new DefaultAzureCredential();
            _digitalTwinsClient = new DigitalTwinsClient(new Uri(_adtEndpoint), credential);
            _logger.LogInformation("Digital Twins client initialized for endpoint: {Endpoint}", _adtEndpoint);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to initialize Digital Twins client");
            throw;
        }
    }

    /// <summary>
    /// Creates a new warehouse digital twin
    /// </summary>
    public async Task<string> CreateWarehouseAsync(WarehouseDigitalTwin warehouse)
    {
        try
        {
            _logger.LogInformation("Creating warehouse digital twin: {WarehouseId}", warehouse.Id);

            // Create the digital twin
            var twinData = JsonSerializer.SerializeToNode(warehouse);
            var createdTwin = await _digitalTwinsClient.CreateOrReplaceDigitalTwinAsync(
                warehouse.Id, twinData);

            _logger.LogInformation("Successfully created warehouse digital twin: {WarehouseId}", warehouse.Id);
            return createdTwin.Value.Id;
        }
        catch (RequestFailedException ex)
        {
            _logger.LogError(ex, "Failed to create warehouse digital twin: {WarehouseId}", warehouse.Id);
            throw new DigitalTwinException($"Failed to create warehouse digital twin: {ex.Message}", ex);
        }
    }

    /// <summary>
    /// Creates a new zone digital twin and establishes relationship with warehouse
    /// </summary>
    public async Task<string> CreateZoneAsync(Zone zone, string warehouseId)
    {
        try
        {
            _logger.LogInformation("Creating zone digital twin: {ZoneId} for warehouse: {WarehouseId}", 
                zone.Id, warehouseId);

            // Create the zone twin
            var zoneData = JsonSerializer.SerializeToNode(zone);
            var createdZone = await _digitalTwinsClient.CreateOrReplaceDigitalTwinAsync(
                zone.Id, zoneData);

            // Create relationship to warehouse
            var relationship = new BasicRelationship
            {
                TargetId = zone.Id,
                Name = "containsZone"
            };

            await _digitalTwinsClient.CreateOrReplaceRelationshipAsync(
                warehouseId, $"{warehouseId}_contains_{zone.Id}", relationship);

            _logger.LogInformation("Successfully created zone digital twin: {ZoneId}", zone.Id);
            return createdZone.Value.Id;
        }
        catch (RequestFailedException ex)
        {
            _logger.LogError(ex, "Failed to create zone digital twin: {ZoneId}", zone.Id);
            throw new DigitalTwinException($"Failed to create zone digital twin: {ex.Message}", ex);
        }
    }

    /// <summary>
    /// Creates a new robot digital twin and establishes relationship with zone
    /// </summary>
    public async Task<string> CreateRobotAsync(RobotAsset robot, string zoneId)
    {
        try
        {
            _logger.LogInformation("Creating robot digital twin: {RobotId} for zone: {ZoneId}", 
                robot.Id, zoneId);

            // Create the robot twin
            var robotData = JsonSerializer.SerializeToNode(robot);
            var createdRobot = await _digitalTwinsClient.CreateOrReplaceDigitalTwinAsync(
                robot.Id, robotData);

            // Create relationship to zone
            var relationship = new BasicRelationship
            {
                TargetId = robot.Id,
                Name = "containsRobot"
            };

            await _digitalTwinsClient.CreateOrReplaceRelationshipAsync(
                zoneId, $"{zoneId}_contains_{robot.Id}", relationship);

            _logger.LogInformation("Successfully created robot digital twin: {RobotId}", robot.Id);
            return createdRobot.Value.Id;
        }
        catch (RequestFailedException ex)
        {
            _logger.LogError(ex, "Failed to create robot digital twin: {RobotId}", robot.Id);
            throw new DigitalTwinException($"Failed to create robot digital twin: {ex.Message}", ex);
        }
    }

    /// <summary>
    /// Updates a digital twin's properties
    /// </summary>
    public async Task UpdateDigitalTwinAsync(string twinId, Dictionary<string, object> properties)
    {
        try
        {
            _logger.LogInformation("Updating digital twin: {TwinId}", twinId);

            var updateOperations = properties.Select(kvp => 
                new UpdateOperation("replace", $"/{kvp.Key}", kvp.Value)).ToList();

            await _digitalTwinsClient.UpdateDigitalTwinAsync(twinId, updateOperations);

            _logger.LogInformation("Successfully updated digital twin: {TwinId}", twinId);
        }
        catch (RequestFailedException ex)
        {
            _logger.LogError(ex, "Failed to update digital twin: {TwinId}", twinId);
            throw new DigitalTwinException($"Failed to update digital twin: {ex.Message}", ex);
        }
    }

    /// <summary>
    /// Gets a digital twin by ID
    /// </summary>
    public async Task<T?> GetDigitalTwinAsync<T>(string twinId) where T : class
    {
        try
        {
            _logger.LogInformation("Getting digital twin: {TwinId}", twinId);

            var twin = await _digitalTwinsClient.GetDigitalTwinAsync<BasicDigitalTwin>(twinId);
            
            if (twin == null)
            {
                _logger.LogWarning("Digital twin not found: {TwinId}", twinId);
                return null;
            }

            var twinJson = JsonSerializer.Serialize(twin);
            var result = JsonSerializer.Deserialize<T>(twinJson);

            _logger.LogInformation("Successfully retrieved digital twin: {TwinId}", twinId);
            return result;
        }
        catch (RequestFailedException ex)
        {
            _logger.LogError(ex, "Failed to get digital twin: {TwinId}", twinId);
            throw new DigitalTwinException($"Failed to get digital twin: {ex.Message}", ex);
        }
    }

    /// <summary>
    /// Queries digital twins using the Azure Digital Twins query language
    /// </summary>
    public async Task<List<T>> QueryDigitalTwinsAsync<T>(string query) where T : class
    {
        try
        {
            _logger.LogInformation("Querying digital twins with query: {Query}", query);

            var queryResult = await _digitalTwinsClient.QueryAsync<BasicDigitalTwin>(query);
            var results = new List<T>();

            await foreach (var twin in queryResult)
            {
                var twinJson = JsonSerializer.Serialize(twin);
                var result = JsonSerializer.Deserialize<T>(twinJson);
                if (result != null)
                {
                    results.Add(result);
                }
            }

            _logger.LogInformation("Query returned {Count} results", results.Count);
            return results;
        }
        catch (RequestFailedException ex)
        {
            _logger.LogError(ex, "Failed to query digital twins with query: {Query}", query);
            throw new DigitalTwinException($"Failed to query digital twins: {ex.Message}", ex);
        }
    }

    /// <summary>
    /// Deletes a digital twin
    /// </summary>
    public async Task DeleteDigitalTwinAsync(string twinId)
    {
        try
        {
            _logger.LogInformation("Deleting digital twin: {TwinId}", twinId);

            await _digitalTwinsClient.DeleteDigitalTwinAsync(twinId);

            _logger.LogInformation("Successfully deleted digital twin: {TwinId}", twinId);
        }
        catch (RequestFailedException ex)
        {
            _logger.LogError(ex, "Failed to delete digital twin: {TwinId}", twinId);
            throw new DigitalTwinException($"Failed to delete digital twin: {ex.Message}", ex);
        }
    }

    /// <summary>
    /// Gets all zones for a warehouse
    /// </summary>
    public async Task<List<Zone>> GetWarehouseZonesAsync(string warehouseId)
    {
        try
        {
            var query = $"SELECT zone.* FROM DigitalTwins zone WHERE IS_OF_MODEL(zone, 'dtmi:boggssystems:warehouse:zone;1') AND zone.$metadata.$target IN (SELECT containsZone.targetId FROM DigitalTwins warehouse JOIN containsZone ON warehouse WHERE warehouse.$dtId = '{warehouseId}')";
            
            return await QueryDigitalTwinsAsync<Zone>(query);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get zones for warehouse: {WarehouseId}", warehouseId);
            throw new DigitalTwinException($"Failed to get warehouse zones: {ex.Message}", ex);
        }
    }

    /// <summary>
    /// Gets all robots in a zone
    /// </summary>
    public async Task<List<RobotAsset>> GetZoneRobotsAsync(string zoneId)
    {
        try
        {
            var query = $"SELECT robot.* FROM DigitalTwins robot WHERE IS_OF_MODEL(robot, 'dtmi:boggssystems:warehouse:robot;1') AND robot.$metadata.$target IN (SELECT containsRobot.targetId FROM DigitalTwins zone JOIN containsRobot ON zone WHERE zone.$dtId = '{zoneId}')";
            
            return await QueryDigitalTwinsAsync<RobotAsset>(query);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get robots for zone: {ZoneId}", zoneId);
            throw new DigitalTwinException($"Failed to get zone robots: {ex.Message}", ex);
        }
    }

    /// <summary>
    /// Updates robot location and status
    /// </summary>
    public async Task UpdateRobotStatusAsync(string robotId, RobotStatus status, Location? location = null)
    {
        try
        {
            var updates = new Dictionary<string, object>
            {
                ["status"] = status.ToString(),
                ["lastUpdated"] = DateTime.UtcNow
            };

            if (location != null)
            {
                updates["location"] = location;
            }

            await UpdateDigitalTwinAsync(robotId, updates);
            
            _logger.LogInformation("Updated robot {RobotId} status to {Status}", robotId, status);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to update robot status: {RobotId}", robotId);
            throw new DigitalTwinException($"Failed to update robot status: {ex.Message}", ex);
        }
    }

    /// <summary>
    /// Creates a complete warehouse model with zones and robots
    /// </summary>
    public async Task<string> CreateCompleteWarehouseModelAsync(WarehouseDigitalTwin warehouse, List<Zone> zones, List<RobotAsset> robots)
    {
        try
        {
            _logger.LogInformation("Creating complete warehouse model: {WarehouseId}", warehouse.Id);

            // Create warehouse
            await CreateWarehouseAsync(warehouse);

            // Create zones
            foreach (var zone in zones)
            {
                await CreateZoneAsync(zone, warehouse.Id);
                
                // Create robots for this zone
                var zoneRobots = robots.Where(r => r.CurrentZoneId == zone.Id).ToList();
                foreach (var robot in zoneRobots)
                {
                    await CreateRobotAsync(robot, zone.Id);
                }
            }

            _logger.LogInformation("Successfully created complete warehouse model: {WarehouseId}", warehouse.Id);
            return warehouse.Id;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to create complete warehouse model: {WarehouseId}", warehouse.Id);
            throw new DigitalTwinException($"Failed to create complete warehouse model: {ex.Message}", ex);
        }
    }
}

/// <summary>
/// Custom exception for Digital Twin operations
/// </summary>
public class DigitalTwinException : Exception
{
    public DigitalTwinException(string message) : base(message) { }
    public DigitalTwinException(string message, Exception innerException) : base(message, innerException) { }
}
