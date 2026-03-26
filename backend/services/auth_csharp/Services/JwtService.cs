using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using Microsoft.IdentityModel.Tokens;
using AuthService.Models;

namespace AuthService.Services;

public class JwtService
{
    private readonly IConfiguration _configuration;
    private readonly string _adminJwtSecret;

    public JwtService(IConfiguration configuration)
    {
        _configuration = configuration;
        // Read from JWT_SECRET environment variable (32+ chars for HS256)
        _adminJwtSecret = configuration["JWT_SECRET"] ?? "your-super-secret-256-bit-jwt-signing-key-minimum-32-chars";
    }

    public string GenerateAdminToken(AdminUser admin)
    {
        var securityKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_adminJwtSecret));
        var credentials = new SigningCredentials(securityKey, SecurityAlgorithms.HmacSha256);

        var claims = new[]
        {
            new Claim("adminId", admin.Id.ToString()),
            new Claim("username", admin.Username),
            new Claim("role", admin.Role.ToString().ToLower()),
            new Claim("permissions", string.Join(",", admin.Permissions))
        };

        var token = new JwtSecurityToken(
            claims: claims,
            expires: DateTime.Now.AddHours(8),
            signingCredentials: credentials
        );

        return new JwtSecurityTokenHandler().WriteToken(token);
    }

    public ClaimsPrincipal? ValidateAdminToken(string token)
    {
        try
        {
            var tokenHandler = new JwtSecurityTokenHandler();
            var key = Encoding.UTF8.GetBytes(_adminJwtSecret);

            tokenHandler.ValidateToken(token, new TokenValidationParameters
            {
                ValidateIssuerSigningKey = true,
                IssuerSigningKey = new SymmetricSecurityKey(key),
                ValidateIssuer = false,
                ValidateAudience = false,
                ClockSkew = TimeSpan.Zero
            }, out SecurityToken validatedToken);

            var jwtToken = (JwtSecurityToken)validatedToken;
            var identity = new ClaimsIdentity(jwtToken.Claims, "Jwt");
            return new ClaimsPrincipal(identity);
        }
        catch
        {
            return null;
        }
    }
}
