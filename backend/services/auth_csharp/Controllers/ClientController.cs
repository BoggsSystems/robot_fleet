using Microsoft.AspNetCore.Mvc;
using AuthService.Models;
using AuthService.Services;
using AuthService.Controllers;

namespace AuthService.Controllers;

[ApiController]
[Route("api/admin")]
public class ClientController : ControllerBase
{
    private readonly ClientStore _clientStore;
    private readonly ILogger<ClientController> _logger;

    public ClientController(ClientStore clientStore, ILogger<ClientController> logger)
    {
        _clientStore = clientStore;
        _logger = logger;
    }

    // GET /api/admin/clients
    [HttpGet("clients")]
    [ServiceFilter(typeof(AdminAuthFilter))]
    public async Task<IActionResult> GetClients()
    {
        try
        {
            var clients = await _clientStore.GetAllAsync();
            _logger.LogInformation("Retrieved {Count} clients", clients.Count);
            
            return Ok(new ClientsListResponse
            {
                Clients = clients,
                Total = clients.Count
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving clients");
            return StatusCode(500, new { error = "Failed to retrieve clients", detail = ex.Message });
        }
    }

    // GET /api/admin/clients/{id}
    [HttpGet("clients/{id}")]
    [ServiceFilter(typeof(AdminAuthFilter))]
    public async Task<IActionResult> GetClient(string id)
    {
        try
        {
            var client = await _clientStore.GetByIdAsync(id);
            if (client == null)
            {
                return NotFound(new { error = "Client not found" });
            }
            
            return Ok(new ClientResponse
            {
                Message = "Client retrieved successfully",
                Client = client
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving client {ClientId}", id);
            return StatusCode(500, new { error = "Failed to retrieve client", detail = ex.Message });
        }
    }

    // POST /api/admin/clients
    [HttpPost("clients")]
    [ServiceFilter(typeof(AdminAuthFilter))]
    public async Task<IActionResult> CreateClient([FromBody] CreateClientRequest request)
    {
        try
        {
            _logger.LogInformation("Creating client: {ClientName}", request.Name);
            
            // Validate required fields
            if (string.IsNullOrWhiteSpace(request.Name))
            {
                return BadRequest(new { error = "Client name is required" });
            }
            
            if (string.IsNullOrWhiteSpace(request.Email))
            {
                return BadRequest(new { error = "Email is required" });
            }
            
            // Map request to Client model
            var client = new Client
            {
                Name = request.Name,
                Email = request.Email,
                Phone = request.Phone,
                Plan = request.Plan,
                EntityType = request.EntityType,
                Industry = request.Industry,
                TaxId = request.TaxId,
                Locations = request.Locations ?? new List<ClientLocation>(),
                FleetSize = request.FleetSize,
                DeploymentPriority = request.DeploymentPriority,
                Integrations = request.Integrations ?? new List<string>()
            };
            
            var createdClient = await _clientStore.CreateAsync(client);
            
            _logger.LogInformation("Created client: {ClientId}", createdClient.Id);
            
            return Created($"/api/admin/clients/{createdClient.Id}", new ClientResponse
            {
                Message = "Client created successfully",
                Client = createdClient
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating client");
            return StatusCode(500, new { error = "Failed to create client", detail = ex.Message });
        }
    }

    // PUT /api/admin/clients/{id}
    [HttpPut("clients/{id}")]
    [ServiceFilter(typeof(AdminAuthFilter))]
    public async Task<IActionResult> UpdateClient(string id, [FromBody] UpdateClientRequest request)
    {
        try
        {
            _logger.LogInformation("Updating client: {ClientId}", id);
            
            var updatedClient = await _clientStore.UpdateAsync(id, request);
            if (updatedClient == null)
            {
                return NotFound(new { error = "Client not found" });
            }
            
            _logger.LogInformation("Updated client: {ClientId}", id);
            
            return Ok(new ClientResponse
            {
                Message = "Client updated successfully",
                Client = updatedClient
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating client {ClientId}", id);
            return StatusCode(500, new { error = "Failed to update client", detail = ex.Message });
        }
    }

    // DELETE /api/admin/clients/{id}
    [HttpDelete("clients/{id}")]
    [ServiceFilter(typeof(AdminAuthFilter))]
    public async Task<IActionResult> DeleteClient(string id)
    {
        try
        {
            _logger.LogInformation("Deleting client: {ClientId}", id);
            
            var deleted = await _clientStore.DeleteAsync(id);
            if (!deleted)
            {
                return NotFound(new { error = "Client not found" });
            }
            
            _logger.LogInformation("Deleted client: {ClientId}", id);
            
            return Ok(new { message = "Client deleted successfully" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deleting client {ClientId}", id);
            return StatusCode(500, new { error = "Failed to delete client", detail = ex.Message });
        }
    }

    // GET /api/admin/dashboard/stats
    [HttpGet("dashboard/stats")]
    [ServiceFilter(typeof(AdminAuthFilter))]
    public async Task<IActionResult> GetDashboardStats()
    {
        try
        {
            var stats = await _clientStore.GetDashboardStatsAsync();
            _logger.LogInformation("Retrieved dashboard stats");
            
            return Ok(stats);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving dashboard stats");
            return StatusCode(500, new { error = "Failed to retrieve dashboard stats", detail = ex.Message });
        }
    }
}
