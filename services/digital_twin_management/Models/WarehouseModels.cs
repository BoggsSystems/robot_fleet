using System.Text.Json.Serialization;

namespace WarehouseDigitalTwin.Models;

/// <summary>
/// Core warehouse digital twin model representing the complete warehouse state
/// </summary>
public class WarehouseDigitalTwin
{
    [JsonPropertyName("$dtId")]
    public string Id { get; set; } = string.Empty;
    
    [JsonPropertyName("$dtId")]
    public string ModelId { get; set; } = "dtmi:boggssystems:warehouse:digital:warehouse;1";
    
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;
    
    [JsonPropertyName("description")]
    public string Description { get; set; } = string.Empty;
    
    [JsonPropertyName("warehouseType")]
    public WarehouseType WarehouseType { get; set; }
    
    [JsonPropertyName("status")]
    public WarehouseStatus Status { get; set; }
    
    [JsonPropertyName("totalArea")]
    public double TotalArea { get; set; }
    
    [JsonPropertyName("zones")]
    public List<Zone> Zones { get; set; } = new();
    
    [JsonPropertyName("robots")]
    public List<RobotAsset> Robots { get; set; } = new();
    
    [JsonPropertyName("workstations")]
    public List<Workstation> Workstations { get; set; } = new();
    
    [JsonPropertyName("conveyors")]
    public List<Conveyor> Conveyors { get; set; } = new();
    
    [JsonPropertyName("dockingBays")]
    public List<DockingBay> DockingBays { get; set; } = new();
    
    [JsonPropertyName("lastUpdated")]
    public DateTime LastUpdated { get; set; } = DateTime.UtcNow;
    
    [JsonPropertyName("metadata")]
    public Dictionary<string, object> Metadata { get; set; } = new();
}

/// <summary>
/// Represents a warehouse zone with specific operational characteristics
/// </summary>
public class Zone
{
    [JsonPropertyName("$dtId")]
    public string Id { get; set; } = string.Empty;
    
    [JsonPropertyName("$dtId")]
    public string ModelId { get; set; } = "dtmi:boggssystems:warehouse:zone;1";
    
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;
    
    [JsonPropertyName("zoneType")]
    public WarehouseZoneType ZoneType { get; set; }
    
    [JsonPropertyName("status")]
    public ZoneStatus Status { get; set; }
    
    [JsonPropertyName("area")]
    public double Area { get; set; }
    
    [JsonPropertyName("capacity")]
    public int Capacity { get; set; }
    
    [JsonPropertyName("currentOccupancy")]
    public int CurrentOccupancy { get; set; }
    
    [JsonPropertyName("temperature")]
    public double Temperature { get; set; }
    
    [JsonPropertyName("humidity")]
    public double Humidity { get; set; }
    
    [JsonPropertyName("containsLocations")]
    public List<string> ContainsLocations { get; set; } = new();
    
    [JsonPropertyName("connectedTo")]
    public List<string> ConnectedTo { get; set; } = new();
    
    [JsonPropertyName("businessRules")]
    public List<BusinessRule> BusinessRules { get; set; } = new();
    
    [JsonPropertyName("lastUpdated")]
    public DateTime LastUpdated { get; set; } = DateTime.UtcNow;
}

/// <summary>
/// Represents a robot asset in the warehouse
/// </summary>
public class RobotAsset
{
    [JsonPropertyName("$dtId")]
    public string Id { get; set; } = string.Empty;
    
    [JsonPropertyName("$dtId")]
    public string ModelId { get; set; } = "dtmi:boggssystems:warehouse:robot;1";
    
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;
    
    [JsonPropertyName("robotType")]
    public RobotType RobotType { get; set; }
    
    [JsonPropertyName("status")]
    public RobotStatus Status { get; set; }
    
    [JsonPropertyName("batteryPct")]
    public double BatteryPct { get; set; }
    
    [JsonPropertyName("currentTaskId")]
    public string? CurrentTaskId { get; set; }
    
    [JsonPropertyName("currentZoneId")]
    public string? CurrentZoneId { get; set; }
    
    [JsonPropertyName("capabilities")]
    public List<string> Capabilities { get; set; } = new();
    
    [JsonPropertyName("location")]
    public Location Location { get; set; } = new();
    
    [JsonPropertyName("healthStatus")]
    public HealthStatus HealthStatus { get; set; }
    
    [JsonPropertyName("lastUpdated")]
    public DateTime LastUpdated { get; set; } = DateTime.UtcNow;
}

/// <summary>
/// Represents a workstation for specific warehouse operations
/// </summary>
public class Workstation
{
    [JsonPropertyName("$dtId")]
    public string Id { get; set; } = string.Empty;
    
    [JsonPropertyName("$dtId")]
    public string ModelId { get; set; } = "dtmi:boggssystems:warehouse:workstation;1";
    
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;
    
    [JsonPropertyName("workstationType")]
    public WorkstationType WorkstationType { get; set; }
    
    [JsonPropertyName("status")]
    public WorkstationStatus Status { get; set; }
    
    [JsonPropertyName("location")]
    public Location Location { get; set; } = new();
    
    [JsonPropertyName("currentOperator")]
    public string? CurrentOperator { get; set; }
    
    [JsonPropertyName("activeTaskId")]
    public string? ActiveTaskId { get; set; }
    
    [JsonPropertyName("lastUpdated")]
    public DateTime LastUpdated { get; set; } = DateTime.UtcNow;
}

/// <summary>
/// Represents a conveyor system in the warehouse
/// </summary>
public class Conveyor
{
    [JsonPropertyName("$dtId")]
    public string Id { get; set; } = string.Empty;
    
    [JsonPropertyName("$dtId")]
    public string ModelId { get; set; } = "dtmi:boggssystems:warehouse:conveyor;1";
    
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;
    
