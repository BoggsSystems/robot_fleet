# Auth Service - C#

C# JWT Authentication Service for Robot Fleet SuperAdmin Dashboard.

## Features

- JWT Authentication with role-based permissions
- Admin user management (superadmin, support, billing, technical)
- BCrypt password hashing
- In-memory user storage (replace with database in production)
- Swagger UI documentation
- Health check endpoint

## Default Credentials

- **Username:** `admin`
- **Password:** `admin123`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/admin/login` | Authenticate admin user |
| `GET` | `/auth/admin/profile` | Get current admin profile |
| `POST` | `/auth/admin/logout` | Logout admin |
| `GET` | `/auth/admin/users` | List all admin users |
| `POST` | `/auth/admin/users` | Create new admin user |
| `GET` | `/health` | Health check |
| `GET` | `/swagger` | Swagger UI |

## Local Development

```bash
# Run locally
cd backend/services/auth_csharp
dotnet run

# Or with specific port
dotnet run --urls "http://0.0.0.0:3001"
```

## Docker Build

```bash
cd backend/services/auth_csharp

# Build image
docker build -t auth-service:latest .

# Run container
docker run -p 3001:3001 auth-service:latest
```

## Azure Deployment

### Prerequisites

- Azure CLI installed
- Docker installed
- Azure subscription

### Option 1: Manual Deployment (Windows)

```batch
cd backend/services/auth_csharp
deploy-azure.bat
```

### Option 2: Manual Deployment (Linux/Mac)

```bash
cd backend/services/auth_csharp
chmod +x deploy-azure.sh
./deploy-azure.sh
```

### Option 3: GitHub Actions (Automated)

1. Add Azure credentials to GitHub Secrets as `AZURE_CREDENTIALS`:
   ```bash
   az ad sp create-for-rbac \
     --name "github-actions-auth-service" \
     --role contributor \
     --scopes /subscriptions/{subscription-id}/resourceGroups/robot-fleet-simulator-rg \
     --sdk-auth
   ```

2. Copy the JSON output to GitHub Secrets
3. Push to `main` branch or trigger workflow manually

## Configuration

Environment variables:
- `ASPNETCORE_URLS` - Server URLs (default: `http://0.0.0.0:3001`)
- `ASPNETCORE_ENVIRONMENT` - Environment (default: `Production`)
- `Jwt__AdminSecret` - JWT signing key

## Architecture

```
┌─────────────────┐
│  Auth Service   │
│    (C# .NET 8)  │
├─────────────────┤
│  Controllers    │ ← AdminAuthController
│  Services       │ ← JwtService, AdminStore
│  Middleware     │ ← AdminAuthFilter
│  Models         │ ← AdminUser, DTOs
└─────────────────┘
```

## Migration from Node.js

This C# service replaces the Node.js auth service at `backend/services/auth/`. 
The API is fully compatible - the frontend requires no changes.

## Tech Stack

- .NET 8
- ASP.NET Core Web API
- JWT (System.IdentityModel.Tokens.Jwt)
- BCrypt (BCrypt.Net-Next)
- Swagger (Swashbuckle.AspNetCore)
- Docker
- Azure Container Apps
