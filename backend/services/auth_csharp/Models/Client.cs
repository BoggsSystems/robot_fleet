using System.Text.Json.Serialization;

namespace AuthService.Models;

[JsonConverter(typeof(JsonStringEnumConverter))]
public enum ClientPlan
{
    hobby,
    pro,
    business,
    enterprise
}

[JsonConverter(typeof(JsonStringEnumConverter))]
public enum ClientStatus
{
    active,
    trial,
    suspended,
    inactive,
    pending_setup
}

public class MagicToken
{
    public string Id { get; set; } = string.Empty;
    public string ClientId { get; set; } = string.Empty;
    public string Token { get; set; } = string.Empty;
    public DateTime ExpiresAt { get; set; }
    public bool IsUsed { get; set; } = false;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}

public class ClientLocation
{
    public string Name { get; set; } = string.Empty;
    public string Address { get; set; } = string.Empty;
    public string Type { get; set; } = "primary";
    public string Classification { get; set; } = "indoor";
    public string Size { get; set; } = string.Empty;
    public string OperatingHours { get; set; } = "24/7";
}

public class ClientFleet
{
    public int TotalRobots { get; set; }
    public int ActiveRobots { get; set; }
    public int IdleRobots { get; set; }
    public int MaintenanceRobots { get; set; }
}

public class ClientSubscription
{
    public string StartDate { get; set; } = string.Empty;
    public string EndDate { get; set; } = string.Empty;
    public int Mrr { get; set; }
}

public class Client
{
    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;

    public string Name { get; set; } = string.Empty;
    public ClientStatus Status { get; set; } = ClientStatus.pending_setup;
    public ClientPlan Plan { get; set; } = ClientPlan.hobby;
    public string EntityType { get; set; } = "business";
    public string? Industry { get; set; }
    public string Email { get; set; } = string.Empty;
    public string? Phone { get; set; }
    public string? TaxId { get; set; }
    public string? PasswordHash { get; set; }
    public List<MagicToken> MagicTokens { get; set; } = new();
    public List<ClientLocation> Locations { get; set; } = new();
    public int FleetSize { get; set; }
    public string DeploymentPriority { get; set; } = "standard";
    public List<string> Integrations { get; set; } = new();
    public ClientFleet Fleet { get; set; } = new();
    public ClientSubscription Subscription { get; set; } = new();
    public DateTime CreatedAt { get; set; }
    public DateTime? UpdatedAt { get; set; }
}

// DTOs for API requests/responses
public class CreateClientRequest
{
    public string Name { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string? Phone { get; set; }
    public ClientPlan Plan { get; set; } = ClientPlan.hobby;
    public string EntityType { get; set; } = "business";
    public string? Industry { get; set; }
    public string? TaxId { get; set; }
    public List<ClientLocation> Locations { get; set; } = new();
    public int FleetSize { get; set; } = 1;
    public string DeploymentPriority { get; set; } = "standard";
    public List<string> Integrations { get; set; } = new();
}

public class UpdateClientRequest
{
    public string? Name { get; set; }
    public string? Email { get; set; }
    public ClientPlan? Plan { get; set; }
    public ClientStatus? Status { get; set; }
    public List<ClientLocation>? Locations { get; set; }
    public int? FleetSize { get; set; }
    public List<MagicToken>? MagicTokens { get; set; }
}

public class ClientResponse
{
    public string Message { get; set; } = string.Empty;
    public Client Client { get; set; } = new();
}

public class ClientsListResponse
{
    public List<Client> Clients { get; set; } = new();
    public int Total { get; set; }
}

public class ClientSummaryDto
{
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty;
    public string Plan { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public int FleetSize { get; set; }
    public int Mrr { get; set; }
    public DateTime CreatedAt { get; set; }
}

// Dashboard stats DTOs
public class DashboardStatsResponse
{
    public int TotalClients { get; set; }
    public int TotalRobots { get; set; }
    public int ActiveDeployments { get; set; }
    public int MonthlyRecurringRevenue { get; set; }
    public int TrialClients { get; set; }
    public int ActiveClients { get; set; }
    public int SuspendedClients { get; set; }
    public List<PlanDistribution> PlanDistribution { get; set; } = new();
    public List<MonthlyMrr> MrrTrend { get; set; } = new();
}

public class PlanDistribution
{
    public string Plan { get; set; } = string.Empty;
    public int Count { get; set; }
}

public class MonthlyMrr
{
    public string Month { get; set; } = string.Empty;
    public int Mrr { get; set; }
}

// Magic Link DTOs
public class GenerateMagicLinkRequest
{
    public string ClientId { get; set; } = string.Empty;
}

public class GenerateMagicLinkResponse
{
    public string Message { get; set; } = string.Empty;
    public string MagicLinkUrl { get; set; } = string.Empty;
    public string ClientId { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
}

public class ValidateMagicTokenRequest
{
    public string Token { get; set; } = string.Empty;
}

public class ValidateMagicTokenResponse
{
    public string Message { get; set; } = string.Empty;
    public string ClientId { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public bool IsValid { get; set; }
}

public class SetPasswordRequest
{
    public string Token { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty;
}

public class SetPasswordResponse
{
    public string Message { get; set; } = string.Empty;
    public string ClientId { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public bool Success { get; set; }
}

public class RequestPasswordResetRequest
{
    public string Email { get; set; } = string.Empty;
}

public class RequestPasswordResetResponse
{
    public string Message { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public bool Success { get; set; }
}