    [JsonPropertyName("conveyorType")]
    public ConveyorType ConveyorType { get; set; }
    
    [JsonPropertyName("status")]
    public ConveyorStatus Status { get; set; }
    
    [JsonPropertyName("speed")]
    public double Speed { get; set; }
    
    [JsonPropertyName("capacity")]
    public double Capacity { get; set; }
    
    [JsonPropertyName("currentLoad")]
    public double CurrentLoad { get; set; }
    
    [JsonPropertyName("startLocation")]
    public string StartLocation { get; set; } = string.Empty;
    
    [JsonPropertyName("endLocation")]
    public string EndLocation { get; set; } = string.Empty;
    
    [JsonPropertyName("lastUpdated")]
    public DateTime LastUpdated { get; set; } = DateTime.UtcNow;
}

/// <summary>
/// Represents a docking bay for receiving and shipping
/// </summary>
public class DockingBay
{
    [JsonPropertyName("$dtId")]
    public string Id { get; set; } = string.Empty;
    
    [JsonPropertyName("$dtId")]
    public string ModelId { get; set; } = "dtmi:boggssystems:warehouse:dockingbay;1";
    
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;
    
    [JsonPropertyName("bayType")]
    public DockingBayType BayType { get; set; }
    
    [JsonPropertyName("status")]
    public DockingBayStatus Status { get; set; }
    
    [JsonPropertyName("location")]
    public Location Location { get; set; } = new();
    
    [JsonPropertyName("currentVehicle")]
    public string? CurrentVehicle { get; set; }
    
    [JsonPropertyName("estimatedArrival")]
    public DateTime? EstimatedArrival { get; set; }
    
    [JsonPropertyName("estimatedDeparture")]
    public DateTime? EstimatedDeparture { get; set; }
    
    [JsonPropertyName("lastUpdated")]
    public DateTime LastUpdated { get; set; } = DateTime.UtcNow;
}

/// <summary>
/// Represents a location in 3D space
/// </summary>
public class Location
{
    [JsonPropertyName("x")]
    public double X { get; set; }
    
    [JsonPropertyName("y")]
    public double Y { get; set; }
    
    [JsonPropertyName("z")]
    public double Z { get; set; }
    
    [JsonPropertyName("zoneId")]
    public string? ZoneId { get; set; }
    
    [JsonPropertyName("floor")]
    public int Floor { get; set; } = 1;
}

/// <summary>
/// Represents a business rule for warehouse operations
/// </summary>
public class BusinessRule
{
    [JsonPropertyName("ruleId")]
    public string RuleId { get; set; } = string.Empty;
    
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;
    
    [JsonPropertyName("description")]
    public string Description { get; set; } = string.Empty;
    
    [JsonPropertyName("ruleType")]
    public BusinessRuleType RuleType { get; set; }
    
    [JsonPropertyName("conditions")]
    public List<RuleCondition> Conditions { get; set; } = new();
    
    [JsonPropertyName("actions")]
    public List<RuleAction> Actions { get; set; } = new();
    
    [JsonPropertyName("priority")]
    public RulePriority Priority { get; set; }
    
    [JsonPropertyName("enabled")]
    public bool Enabled { get; set; } = true;
}

/// <summary>
/// Represents a condition in a business rule
/// </summary>
public class RuleCondition
{
    [JsonPropertyName("property")]
    public string Property { get; set; } = string.Empty;
    
    [JsonPropertyName("operator")]
    public string Operator { get; set; } = string.Empty;
    
    [JsonPropertyName("value")]
    public object Value { get; set; } = string.Empty;
}

/// <summary>
/// Represents an action in a business rule
/// </summary>
public class RuleAction
{
    [JsonPropertyName("actionType")]
    public string ActionType { get; set; } = string.Empty;
    
    [JsonPropertyName("parameters")]
    public Dictionary<string, object> Parameters { get; set; } = new();
}

// Enums for warehouse entities
public enum WarehouseType
{
    Distribution,
    Fulfillment,
    Manufacturing,
    ColdStorage,
    CrossDock
}

public enum WarehouseStatus
{
    Active,
    Inactive,
    Maintenance,
    Emergency
}

public enum WarehouseZoneType
{
    Receiving,
    Stowing,
    Picking,
    Packing,
    Shipping,
    QualityControl,
    Charging,
    Maintenance,
    Storage,
    Office
}

public enum ZoneStatus
{
    Active,
    Inactive,
    Maintenance,
    Restricted,
    Emergency
}

public enum RobotType
{
    Humanoid,
    Quadruped,
    AGV,
    Drone,
    Fixed
}

public enum RobotStatus
{
    Idle,
    Busy,
    Charging,
    Maintenance,
    Error,
    Offline
}

public enum HealthStatus
{
    Healthy,
    Warning,
    Critical,
    Offline
}

public enum WorkstationType
{
    Picking,
    Packing,
    QualityControl,
    Receiving,
    Shipping,
    Maintenance
}

public enum WorkstationStatus
{
    Available,
    Occupied,
    Maintenance,
    Offline
}

public enum ConveyorType
{
    Belt,
    Roller,
    Chain,
    Sortation,
    Accumulation
}

public enum ConveyorStatus
{
    Running,
    Stopped,
    Maintenance,
    Error,
    Emergency
}

public enum DockingBayType
{
    Receiving,
    Shipping,
    Both,
    Specialized
}

public enum DockingBayStatus
{
    Available,
    Occupied,
    Reserved,
    Maintenance,
    OutOfService
}

public enum BusinessRuleType
{
    Safety,
    Efficiency,
    Quality,
    Compliance,
    Operational
}

public enum RulePriority
{
    Low,
    Medium,
    High,
    Critical
}
