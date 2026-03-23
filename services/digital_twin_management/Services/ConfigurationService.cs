using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using System.Text.Json;
using WarehouseDigitalTwin.Models;
using FluentValidation;
using FluentValidation.Results;

namespace WarehouseDigitalTwin.Services;

/// <summary>
/// Service for managing warehouse configuration and client setup
/// </summary>
public class ConfigurationService
{
    private readonly ILogger<ConfigurationService> _logger;
    private readonly DigitalTwinManager _digitalTwinManager;
    private readonly IValidator<WarehouseDigitalTwin> _warehouseValidator;
    private readonly IValidator<Zone> _zoneValidator;
    private readonly IValidator<RobotAsset> _robotValidator;

    public ConfigurationService(
        ILogger<ConfigurationService> logger,
        DigitalTwinManager digitalTwinManager,
        IValidator<WarehouseDigitalTwin> warehouseValidator,
        IValidator<Zone> zoneValidator,
        IValidator<RobotAsset> robotValidator)
    {
        _logger = logger;
        _digitalTwinManager = digitalTwinManager;
        _warehouseValidator = warehouseValidator;
        _zoneValidator = zoneValidator;
        _robotValidator = robotValidator;
    }

    /// <summary>
    /// Creates a complete warehouse configuration from client input
    /// </summary>
    public async Task<ConfigurationResult> CreateWarehouseConfigurationAsync(WarehouseConfigurationRequest request)
    {
        try
        {
            _logger.LogInformation("Creating warehouse configuration for client: {ClientId}", request.ClientId);

            // Validate request
            var validationResult = await ValidateConfigurationRequestAsync(request);
            if (!validationResult.IsValid)
            {
                return new ConfigurationResult
                {
                    Success = false,
                    Errors = validationResult.Errors.Select(e => e.ErrorMessage).ToList()
                };
            }

            // Create warehouse model
            var warehouse = CreateWarehouseModel(request);
            var zones = CreateZoneModels(request);
            var robots = CreateRobotModels(request);

            // Validate all models
            var warehouseValidation = await _warehouseValidator.ValidateAsync(warehouse);
            if (!warehouseValidation.IsValid)
            {
                return new ConfigurationResult
                {
                    Success = false,
                    Errors = warehouseValidation.Errors.Select(e => e.ErrorMessage).ToList()
                };
            }

            // Create digital twins
            var warehouseId = await _digitalTwinManager.CreateCompleteWarehouseModelAsync(warehouse, zones, robots);

            _logger.LogInformation("Successfully created warehouse configuration: {WarehouseId}", warehouseId);

            return new ConfigurationResult
            {
                Success = true,
                WarehouseId = warehouseId,
                CreatedZones = zones.Select(z => z.Id).ToList(),
                CreatedRobots = robots.Select(r => r.Id).ToList()
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to create warehouse configuration for client: {ClientId}", request.ClientId);
            return new ConfigurationResult
            {
                Success = false,
                Errors = new List<string> { $"Configuration failed: {ex.Message}" }
            };
        }
    }

    /// <summary>
    /// Updates warehouse configuration
    /// </summary>
    public async Task<ConfigurationResult> UpdateWarehouseConfigurationAsync(string warehouseId, WarehouseConfigurationRequest request)
    {
        try
        {
            _logger.LogInformation("Updating warehouse configuration: {WarehouseId}", warehouseId);

            // Get existing warehouse
            var existingWarehouse = await _digitalTwinManager.GetDigitalTwinAsync<WarehouseDigitalTwin>(warehouseId);
            if (existingWarehouse == null)
            {
                return new ConfigurationResult
                {
                    Success = false,
                    Errors = new List<string> { "Warehouse not found" }
                };
            }

            // Validate request
            var validationResult = await ValidateConfigurationRequestAsync(request);
            if (!validationResult.IsValid)
            {
                return new ConfigurationResult
                {
                    Success = false,
                    Errors = validationResult.Errors.Select(e => e.ErrorMessage).ToList()
                };
            }

            // Update warehouse properties
            var updates = new Dictionary<string, object>
            {
                ["name"] = request.WarehouseName,
                ["description"] = request.Description,
                ["lastUpdated"] = DateTime.UtcNow
            };

            await _digitalTwinManager.UpdateDigitalTwinAsync(warehouseId, updates);

            _logger.LogInformation("Successfully updated warehouse configuration: {WarehouseId}", warehouseId);

            return new ConfigurationResult
            {
                Success = true,
                WarehouseId = warehouseId
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to update warehouse configuration: {WarehouseId}", warehouseId);
            return new ConfigurationResult
            {
                Success = false,
                Errors = new List<string> { $"Update failed: {ex.Message}" }
            };
        }
    }

    /// <summary>
    /// Gets warehouse configuration summary
    /// </summary>
    public async Task<WarehouseConfigurationSummary?> GetWarehouseConfigurationAsync(string warehouseId)
    {
        try
        {
            _logger.LogInformation("Getting warehouse configuration: {WarehouseId}", warehouseId);

            var warehouse = await _digitalTwinManager.GetDigitalTwinAsync<WarehouseDigitalTwin>(warehouseId);
            if (warehouse == null)
            {
                return null;
            }

            var zones = await _digitalTwinManager.GetWarehouseZonesAsync(warehouseId);
            var robots = new List<RobotAsset>();

            foreach (var zone in zones)
            {
                var zoneRobots = await _digitalTwinManager.GetZoneRobotsAsync(zone.Id);
                robots.AddRange(zoneRobots);
            }

            return new WarehouseConfigurationSummary
            {
                Warehouse = warehouse,
                Zones = zones,
                Robots = robots,
                TotalRobots = robots.Count,
                ActiveRobots = robots.Count(r => r.Status == RobotStatus.Idle || r.Status == RobotStatus.Busy),
                ZonesByType = zones.GroupBy(z => z.ZoneType).ToDictionary(g => g.Key, g => g.Count()),
                RobotsByType = robots.GroupBy(r => r.RobotType).ToDictionary(g => g.Key, g => g.Count())
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get warehouse configuration: {WarehouseId}", warehouseId);
            throw;
        }
    }

    /// <summary>
    /// Validates configuration request
    /// </summary>
    private async Task<ValidationResult> ValidateConfigurationRequestAsync(WarehouseConfigurationRequest request)
    {
        var validationResult = new ValidationResult();

        // Basic validation
        if (string.IsNullOrWhiteSpace(request.WarehouseName))
        {
            validationResult.Errors.Add(new ValidationFailure("WarehouseName", "Warehouse name is required"));
        }

        if (string.IsNullOrWhiteSpace(request.ClientId))
        {
            validationResult.Errors.Add(new ValidationFailure("ClientId", "Client ID is required"));
        }

        if (request.Zones == null || !request.Zones.Any())
        {
            validationResult.Errors.Add(new ValidationFailure("Zones", "At least one zone is required"));
        }

        if (request.Robots == null || !request.Robots.Any())
        {
            validationResult.Errors.Add(new ValidationFailure("Robots", "At least one robot is required"));
        }

        // Validate zone configurations
        if (request.Zones != null)
        {
            foreach (var zone in request.Zones)
            {
                if (string.IsNullOrWhiteSpace(zone.Name))
                {
                    validationResult.Errors.Add(new ValidationFailure("Zone.Name", "Zone name is required"));
                }

                if (zone.Area <= 0)
                {
                    validationResult.Errors.Add(new ValidationFailure("Zone.Area", "Zone area must be greater than 0"));
                }
            }
        }

        // Validate robot configurations
        if (request.Robots != null)
        {
            foreach (var robot in request.Robots)
            {
                if (string.IsNullOrWhiteSpace(robot.Name))
                {
                    validationResult.Errors.Add(new ValidationFailure("Robot.Name", "Robot name is required"));
                }

                if (robot.BatteryPct < 0 || robot.BatteryPct > 100)
                {
                    validationResult.Errors.Add(new ValidationFailure("Robot.BatteryPct", "Battery percentage must be between 0 and 100"));
                }
            }
        }

        return validationResult;
    }

    /// <summary>
    /// Creates warehouse model from configuration request
    /// </summary>
    private WarehouseDigitalTwin CreateWarehouseModel(WarehouseConfigurationRequest request)
    {
        return new WarehouseDigitalTwin
        {
            Id = $"warehouse-{request.ClientId}-{Guid.NewGuid():N}",
            Name = request.WarehouseName,
            Description = request.Description ?? $"Warehouse for client {request.ClientId}",
            WarehouseType = request.WarehouseType,
            Status = WarehouseStatus.Active,
            TotalArea = request.TotalArea,
            LastUpdated = DateTime.UtcNow,
            Metadata = new Dictionary<string, object>
            {
                ["clientId"] = request.ClientId,
                ["createdBy"] = "ConfigurationService",
                ["configurationVersion"] = "1.0"
            }
        };
    }

    /// <summary>
    /// Creates zone models from configuration request
    /// </summary>
    private List<Zone> CreateZoneModels(WarehouseConfigurationRequest request)
    {
        var zones = new List<Zone>();

        foreach (var zoneRequest in request.Zones)
        {
            var zone = new Zone
            {
                Id = $"zone-{Guid.NewGuid():N}",
                Name = zoneRequest.Name,
                ZoneType = zoneRequest.ZoneType,
                Status = ZoneStatus.Active,
                Area = zoneRequest.Area,
                Capacity = zoneRequest.Capacity,
                CurrentOccupancy = 0,
                Temperature = 20.0, // Default temperature
                Humidity = 45.0, // Default humidity
                BusinessRules = CreateBusinessRules(zoneRequest.ZoneType),
                LastUpdated = DateTime.UtcNow
            };

            zones.Add(zone);
        }

        return zones;
    }

    /// <summary>
    /// Creates robot models from configuration request
    /// </summary>
    private List<RobotAsset> CreateRobotModels(WarehouseConfigurationRequest request)
    {
        var robots = new List<RobotAsset>();

        foreach (var robotRequest in request.Robots)
        {
            var robot = new RobotAsset
            {
                Id = $"robot-{Guid.NewGuid():N}",
                Name = robotRequest.Name,
                RobotType = robotRequest.RobotType,
                Status = RobotStatus.Idle,
                BatteryPct = robotRequest.BatteryPct,
                CurrentZoneId = request.Zones.FirstOrDefault()?.Id, // Assign to first zone for now
                Capabilities = GetRobotCapabilities(robotRequest.RobotType),
                Location = new Location { X = 0, Y = 0, Z = 0 },
                HealthStatus = HealthStatus.Healthy,
                LastUpdated = DateTime.UtcNow
            };

            robots.Add(robot);
        }

        return robots;
    }

    /// <summary>
    /// Creates default business rules for a zone type
    /// </summary>
    private List<BusinessRule> CreateBusinessRules(WarehouseZoneType zoneType)
    {
        return zoneType switch
        {
            WarehouseZoneType.Receiving => new List<BusinessRule>
            {
                new BusinessRule
                {
                    RuleId = "receiving-capacity",
                    Name = "Receiving Capacity Limit",
                    Description = "Prevent overloading receiving zone",
                    RuleType = BusinessRuleType.Operational,
                    Priority = RulePriority.High,
                    Conditions = new List<RuleCondition>
                    {
                        new RuleCondition { Property = "currentOccupancy", Operator = ">", Value = 80 }
                    },
                    Actions = new List<RuleAction>
                    {
                        new RuleAction 
                        { 
                            ActionType = "alert", 
                            Parameters = new Dictionary<string, object>
                            {
                                ["message"] = "Receiving zone approaching capacity limit",
                                ["severity"] = "warning"
                            }
                        }
                    }
                }
            },
            WarehouseZoneType.Charging => new List<BusinessRule>
            {
                new BusinessRule
                {
                    RuleId = "charging-station-availability",
                    Name = "Charging Station Availability",
                    Description = "Ensure charging stations are available",
                    RuleType = BusinessRuleType.Operational,
                    Priority = RulePriority.Medium,
                    Conditions = new List<RuleCondition>
                    {
                        new RuleCondition { Property = "availableChargingStations", Operator = "<", Value = 2 }
                    },
                    Actions = new List<RuleAction>
                    {
                        new RuleAction 
                        { 
                            ActionType = "reallocate", 
                            Parameters = new Dictionary<string, object>
                            {
                                ["robotType"] = "AGV",
                                ["priority"] = "low"
                            }
                        }
                    }
                }
            },
            _ => new List<BusinessRule>()
        };
    }

    /// <summary>
    /// Gets default capabilities for robot type
    /// </summary>
    private List<string> GetRobotCapabilities(RobotType robotType)
    {
        return robotType switch
        {
            RobotType.Humanoid => new List<string> { "picking", "packing", "manipulation", "inspection" },
            RobotType.Quadruped => new List<string> { "patrol", "inspection", "transport", "navigation" },
            RobotType.AGV => new List<string> { "transport", "pallet_handling", "conveyor_integration" },
            RobotType.Drone => new List<string> { "inventory_count", "inspection", "surveillance" },
            RobotType.Fixed => new List<string> { "stationary_task", "quality_control" },
            _ => new List<string>()
        };
    }
}

/// <summary>
/// Request model for warehouse configuration
/// </summary>
public class WarehouseConfigurationRequest
{
    public string ClientId { get; set; } = string.Empty;
    public string WarehouseName { get; set; } = string.Empty;
    public string? Description { get; set; }
    public WarehouseType WarehouseType { get; set; }
    public double TotalArea { get; set; }
    public List<ZoneConfiguration> Zones { get; set; } = new();
    public List<RobotConfiguration> Robots { get; set; } = new();
}

/// <summary>
/// Zone configuration model
/// </summary>
public class ZoneConfiguration
{
    public string Name { get; set; } = string.Empty;
    public WarehouseZoneType ZoneType { get; set; }
    public double Area { get; set; }
    public int Capacity { get; set; }
}

/// <summary>
/// Robot configuration model
/// </summary>
public class RobotConfiguration
{
    public string Name { get; set; } = string.Empty;
    public RobotType RobotType { get; set; }
    public double BatteryPct { get; set; } = 100.0;
}

/// <summary>
/// Result of warehouse configuration operation
/// </summary>
public class ConfigurationResult
{
    public bool Success { get; set; }
    public string? WarehouseId { get; set; }
    public List<string> CreatedZones { get; set; } = new();
    public List<string> CreatedRobots { get; set; } = new();
    public List<string> Errors { get; set; } = new();
}

/// <summary>
/// Summary of warehouse configuration
/// </summary>
public class WarehouseConfigurationSummary
{
    public WarehouseDigitalTwin Warehouse { get; set; } = new();
    public List<Zone> Zones { get; set; } = new();
    public List<RobotAsset> Robots { get; set; } = new();
    public int TotalRobots { get; set; }
    public int ActiveRobots { get; set; }
    public Dictionary<WarehouseZoneType, int> ZonesByType { get; set; } = new();
    public Dictionary<RobotType, int> RobotsByType { get; set; } = new();
}
