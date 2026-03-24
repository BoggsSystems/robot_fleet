using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.AspNetCore.Mvc;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseAuthorization();
app.MapControllers();

// Add health check endpoint
app.MapGet("/health", () => new 
{
    status = "healthy",
    service = "warehouse-digital-twin",
    timestamp = DateTime.UtcNow,
    version = "1.0.0"
});

// Add root endpoint
app.MapGet("/", () => new 
{
    message = "Warehouse Digital Twin Service",
    status = "running",
    capabilities = new[] { "digital-twin-management", "warehouse-configuration", "client-setup" }
});

// Simple warehouse configuration endpoint
app.MapPost("/api/DigitalTwin/warehouse/configuration", (WarehouseConfig config) => 
{
    var warehouseId = $"warehouse-{Guid.NewGuid():N}";
    
    return new 
    {
        warehouseId = warehouseId,
        clientId = config.ClientId,
        warehouseName = config.WarehouseName,
        warehouseType = config.WarehouseType,
        totalArea = config.TotalArea,
        status = "created",
        timestamp = DateTime.UtcNow,
        message = "Warehouse configuration created successfully"
    };
});

// Simple zone management endpoint
app.MapPost("/api/DigitalTwin/zone", (ZoneConfig zone) => 
{
    var zoneId = $"zone-{Guid.NewGuid():N}";
    
    return new 
    {
        zoneId = zoneId,
        name = zone.Name,
        zoneType = zone.ZoneType,
        area = zone.Area,
        capacity = zone.Capacity,
        status = "created",
        timestamp = DateTime.UtcNow
    };
});

// Simple robot management endpoint
app.MapPost("/api/DigitalTwin/robot", (RobotConfig robot) => 
{
    var robotId = $"robot-{Guid.NewGuid():N}";
    
    return new 
    {
        robotId = robotId,
        name = robot.Name,
        robotType = robot.RobotType,
        batteryPct = robot.BatteryPct,
        status = "created",
        timestamp = DateTime.UtcNow
    };
});

// Simple query endpoint
app.MapGet("/api/DigitalTwin/warehouse/{warehouseId}", (string warehouseId) => 
{
    return new 
    {
        warehouseId = warehouseId,
        name = "Sample Warehouse",
        type = "Distribution",
        totalArea = 50000,
        zones = new[] 
        {
            new { id = "zone-1", name = "Receiving", type = "Receiving", capacity = 150 },
            new { id = "zone-2", name = "Picking", type = "Picking", capacity = 300 }
        },
        robots = new[]
        {
            new { id = "robot-1", name = "Picker-001", type = "Humanoid", batteryPct = 95.0, status = "idle" }
        },
        status = "active",
        lastUpdated = DateTime.UtcNow
    };
});

app.Run();

// Simple DTOs
public class WarehouseConfig
{
    public string ClientId { get; set; } = string.Empty;
    public string WarehouseName { get; set; } = string.Empty;
    public string WarehouseType { get; set; } = "Distribution";
    public int TotalArea { get; set; }
}

public class ZoneConfig
{
    public string Name { get; set; } = string.Empty;
    public string ZoneType { get; set; } = string.Empty;
    public int Area { get; set; }
    public int Capacity { get; set; }
}

public class RobotConfig
{
    public string Name { get; set; } = string.Empty;
    public string RobotType { get; set; } = string.Empty;
    public double BatteryPct { get; set; }
}
