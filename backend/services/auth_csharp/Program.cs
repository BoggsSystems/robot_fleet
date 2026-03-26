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
// Cosmos DB configuration
var cosmosConnectionString = Environment.GetEnvironmentVariable("COSMOS_CONNECTION_STRING") 
    ?? builder.Configuration.GetConnectionString("CosmosDb")
    ?? "AccountEndpoint=https://localhost:8081/;AccountKey=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==";

builder.Services.AddSingleton<CosmosDbService>(sp => 
    new CosmosDbService(
        cosmosConnectionString, 
        "auth-db", 
        "admin-users"
    ));
builder.Services.AddSingleton<AdminStore>();
builder.Services.AddSingleton<ClientStore>();
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
    message = "Auth & Management Service",
    version = "2.0.0",
    description = "Authentication and Client Management Service for Robot Fleet System",
    endpoints = new[]
    {
        // Auth endpoints
        "POST /auth/admin/login",
        "GET /auth/admin/profile",
        "POST /auth/admin/logout",
        "GET /auth/admin/users",
        "POST /auth/admin/users",
        // Client management endpoints
        "GET /api/admin/clients",
        "POST /api/admin/clients",
        "GET /api/admin/clients/{id}",
        "PUT /api/admin/clients/{id}",
        "DELETE /api/admin/clients/{id}",
        "GET /api/admin/dashboard/stats",
        // Health
        "GET /health"
    }
});

var port = Environment.GetEnvironmentVariable("PORT") ?? "3001";
app.Urls.Add($"http://0.0.0.0:{port}");

Console.WriteLine($"Auth Service starting on port {port}");

// Initialize stores with default data
using (var scope = app.Services.CreateScope())
{
    var adminStore = scope.ServiceProvider.GetRequiredService<AdminStore>();
    var clientStore = scope.ServiceProvider.GetRequiredService<ClientStore>();
    await adminStore.InitializeAsync();
    await clientStore.InitializeAsync();
}

app.Run();
