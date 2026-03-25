using System.Security.Claims;
using AuthService.Models;

namespace AuthService.Middleware;

public class AdminAuthMiddleware
{
    private readonly RequestDelegate _next;

    public AdminAuthMiddleware(RequestDelegate next)
    {
        _next = next;
    }

    public async Task InvokeAsync(HttpContext context, Services.JwtService jwtService)
    {
        var authHeader = context.Request.Headers["Authorization"].FirstOrDefault();
        
        if (string.IsNullOrEmpty(authHeader))
        {
            context.Response.StatusCode = 401;
            await context.Response.WriteAsJsonAsync(new { error = "Authorization header required" });
            return;
        }

        var token = authHeader.StartsWith("Bearer ") ? authHeader.Substring(7) : authHeader;
        
        if (string.IsNullOrEmpty(token))
        {
            context.Response.StatusCode = 401;
            await context.Response.WriteAsJsonAsync(new { error = "Invalid token format" });
            return;
        }

        var principal = jwtService.ValidateAdminToken(token);
        
        if (principal == null)
        {
            context.Response.StatusCode = 403;
            await context.Response.WriteAsJsonAsync(new { error = "Invalid or expired token" });
            return;
        }

        context.User = principal;
        await _next(context);
    }
}

public static class PermissionMiddleware
{
    public static IApplicationBuilder UseAdminAuth(this IApplicationBuilder app)
    {
        return app.UseMiddleware<AdminAuthMiddleware>();
    }
}

public static class PermissionExtensions
{
    public static bool HasPermission(this ClaimsPrincipal user, string permission)
    {
        var permissionsClaim = user.FindFirst("permissions")?.Value;
        if (string.IsNullOrEmpty(permissionsClaim)) return false;

        var permissions = permissionsClaim.Split(',');
        return permissions.Contains("*") || permissions.Contains(permission);
    }

    public static int GetAdminId(this ClaimsPrincipal user)
    {
        var adminIdClaim = user.FindFirst("adminId")?.Value;
        return adminIdClaim != null ? int.Parse(adminIdClaim) : 0;
    }

    public static string GetRole(this ClaimsPrincipal user)
    {
        return user.FindFirst("role")?.Value ?? string.Empty;
    }
}
