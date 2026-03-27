using Microsoft.AspNetCore.Mvc;
using AuthService.Models;
using AuthService.Services;
using System.Security.Cryptography;
using System.Text;

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

    private static string GenerateSecureToken()
    {
        var bytes = new byte[32];
        using (var rng = RandomNumberGenerator.Create())
        {
            rng.GetBytes(bytes);
        }
        return Convert.ToBase64String(bytes);
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

    // POST /api/admin/clients/{id}/generate-magic-link
    [HttpPost("clients/{id}/generate-magic-link")]
    [ServiceFilter(typeof(AdminAuthFilter))]
    public async Task<IActionResult> GenerateMagicLink(string id)
    {
        try
        {
            _logger.LogInformation("Generating magic link for client: {ClientId}", id);
            
            var client = await _clientStore.GetByIdAsync(id);
            if (client == null)
            {
                return NotFound(new { error = "Client not found" });
            }
            
            // Generate magic token
            var magicToken = new MagicToken
            {
                Id = Guid.NewGuid().ToString(),
                ClientId = id,
                Token = GenerateSecureToken(),
                ExpiresAt = DateTime.UtcNow.AddMinutes(30), // 30 minutes expiry
                IsUsed = false
            };
            
            // Add to client's magic tokens
            client.MagicTokens.Add(magicToken);
            await _clientStore.UpdateAsync(client.Id, new UpdateClientRequest { MagicTokens = client.MagicTokens });
            
            var magicLinkUrl = $"{Request.Scheme}://{Request.Host}/setup-password?token={magicToken.Token}";
            
            _logger.LogInformation("Generated magic link for client {ClientId}: {MagicLink}", id, magicLinkUrl);
            
            return Ok(new GenerateMagicLinkResponse
            {
                Message = "Magic link generated successfully",
                MagicLinkUrl = magicLinkUrl,
                ClientId = client.Id,
                Email = client.Email
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating magic link for client {ClientId}", id);
            return StatusCode(500, new { error = "Failed to generate magic link", detail = ex.Message });
        }
    }

    // POST /api/admin/clients/{id}/send-magic-link
    [HttpPost("clients/{id}/send-magic-link")]
    [ServiceFilter(typeof(AdminAuthFilter))]
    public async Task<IActionResult> SendMagicLink(string id)
    {
        try
        {
            _logger.LogInformation("Sending magic link for client: {ClientId}", id);
            
            var client = await _clientStore.GetByIdAsync(id);
            if (client == null)
            {
                return NotFound(new { error = "Client not found" });
            }
            
            // Generate magic token
            var magicToken = new MagicToken
            {
                Id = Guid.NewGuid().ToString(),
                ClientId = id,
                Token = GenerateSecureToken(),
                ExpiresAt = DateTime.UtcNow.AddMinutes(30),
                IsUsed = false
            };
            
            // Add to client's magic tokens
            client.MagicTokens.Add(magicToken);
            await _clientStore.UpdateAsync(client.Id, new UpdateClientRequest { MagicTokens = client.MagicTokens });
            
            var magicLinkUrl = $"{Request.Scheme}://{Request.Host}/setup-password?token={magicToken.Token}";
            
            // TODO: Send email with magic link
            // For now, just return the link
            _logger.LogInformation("Magic link sent for client {ClientId}: {MagicLink}", id, magicLinkUrl);
            
            return Ok(new GenerateMagicLinkResponse
            {
                Message = "Magic link sent successfully",
                MagicLinkUrl = magicLinkUrl,
                ClientId = client.Id,
                Email = client.Email
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error sending magic link for client {ClientId}", id);
            return StatusCode(500, new { error = "Failed to send magic link", detail = ex.Message });
        }
    }

    // GET /api/validate-magic-token
    [HttpGet("validate-magic-token")]
    public async Task<IActionResult> ValidateMagicToken([FromQuery] string token)
    {
        try
        {
            _logger.LogInformation("Validating magic token: {Token}", token);
            
            if (string.IsNullOrWhiteSpace(token))
            {
                return BadRequest(new { error = "Token is required" });
            }
            
            // Find client with valid magic token
            var clients = await _clientStore.GetAllAsync();
            var client = clients.FirstOrDefault(c => c.MagicTokens.Any(t => 
                t.Token == token && 
                !t.IsUsed && 
                t.ExpiresAt > DateTime.UtcNow));
            
            if (client == null)
            {
                return BadRequest(new ValidateMagicTokenResponse
                {
                    Message = "Invalid or expired token",
                    IsValid = false
                });
            }
            
            return Ok(new ValidateMagicTokenResponse
            {
                Message = "Token is valid",
                ClientId = client.Id,
                Email = client.Email,
                Name = client.Name,
                IsValid = true
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error validating magic token");
            return StatusCode(500, new { error = "Failed to validate token", detail = ex.Message });
        }
    }

    // POST /api/set-password
    [HttpPost("set-password")]
    public async Task<IActionResult> SetPassword([FromBody] SetPasswordRequest request)
    {
        try
        {
            _logger.LogInformation("Setting password for token: {Token}", request.Token);
            
            if (string.IsNullOrWhiteSpace(request.Token) || string.IsNullOrWhiteSpace(request.Password))
            {
                return BadRequest(new { error = "Token and password are required" });
            }
            
            if (request.Password.Length < 8)
            {
                return BadRequest(new { error = "Password must be at least 8 characters long" });
            }
            
            // Find client with valid magic token
            var clients = await _clientStore.GetAllAsync();
            var client = clients.FirstOrDefault(c => c.MagicTokens.Any(t => 
                t.Token == request.Token && 
                !t.IsUsed && 
                t.ExpiresAt > DateTime.UtcNow));
            
            if (client == null)
            {
                return BadRequest(new SetPasswordResponse
                {
                    Message = "Invalid or expired token",
                    Success = false
                });
            }
            
            // Hash password and update client
            var hashedPassword = BCrypt.Net.BCrypt.HashPassword(request.Password);
            client.PasswordHash = hashedPassword;
            client.Status = ClientStatus.active;
            client.UpdatedAt = DateTime.UtcNow;
            
            // Mark token as used
            var magicToken = client.MagicTokens.First(t => t.Token == request.Token);
            magicToken.IsUsed = true;
            
            await _clientStore.UpdateAsync(client.Id, new UpdateClientRequest { MagicTokens = client.MagicTokens });
            
            _logger.LogInformation("Password set successfully for client: {ClientId}", client.Id);
            
            return Ok(new SetPasswordResponse
            {
                Message = "Password set successfully",
                ClientId = client.Id,
                Email = client.Email,
                Name = client.Name,
                Success = true
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error setting password");
            return StatusCode(500, new { error = "Failed to set password", detail = ex.Message });
        }
    }

    // POST /api/request-password-reset
    [HttpPost("request-password-reset")]
    public async Task<IActionResult> RequestPasswordReset([FromBody] RequestPasswordResetRequest request)
    {
        try
        {
            _logger.LogInformation("Requesting password reset for email: {Email}", request.Email);
            
            if (string.IsNullOrWhiteSpace(request.Email))
            {
                return BadRequest(new { error = "Email is required" });
            }
            
            // Find client by email
            var clients = await _clientStore.GetAllAsync();
            var client = clients.FirstOrDefault(c => c.Email.Equals(request.Email, StringComparison.OrdinalIgnoreCase));
            
            if (client == null)
            {
                return BadRequest(new RequestPasswordResetResponse
                {
                    Message = "No account found with this email",
                    Success = false
                });
            }
            
            // Generate magic token for password reset
            var magicToken = new MagicToken
            {
                Id = Guid.NewGuid().ToString(),
                ClientId = client.Id,
                Token = GenerateSecureToken(),
                ExpiresAt = DateTime.UtcNow.AddMinutes(30),
                IsUsed = false
            };
            
            // Add to client's magic tokens
            client.MagicTokens.Add(magicToken);
            await _clientStore.UpdateAsync(client.Id, new UpdateClientRequest { MagicTokens = client.MagicTokens });
            
            var resetLink = $"{Request.Scheme}://{Request.Host}/reset-password?token={magicToken.Token}";
            
            // TODO: Send password reset email
            _logger.LogInformation("Password reset link generated for client {ClientId}: {ResetLink}", client.Id, resetLink);
            
            return Ok(new RequestPasswordResetResponse
            {
                Message = "Password reset link sent to your email",
                Email = client.Email,
                Success = true
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error requesting password reset");
            return StatusCode(500, new { error = "Failed to request password reset", detail = ex.Message });
        }
    }

    // GET /api/reset-password
    [HttpGet("reset-password")]
    public async Task<IActionResult> ResetPasswordPage([FromQuery] string token)
    {
        try
        {
            _logger.LogInformation("Loading reset password page for token: {Token}", token);
            
            if (string.IsNullOrWhiteSpace(token))
            {
                return BadRequest(new { error = "Token is required" });
            }
            
            // Find client with valid magic token
            var clients = await _clientStore.GetAllAsync();
            var client = clients.FirstOrDefault(c => c.MagicTokens.Any(t => 
                t.Token == token && 
                !t.IsUsed && 
                t.ExpiresAt > DateTime.UtcNow));
            
            if (client == null)
            {
                return BadRequest(new { error = "Invalid or expired token" });
            }
            
            return Ok(new ValidateMagicTokenResponse
            {
                Message = "Token is valid for password reset",
                ClientId = client.Id,
                Email = client.Email,
                Name = client.Name,
                IsValid = true
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error loading reset password page");
            return StatusCode(500, new { error = "Failed to load reset page", detail = ex.Message });
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
