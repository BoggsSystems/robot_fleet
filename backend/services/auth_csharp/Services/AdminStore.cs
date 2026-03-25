using AuthService.Models;
using BCrypt.Net;

namespace AuthService.Services;

public class AdminStore
{
    private readonly List<AdminUser> _adminUsers = new();
    private int _nextId = 1;

    public AdminStore()
    {
        // Initialize with default superadmin
        _ = InitializeDefaultSuperAdminAsync();
    }

    private async Task InitializeDefaultSuperAdminAsync()
    {
        var existingAdmin = _adminUsers.FirstOrDefault(u => u.Username == "admin");
        if (existingAdmin == null)
        {
            var hashedPassword = BCrypt.HashPassword("admin123");
            var admin = new AdminUser
            {
                Id = _nextId++,
                Username = "admin",
                Email = "admin@robotfleet.com",
                Password = hashedPassword,
                Role = AdminRole.Superadmin,
                Permissions = AdminRolePermissions.GetPermissions(AdminRole.Superadmin).ToList(),
                Profile = new AdminProfile
                {
                    FirstName = "Super",
                    LastName = "Admin",
                    Department = "Management",
                    Phone = "+1-555-0100"
                },
                CreatedAt = DateTime.UtcNow,
                LastLogin = null
            };
            _adminUsers.Add(admin);
            Console.WriteLine("Default superadmin created: admin/admin123");
        }
    }

    public AdminUser? GetByUsername(string username)
    {
        return _adminUsers.FirstOrDefault(u => u.Username == username);
    }

    public AdminUser? GetById(int id)
    {
        return _adminUsers.FirstOrDefault(u => u.Id == id);
    }

    public List<AdminUser> GetAll()
    {
        return _adminUsers.ToList();
    }

    public AdminUser Create(AdminUser user)
    {
        user.Id = _nextId++;
        user.CreatedAt = DateTime.UtcNow;
        _adminUsers.Add(user);
        return user;
    }

    public void UpdateLastLogin(int id)
    {
        var user = _adminUsers.FirstOrDefault(u => u.Id == id);
        if (user != null)
        {
            user.LastLogin = DateTime.UtcNow;
        }
    }

    public bool UsernameExists(string username)
    {
        return _adminUsers.Any(u => u.Username == username);
    }
}
