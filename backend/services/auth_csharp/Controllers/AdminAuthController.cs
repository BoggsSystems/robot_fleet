using Microsoft.AspNetCore.Mvc;
using AuthService.Models;
using AuthService.Services;
using AuthService.Middleware;
using BCrypt.Net;
using System.Security.Claims;

namespace AuthService.Controllers;

[ApiController]
[Route("auth")]
public class AdminAuthController : ControllerBase
{
    private readonly AdminStore _adminStore;
    private readonly JwtService _jwtService;

    public AdminAuthController(AdminStore adminStore, JwtService jwtService)
    {
        _adminStore = adminStore;
        _jwtService = jwtService;
    }

    [HttpPost("admin/login")]
    public IActionResult AdminLogin([FromBody] AdminLoginRequest request)
    {
        var admin = _adminStore.GetByUsername(request.Username);
        if (admin == null)
        {
            return Unauthorized(new { error = "Invalid credentials" });
        }

        if (!BCrypt.Verify(request.Password, admin.Password))
        {
            return Unauthorized(new { error = "Invalid credentials" });
        }

        _adminStore.UpdateLastLogin(admin.Id);
        var token = _jwtService.GenerateAdminToken(admin);

        return Ok(new AdminLoginResponse
        {
            Message = "Admin login successful",
            Token = token,
            Admin = MapToDto(admin)
        });
    }

    [HttpGet("admin/profile")]
    [ServiceFilter(typeof(AdminAuthFilter))]
    public IActionResult GetAdminProfile()
    {
        var adminId = User.GetAdminId();
        var admin = _adminStore.GetById(adminId);

        if (admin == null)
        {
            return NotFound(new { error = "Admin user not found" });
        }

        return Ok(new AdminProfileResponse
        {
            Admin = MapToDto(admin)
        });
    }

    [HttpPost("admin/logout")]
    [ServiceFilter(typeof(AdminAuthFilter))]
    public IActionResult AdminLogout()
    {
        return Ok(new { message = "Admin logout successful" });
    }

    [HttpGet("admin/users")]
    [ServiceFilter(typeof(AdminAuthFilter))]
    public IActionResult GetAdminUsers()
    {
        if (!User.HasPermission("user:read"))
        {
            return Forbid();
        }

        var users = _adminStore.GetAll();
        var userDtos = users.Select(u => new AdminUserSummaryDto
        {
            Id = u.Id,
            Username = u.Username,
            Email = u.Email,
            Role = u.Role.ToString().ToLower(),
            Profile = u.Profile,
            LastLogin = u.LastLogin,
            CreatedAt = u.CreatedAt
        }).ToList();

        return Ok(new { users = userDtos });
    }

    [HttpPost("admin/users")]
    [ServiceFilter(typeof(AdminAuthFilter))]
    public IActionResult CreateAdminUser([FromBody] CreateAdminRequest request)
    {
        if (!User.HasPermission("user:write"))
        {
            return Forbid();
        }

        if (!Enum.IsDefined(typeof(AdminRole), request.Role))
        {
            return BadRequest(new { error = "Invalid role" });
        }

        if (_adminStore.UsernameExists(request.Username))
        {
            return BadRequest(new { error = "Username already exists" });
        }

        var hashedPassword = BCrypt.HashPassword(request.Password);
        var newAdmin = new AdminUser
        {
            Username = request.Username,
            Email = request.Email,
            Password = hashedPassword,
            Role = request.Role,
            Permissions = AdminRolePermissions.GetPermissions(request.Role).ToList(),
            Profile = request.Profile ?? new AdminProfile(),
            CreatedBy = User.GetAdminId()
        };

        _adminStore.Create(newAdmin);

        return Created($"/auth/admin/users/{newAdmin.Id}", new
        {
            message = "Admin user created successfully",
            admin = MapToDto(newAdmin)
        });
    }

    private static AdminUserDto MapToDto(AdminUser admin)
    {
        return new AdminUserDto
        {
            Id = admin.Id,
            Username = admin.Username,
            Email = admin.Email,
            Role = admin.Role.ToString().ToLower(),
            Permissions = admin.Permissions,
            Profile = admin.Profile,
            LastLogin = admin.LastLogin,
            CreatedAt = admin.CreatedAt
        };
    }
}

public class AdminAuthFilter : IAuthorizationFilter
{
    private readonly JwtService _jwtService;

    public AdminAuthFilter(JwtService jwtService)
    {
        _jwtService = jwtService;
    }

    public void OnAuthorization(AuthorizationFilterContext context)
    {
        var authHeader = context.HttpContext.Request.Headers["Authorization"].FirstOrDefault();
        
        if (string.IsNullOrEmpty(authHeader))
        {
            context.Result = new UnauthorizedObjectResult(new { error = "Authorization header required" });
            return;
        }

        var token = authHeader.StartsWith("Bearer ") ? authHeader.Substring(7) : authHeader;
        
        if (string.IsNullOrEmpty(token))
        {
            context.Result = new UnauthorizedObjectResult(new { error = "Invalid token format" });
            return;
        }

        var principal = _jwtService.ValidateAdminToken(token);
        
        if (principal == null)
        {
            context.Result = new ObjectResult(new { error = "Invalid or expired token" }) { StatusCode = 403 };
            return;
        }

        context.HttpContext.User = principal;
    }
}
