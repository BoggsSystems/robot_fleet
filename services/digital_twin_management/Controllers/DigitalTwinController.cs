using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using WarehouseDigitalTwin.Models;
using WarehouseDigitalTwin.Services;

namespace WarehouseDigitalTwin.Controllers;

/// <summary>
/// API controller for Digital Twin management operations
/// </summary>
[ApiController]
[Route("api/[controller]")]
[Produces("application/json")]
public class DigitalTwinController : ControllerBase
{
    private readonly DigitalTwinManager _digitalTwinManager;
    private readonly ConfigurationService _configurationService;
    private readonly ILogger<DigitalTwinController> _logger;

    public DigitalTwinController(
        DigitalTwinManager digitalTwinManager,
        ConfigurationService configurationService,
        ILogger<DigitalTwinController> logger)
    {
        _digitalTwinManager = digitalTwinManager;
        _configurationService = configurationService;
        _logger = logger;
    }

    /// <summary>
    /// Creates a new warehouse digital twin
    /// </summary>
    /// <param name="warehouse">Warehouse configuration</param>
    /// <returns>Created warehouse twin ID</returns>
    [HttpPost("warehouse")]
    public async Task<ActionResult<string>> CreateWarehouse([FromBody] WarehouseDigitalTwin warehouse)
    {
        try
        {
            _logger.LogInformation("Creating warehouse: {WarehouseId}", warehouse.Id);

            var warehouseId = await _digitalTwinManager.CreateWarehouseAsync(warehouse);

            return CreatedAtAction(nameof(GetWarehouse), new { warehouseId }, warehouseId);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to create warehouse: {WarehouseId}", warehouse.Id);
            return StatusCode(500, new { error = "Failed to create warehouse", message = ex.Message });
        }
    }

    /// <summary>
    /// Gets a warehouse digital twin by ID
    /// </summary>
    /// <param name="warehouseId">Warehouse ID</param>
    /// <returns>Warehouse digital twin</returns>
    [HttpGet("warehouse/{warehouseId}")]
    public async Task<ActionResult<WarehouseDigitalTwin>> GetWarehouse(string warehouseId)
    {
        try
        {
            var warehouse = await _digitalTwinManager.GetDigitalTwinAsync<WarehouseDigitalTwin>(warehouseId);

            if (warehouse == null)
            {
                return NotFound(new { error = "Warehouse not found", warehouseId });
            }

            return Ok(warehouse);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get warehouse: {WarehouseId}", warehouseId);
            return StatusCode(500, new { error = "Failed to get warehouse", message = ex.Message });
        }
    }

