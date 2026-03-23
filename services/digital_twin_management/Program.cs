using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Serilog;
using FluentValidation;
using WarehouseDigitalTwin.Models;
using WarehouseDigitalTwin.Services;
using WarehouseDigitalTwin.Validators;

var builder = WebApplication.CreateBuilder(args);

// Configure Serilog
Log.Logger = new LoggerConfiguration()
    .WriteTo.Console()
    .WriteTo.ApplicationInsights(builder.Configuration["ApplicationInsights:InstrumentationKey"], TelemetryConverter.Traces)
    .CreateLogger();

builder.Host.UseSerilog();

// Add services to the container
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new() { 
        Title = "Warehouse Digital Twin API", 
        Version = "v1",
        Description = "Azure Digital Twins management API for warehouse operations"
    });
});

// Add Azure services
builder.Services.AddAzureClients(clientBuilder =>
{
    clientBuilder.AddDigitalTwinClient(builder.Configuration.GetSection("AzureDigitalTwins"));
});

// Add FluentValidation
builder.Services.AddValidatorsFromAssemblyContaining<WarehouseDigitalTwinValidator>();

// Register custom services
builder.Services.AddSingleton<DigitalTwinManager>();
builder.Services.AddSingleton<ConfigurationService>();

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

// Configure logging
builder.Services.AddLogging(loggingBuilder =>
{
    loggingBuilder.ClearProviders();
    loggingBuilder.AddSerilog();
});

var app = builder.Build();

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(c =>
    {
        c.SwaggerEndpoint("/swagger/v1/swagger.json", "Warehouse Digital Twin API v1");
        c.RoutePrefix = "swagger";
    });
}

app.UseHttpsRedirection();
app.UseCors("AllowAll");
app.UseAuthorization();

app.MapControllers();

// Health check endpoint
app.MapGet("/health", () => new { status = "healthy", timestamp = DateTime.UtcNow });

try
{
    Log.Information("Starting Warehouse Digital Twin Service");
    app.Run();
}
catch (Exception ex)
{
    Log.Fatal(ex, "Warehouse Digital Twin Service terminated unexpectedly");
}
finally
{
    Log.CloseAndFlush();
}
