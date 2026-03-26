using AuthService.Models;
using BCrypt.Net;

namespace AuthService.Services;

public class AdminStore
{
    private readonly CosmosDbService _cosmosDbService;

    public AdminStore(CosmosDbService cosmosDbService)
    {
        _cosmosDbService = cosmosDbService;
    }

    public async Task InitializeAsync()
    {
        await InitializeDefaultSuperAdminAsync();
    }

    private async Task InitializeDefaultSuperAdminAsync()
    {
        var existingAdmin = await _cosmosDbService.GetByUsernameAsync("admin");
        if (existingAdmin == null)
        {
            var hashedPassword = BCrypt.Net.BCrypt.HashPassword("admin123");
            var admin = new AdminUser
            {
                Id = 1,
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
            await _cosmosDbService.CreateAsync(admin);
            Console.WriteLine("Default superadmin created in Cosmos DB: admin/admin123");
        }
        else
        {
            Console.WriteLine("Default superadmin already exists in Cosmos DB");
        }
    }

    public async Task<AdminUser?> GetByUsernameAsync(string username)
    {
        return await _cosmosDbService.GetByUsernameAsync(username);
    }

    public AdminUser? GetByUsername(string username)
    {
        return GetByUsernameAsync(username).GetAwaiter().GetResult();
    }

    public async Task<AdminUser?> GetByIdAsync(int id)
    {
        return await _cosmosDbService.GetByIdAsync(id);
    }

    public AdminUser? GetById(int id)
    {
        return GetByIdAsync(id).GetAwaiter().GetResult();
    }

    public async Task<List<AdminUser>> GetAllAsync()
    {
        return await _cosmosDbService.GetAllAsync();
    }

    public List<AdminUser> GetAll()
    {
        return GetAllAsync().GetAwaiter().GetResult();
    }

    public async Task<AdminUser> CreateAsync(AdminUser user)
    {
        return await _cosmosDbService.CreateAsync(user);
    }

    public AdminUser Create(AdminUser user)
    {
        return CreateAsync(user).GetAwaiter().GetResult();
    }

    public async Task UpdateLastLoginAsync(int id)
    {
        await _cosmosDbService.UpdateLastLoginAsync(id);
    }

    public void UpdateLastLogin(int id)
    {
        UpdateLastLoginAsync(id).GetAwaiter().GetResult();
    }

    public async Task<bool> UsernameExistsAsync(string username)
    {
        return await _cosmosDbService.UsernameExistsAsync(username);
    }

    public bool UsernameExists(string username)
    {
        return UsernameExistsAsync(username).GetAwaiter().GetResult();
    }
}
