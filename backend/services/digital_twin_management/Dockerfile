FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 80

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy project file
COPY ["WarehouseDigitalTwin.csproj", "./"]

# Restore dependencies
RUN dotnet restore "WarehouseDigitalTwin.csproj"

# Copy all source files
COPY . .

# Build the application
RUN dotnet build "WarehouseDigitalTwin.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "WarehouseDigitalTwin.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .

# Set environment variables
ENV ASPNETCORE_URLS=http://+:80
ENV ASPNETCORE_ENVIRONMENT=Production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost/health || exit 1

ENTRYPOINT ["dotnet", "WarehouseDigitalTwin.dll"]
