# 🏗️ **Robot Fleet System - Monorepo Architecture**

## **📁 Directory Structure**

```
robot_fleet/
├── 📦 apps/                          # Frontend Applications
│   ├── cottage_client/               # 🏠 Cottage Client Portal
│   │   ├── dashboard/              # Web interface (port 5173)
│   │   ├── ios/                   # iOS app
│   │   └── package.json
│   └── fleet_admin/                 # 🤖 Fleet Management System
│       ├── dashboard/              # Web interface (port 5174)
│       └── package.json
├── 📦 packages/                       # Shared Code
│   ├── shared-types/              # TypeScript definitions
│   ├── shared-ui/                # React components
│   ├── shared-api/               # API clients
│   └── shared-utils/              # Utility functions
├── ⚙️ services/                      # Backend Services
│   ├── fleet_control/             # Core robot orchestration
│   ├── robot_api/                 # Robot data API (port 8002)
│   └── auth/                      # Authentication service (port 8000)
├── 🔧 infrastructure/               # DevOps & Deployment
│   ├── docker-compose.yml         # Multi-service orchestration
│   ├── Dockerfile                 # Container definitions
│   ├── tools/                    # Development tools
│   └── docs/                     # Documentation
├── 📊 config/                        # Configuration
│   ├── requirements.txt           # Python dependencies
│   ├── .env.example             # Environment template
│   └── .gitignore              # Git ignore rules
└── 📚 package.json                    # Monorepo workspace config
```

## **🚀 Development Workflow**

### **1. Install All Dependencies**
```bash
npm run install:all
```

### **2. Start Development Environment**
```bash
# Start all services
npm run dev

# Start only applications
npm run dev:apps

# Start only backend services
npm run dev:services
```

### **3. Build All Projects**
```bash
npm run build
```

### **4. Run Tests**
```bash
npm run test
```

### **5. Docker Development**
```bash
# Build and start all services
npm run docker:up

# Stop all services
npm run docker:down
```

## **🏠 Applications**

### **Cottage Client Portal**
- **Purpose**: Residential robot control for homeowners
- **Port**: 5173
- **Features**: Terminal dashboard, robot monitoring, home automation
- **Users**: Cottage residents, homeowners
- **Auth**: Simple user authentication

### **Fleet Management System**
- **Purpose**: Business fleet administration for managers
- **Port**: 5174
- **Features**: Customer onboarding, fleet configuration, analytics
- **Users**: Fleet managers, customer support
- **Auth**: Role-based admin authentication

## **⚙️ Services**

### **Robot API Service** (Port 8002)
- **Purpose**: Shared robot data and control endpoints
- **Used by**: Both cottage and fleet admin
- **Features**: Robot types, status, configuration, control

### **Fleet Control Service** (Port 8001)
- **Purpose**: Core robot orchestration and task management
- **Features**: Multi-robot coordination, task scheduling, simulation
- **Used by**: Robot API for orchestration logic

### **Authentication Service** (Port 8000)
- **Purpose**: User management and security
- **Features**: Login, registration, role management, JWT tokens
- **Used by**: Both applications for authentication

## **📦 Shared Packages**

### **@robot-fleet/shared-types**
- **Purpose**: Common TypeScript definitions
- **Contains**: User, Robot, Customer, FleetConfig interfaces
- **Used by**: All applications and services

### **@robot-fleet/shared-ui**
- **Purpose**: Reusable React components
- **Contains**: StatusBadge, RobotCard, Modal, LoadingSpinner
- **Used by**: Cottage and fleet admin applications

### **@robot-fleet/shared-api**
- **Purpose**: API client utilities
- **Contains**: ApiClient, RobotApiClient, FleetApiClient
- **Used by**: Frontend applications

### **@robot-fleet/shared-utils**
- **Purpose**: Common utility functions
- **Contains**: Formatters, validators, helpers
- **Used by**: All applications

## **🔧 Infrastructure**

### **Docker Compose**
- **Multi-service orchestration** with proper networking
- **Database**: PostgreSQL for production, SQLite for development
- **Cache**: Redis for session management
- **Volumes**: Persistent data storage
- **Environment**: Proper configuration management

### **Development Tools**
- **Code quality**: ESLint, Prettier, TypeScript, Python linting
- **Testing**: Jest for frontend, Pytest for backend
- **Building**: Vite for frontend, TypeScript compilation
- **Deployment**: Docker containers, CI/CD ready

## **🎯 Benefits**

### **For Development**
- **Monorepo**: Shared dependencies, consistent tooling
- **Code reuse**: Common components and types
- **Independent deployment**: Each service can deploy separately
- **Type safety**: Shared TypeScript definitions

### **For Operations**
- **Scalability**: Microservices architecture
- **Monitoring**: Centralized logging and metrics
- **Security**: Separate authentication service
- **Reliability**: Container orchestration with health checks

### **For Business**
- **Clear separation**: Residential vs. business applications
- **Scalable growth**: Easy to add new customers/applications
- **Cost efficiency**: Shared infrastructure and services
- **Compliance**: Proper data isolation and security

## **🚀 Getting Started**

### **Prerequisites**
- Node.js 18+
- Python 3.9+
- Docker & Docker Compose
- Git

### **Quick Start**
```bash
# Clone repository
git clone <repository-url>
cd robot_fleet

# Install all dependencies
npm run install:all

# Start development environment
npm run dev

# Access applications
# Cottage Client: http://localhost:5173
# Fleet Admin: http://localhost:5174
# Robot API: http://localhost:8002
```

This monorepo architecture provides **clear separation of concerns** while enabling **code reuse** and **independent deployment** of each service! 🎉
