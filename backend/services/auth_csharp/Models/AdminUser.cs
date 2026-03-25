namespace AuthService.Models;

public enum AdminRole
{
    Superadmin,
    Support,
    Billing,
    Technical
}

public class AdminProfile
{
    public string FirstName { get; set; } = string.Empty;
    public string LastName { get; set; } = string.Empty;
    public string Department { get; set; } = string.Empty;
    public string Phone { get; set; } = string.Empty;
}

public class AdminUser
{
    public int Id { get; set; }
    public string Username { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty; // Hashed
    public AdminRole Role { get; set; }
    public List<string> Permissions { get; set; } = new();
    public AdminProfile Profile { get; set; } = new();
    public DateTime CreatedAt { get; set; }
    public DateTime? LastLogin { get; set; }
    public int? CreatedBy { get; set; }
}

public static class AdminRolePermissions
{
    public static readonly Dictionary<AdminRole, string[]> RolePermissions = new()
    {
        [AdminRole.Superadmin] = new[] { "*" }, // All permissions
        [AdminRole.Support] = new[] { "client:read", "fleet:read", "user:read", "system:read" },
        [AdminRole.Billing] = new[] { "client:read", "client:write", "billing:read", "billing:write" },
        [AdminRole.Technical] = new[] { "fleet:read", "fleet:write", "system:read", "system:admin" }
    };

    public static string[] GetPermissions(AdminRole role) => RolePermissions[role];
}
