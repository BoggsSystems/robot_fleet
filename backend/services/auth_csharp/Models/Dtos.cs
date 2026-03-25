namespace AuthService.Models;

// Login Request/Response
public class AdminLoginRequest
{
    public string Username { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty;
}

public class AdminLoginResponse
{
    public string Message { get; set; } = string.Empty;
    public string Token { get; set; } = string.Empty;
    public AdminUserDto Admin { get; set; } = new();
}

// Profile Response
public class AdminProfileResponse
{
    public AdminUserDto Admin { get; set; } = new();
}

// User Management
public class CreateAdminRequest
{
    public string Username { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public AdminRole Role { get; set; }
    public AdminProfile? Profile { get; set; }
}

public class AdminUsersListResponse
{
    public List<AdminUserSummaryDto> Users { get; set; } = new();
}

// DTOs (Data Transfer Objects)
public class AdminUserDto
{
    public int Id { get; set; }
    public string Username { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string Role { get; set; } = string.Empty;
    public List<string> Permissions { get; set; } = new();
    public AdminProfile Profile { get; set; } = new();
    public DateTime? LastLogin { get; set; }
    public DateTime CreatedAt { get; set; }
}

public class AdminUserSummaryDto
{
    public int Id { get; set; }
    public string Username { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string Role { get; set; } = string.Empty;
    public AdminProfile Profile { get; set; } = new();
    public DateTime? LastLogin { get; set; }
    public DateTime CreatedAt { get; set; }
}

public class LogoutResponse
{
    public string Message { get; set; } = string.Empty;
}

public class ErrorResponse
{
    public string Error { get; set; } = string.Empty;
}
