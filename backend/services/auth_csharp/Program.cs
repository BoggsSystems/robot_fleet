using AuthService.Controllers;
using AuthService.Services;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new Microsoft.OpenApi.Models.OpenApiInfo
    {
        Title = "Auth Service API",
        Version = "v1",
        Description = "Authentication and authorization service for Robot Fleet System"
    });
});

// Add CORS
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

// Register custom services
builder.Services.AddSingleton<AdminStore>();
builder.Services.AddSingleton<JwtService>();
builder.Services.AddScoped<AdminAuthFilter>();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(c =>
    {
        c.SwaggerEndpoint("/swagger/v1/swagger.json", "Auth Service API v1");
    });
}

app.UseCors("AllowAll");
app.UseAuthorization();
app.MapControllers();

// Health check endpoint
app.MapGet("/health", () => new
{
    status = "healthy",
    service = "auth",
    timestamp = DateTime.UtcNow
});

// Root endpoint
app.MapGet("/", () => new
{
    message = "Auth Service",
    version = "1.0.0",
    endpoints = new[]
    {
        "POST /auth/admin/login",
        "GET /auth/admin/profile",
        "POST /auth/admin/logout",
        "GET /auth/admin/users",
        "POST /auth/admin/users",
        "GET /health"
    }
});

var port = Environment.GetEnvironmentVariable("PORT") ?? "3001";
app.Urls.Add($"http://0.0.0.0:{port}");

Console.WriteLine($"Auth Service starting on port {port}");
app.Run();