    /// <summary>
    /// Creates a complete warehouse configuration
    /// </summary>
    /// <param name="request">Warehouse configuration request</param>
    /// <returns>Configuration result</returns>
    [HttpPost("warehouse/configuration")]
    public async Task<ActionResult<ConfigurationResult>> CreateWarehouseConfiguration([FromBody] WarehouseConfigurationRequest request)
    {
        try
        {
            _logger.LogInformation("Creating warehouse configuration for client: {ClientId}", request.ClientId);

            var result = await _configurationService.CreateWarehouseConfigurationAsync(request);

            if (!result.Success)
            {
                return BadRequest(new { error = "Configuration failed", errors = result.Errors });
            }

            return CreatedAtAction(nameof(GetWarehouseConfiguration), new { warehouseId = result.WarehouseId }, result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to create warehouse configuration for client: {ClientId}", request.ClientId);
            return StatusCode(500, new { error = "Failed to create warehouse configuration", message = ex.Message });
        }
    }

    /// <summary>
    /// Gets warehouse configuration summary
    /// </summary>
    /// <param name="warehouseId">Warehouse ID</param>
    /// <returns>Warehouse configuration summary</returns>
    [HttpGet("warehouse/{warehouseId}/configuration")]
    public async Task<ActionResult<WarehouseConfigurationSummary>> GetWarehouseConfiguration(string warehouseId)
    {
        try
        {
            var configuration = await _configurationService.GetWarehouseConfigurationAsync(warehouseId);

            if (configuration == null)
            {
                return NotFound(new { error = "Warehouse configuration not found", warehouseId });
            }

            return Ok(configuration);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get warehouse configuration: {WarehouseId}", warehouseId);
            return StatusCode(500, new { error = "Failed to get warehouse configuration", message = ex.Message });
        }
    }

    /// <summary>
    /// Updates warehouse configuration
    /// </summary>
    /// <param name="warehouseId">Warehouse ID</param>
    /// <param name="request">Update request</param>
    /// <returns>Update result</returns>
    [HttpPut("warehouse/{warehouseId}/configuration")]
    public async Task<ActionResult<ConfigurationResult>> UpdateWarehouseConfiguration(string warehouseId, [FromBody] WarehouseConfigurationRequest request)
    {
        try
        {
            _logger.LogInformation("Updating warehouse configuration: {WarehouseId}", warehouseId);

            var result = await _configurationService.UpdateWarehouseConfigurationAsync(warehouseId, request);

            if (!result.Success)
            {
                return BadRequest(new { error = "Update failed", errors = result.Errors });
            }

            return Ok(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to update warehouse configuration: {WarehouseId}", warehouseId);
            return StatusCode(500, new { error = "Failed to update warehouse configuration", message = ex.Message });
        }
    }

    /// <summary>
    /// Creates a new zone digital twin
    /// </summary>
    /// <param name="warehouseId">Warehouse ID</param>
    /// <param name="zone">Zone configuration</param>
    /// <returns>Created zone twin ID</returns>
    [HttpPost("warehouse/{warehouseId}/zones")]
    public async Task<ActionResult<string>> CreateZone(string warehouseId, [FromBody] Zone zone)
    {
        try
        {
            _logger.LogInformation("Creating zone: {ZoneId} for warehouse: {WarehouseId}", zone.Id, warehouseId);

            var zoneId = await _digitalTwinManager.CreateZoneAsync(zone, warehouseId);

            return CreatedAtAction(nameof(GetZone), new { warehouseId, zoneId }, zoneId);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to create zone: {ZoneId} for warehouse: {WarehouseId}", zone.Id, warehouseId);
            return StatusCode(500, new { error = "Failed to create zone", message = ex.Message });
        }
    }

    /// <summary>
    /// Gets a zone digital twin by ID
    /// </summary>
    /// <param name="warehouseId">Warehouse ID</param>
    /// <param name="zoneId">Zone ID</param>
    /// <returns>Zone digital twin</returns>
    [HttpGet("warehouse/{warehouseId}/zones/{zoneId}")]
    public async Task<ActionResult<Zone>> GetZone(string warehouseId, string zoneId)
    {
        try
        {
            var zone = await _digitalTwinManager.GetDigitalTwinAsync<Zone>(zoneId);

            if (zone == null)
            {
                return NotFound(new { error = "Zone not found", warehouseId, zoneId });
            }

            return Ok(zone);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get zone: {ZoneId} for warehouse: {WarehouseId}", zoneId, warehouseId);
            return StatusCode(500, new { error = "Failed to get zone", message = ex.Message });
        }
    }

    /// <summary>
    /// Gets all zones for a warehouse
    /// </summary>
    /// <param name="warehouseId">Warehouse ID</param>
    /// <returns>List of zones</returns>
    [HttpGet("warehouse/{warehouseId}/zones")]
    public async Task<ActionResult<List<Zone>>> GetWarehouseZones(string warehouseId)
    {
        try
        {
            var zones = await _digitalTwinManager.GetWarehouseZonesAsync(warehouseId);

            return Ok(zones);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get zones for warehouse: {WarehouseId}", warehouseId);
            return StatusCode(500, new { error = "Failed to get warehouse zones", message = ex.Message });
        }
    }

    /// <summary>
    /// Creates a new robot digital twin
    /// </summary>
    /// <param name="warehouseId">Warehouse ID</param>
    /// <param name="zoneId">Zone ID</param>
    /// <param name="robot">Robot configuration</param>
    /// <returns>Created robot twin ID</returns>
    [HttpPost("warehouse/{warehouseId}/zones/{zoneId}/robots")]
    public async Task<ActionResult<string>> CreateRobot(string warehouseId, string zoneId, [FromBody] RobotAsset robot)
    {
        try
        {
            _logger.LogInformation("Creating robot: {RobotId} for zone: {ZoneId} in warehouse: {WarehouseId}", robot.Id, zoneId, warehouseId);

            var robotId = await _digitalTwinManager.CreateRobotAsync(robot, zoneId);

            return CreatedAtAction(nameof(GetRobot), new { warehouseId, zoneId, robotId }, robotId);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to create robot: {RobotId} for zone: {ZoneId} in warehouse: {WarehouseId}", robot.Id, zoneId, warehouseId);
            return StatusCode(500, new { error = "Failed to create robot", message = ex.Message });
        }
    }

    /// <summary>
    /// Gets a robot digital twin by ID
    /// </summary>
    /// <param name="warehouseId">Warehouse ID</param>
    /// <param name="zoneId">Zone ID</param>
    /// <param name="robotId">Robot ID</param>
    /// <returns>Robot digital twin</returns>
    [HttpGet("warehouse/{warehouseId}/zones/{zoneId}/robots/{robotId}")]
    public async Task<ActionResult<RobotAsset>> GetRobot(string warehouseId, string zoneId, string robotId)
    {
        try
        {
            var robot = await _digitalTwinManager.GetDigitalTwinAsync<RobotAsset>(robotId);

            if (robot == null)
            {
                return NotFound(new { error = "Robot not found", warehouseId, zoneId, robotId });
            }

            return Ok(robot);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get robot: {RobotId} for zone: {ZoneId} in warehouse: {WarehouseId}", robotId, zoneId, warehouseId);
            return StatusCode(500, new { error = "Failed to get robot", message = ex.Message });
        }
    }

    /// <summary>
    /// Gets all robots in a zone
    /// </summary>
    /// <param name="warehouseId">Warehouse ID</param>
    /// <param name="zoneId">Zone ID</param>
    /// <returns>List of robots</returns>
    [HttpGet("warehouse/{warehouseId}/zones/{zoneId}/robots")]
    public async Task<ActionResult<List<RobotAsset>>> GetZoneRobots(string warehouseId, string zoneId)
    {
        try
        {
            var robots = await _digitalTwinManager.GetZoneRobotsAsync(zoneId);

            return Ok(robots);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get robots for zone: {ZoneId} in warehouse: {WarehouseId}", zoneId, warehouseId);
            return StatusCode(500, new { error = "Failed to get zone robots", message = ex.Message });
        }
    }

    /// <summary>
    /// Updates robot status and location
    /// </summary>
    /// <param name="warehouseId">Warehouse ID</param>
    /// <param name="zoneId">Zone ID</param>
    /// <param name="robotId">Robot ID</param>
    /// <param name="updateRequest">Update request</param>
    /// <returns>Update result</returns>
    [HttpPut("warehouse/{warehouseId}/zones/{zoneId}/robots/{robotId}/status")]
    public async Task<ActionResult> UpdateRobotStatus(string warehouseId, string zoneId, string robotId, [FromBody] RobotStatusUpdateRequest updateRequest)
    {
        try
        {
            _logger.LogInformation("Updating robot status: {RobotId} to {Status}", robotId, updateRequest.Status);

            await _digitalTwinManager.UpdateRobotStatusAsync(robotId, updateRequest.Status, updateRequest.Location);

            return NoContent();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to update robot status: {RobotId}", robotId);
            return StatusCode(500, new { error = "Failed to update robot status", message = ex.Message });
        }
    }

    /// <summary>
    /// Queries digital twins using custom query
    /// </summary>
    /// <param name="query">Digital Twins query</param>
    /// <returns>Query results</returns>
    [HttpPost("query")]
    public async Task<ActionResult<List<BasicDigitalTwin>>> QueryDigitalTwins([FromBody] string query)
    {
        try
        {
            _logger.LogInformation("Executing Digital Twins query: {Query}", query);

            var results = await _digitalTwinManager.QueryDigitalTwinsAsync<BasicDigitalTwin>(query);

            return Ok(results);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to execute Digital Twins query: {Query}", query);
            return StatusCode(500, new { error = "Failed to execute query", message = ex.Message });
        }
    }

    /// <summary>
    /// Deletes a digital twin
    /// </summary>
    /// <param name="twinId">Twin ID</param>
    /// <returns>Delete result</returns>
    [HttpDelete("{twinId}")]
    public async Task<ActionResult> DeleteDigitalTwin(string twinId)
    {
        try
        {
            _logger.LogInformation("Deleting digital twin: {TwinId}", twinId);

            await _digitalTwinManager.DeleteDigitalTwinAsync(twinId);

            return NoContent();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to delete digital twin: {TwinId}", twinId);
            return StatusCode(500, new { error = "Failed to delete digital twin", message = ex.Message });
        }
    }

    /// <summary>
    /// Health check endpoint
    /// </summary>
    /// <returns>Health status</returns>
    [HttpGet("health")]
    public ActionResult<IActionResult> HealthCheck()
    {
        return Ok(new { status = "healthy", timestamp = DateTime.UtcNow });
    }
}

/// <summary>
/// Request model for robot status updates
/// </summary>
public class RobotStatusUpdateRequest
{
    public RobotStatus Status { get; set; }
    public Location? Location { get; set; }
}
