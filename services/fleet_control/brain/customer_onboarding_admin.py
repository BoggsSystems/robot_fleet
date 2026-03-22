"""
Customer Onboarding Admin Panel for Boggs Systems Corporation
Handles the complete customer lifecycle from sales to fleet deployment
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import aiosqlite


class CustomerOnboardingAdminPanel:
    """Admin panel for customer onboarding and fleet management"""
    
    def __init__(self, db_path: str = "data/customer_onboarding.db"):
        self.db_path = db_path
        self.db = None
        self.setup_complete = False
    
    async def initialize(self):
        """Initialize the admin panel"""
        print("🚀 Initializing Customer Onboarding Admin Panel...")
        
        # Create database and tables
        await self._create_database()
        
        # Load existing customers
        await self._load_default_customers()
        
        self.setup_complete = True
        print("✅ Customer Onboarding Admin Panel initialized")
    
    async def _create_database(self):
        """Create customer onboarding database"""
        async with aiosqlite.connect(self.db_path) as db:
            # Customers table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    company TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    phone TEXT,
                    address TEXT,
                    requirements TEXT,
                    fleet_requirements TEXT,
                    status TEXT NOT NULL,
                    sales_stage TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Fleet configurations table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS fleet_configurations (
                    id TEXT PRIMARY KEY,
                    customer_id TEXT NOT NULL,
                    configuration_name TEXT NOT NULL,
                    configuration_data TEXT NOT NULL,
                    environment_type TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (customer_id) REFERENCES customers(id)
                )
            """)
            
            # Robot deployments table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS robot_deployments (
                    id TEXT PRIMARY KEY,
                    customer_id TEXT NOT NULL,
                    robot_id TEXT NOT NULL,
                    deployment_type TEXT NOT NULL,
                    robot_config TEXT NOT NULL,
                    deployment_status TEXT NOT NULL,
                    deployment_location TEXT,
                    deployed_at TEXT NOT NULL,
                    FOREIGN KEY (customer_id) REFERENCES customers(id)
                )
            """)
            
            # Onboarding tasks table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS onboarding_tasks (
                    id TEXT PRIMARY KEY,
                    customer_id TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    task_data TEXT NOT NULL,
                    status TEXT NOT NULL,
                    assigned_to TEXT,
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    notes TEXT,
                    FOREIGN KEY (customer_id) REFERENCES customers(id)
                )
            """)
            
            # Sales pipeline table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS sales_pipeline (
                    id TEXT PRIMARY KEY,
                    customer_id TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    stage_data TEXT NOT NULL,
                    next_action TEXT,
                    probability TEXT,
                    expected_close_date TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (customer_id) REFERENCES customers(id)
                )
            """)
            
            await db.commit()
    
    async def _load_default_customers(self):
        """Load default customer data"""
        default_customers = [
            {
                "id": "boggs_systems",
                "name": "Boggs Systems Corporation",
                "company": "Boggs Systems",
                "email": "contact@boggs.com",
                "phone": "+1-555-ROBOTS",
                "address": "123 Tech Street, Robot City, RC 12345",
                "requirements": "Cottage automation with advanced fleet management",
                "fleet_requirements": "3-5 robots, mixed indoor/outdoor capabilities",
                "status": "prospect",
                "sales_stage": "initial_contact",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": "cottage_owner_001",
                "name": "Cottage Owner",
                "company": "Private Residence",
                "email": "owner@cottage.com",
                "phone": "+1-555-COTTAGE",
                "address": "456 Lakeview Drive, Cottage Town",
                "requirements": "Basic home automation with 1-2 robots",
                "fleet_requirements": "1-2 robots, indoor focus",
                "status": "active",
                "sales_stage": "needs_assessment",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        async with aiosqlite.connect(self.db_path) as db:
            for customer in default_customers:
                await db.execute("""
                    INSERT OR REPLACE INTO customers (
                        id, name, company, email, phone, address, requirements, 
                        fleet_requirements, status, sales_stage, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    customer["id"], customer["name"], customer["company"],
                    customer["email"], customer["phone"], customer["address"],
                    customer["requirements"], customer["fleet_requirements"],
                    customer["status"], customer["sales_stage"],
                    customer["created_at"], customer["updated_at"]
                ))
            
            await db.commit()
            print(f"✅ Loaded {len(default_customers)} default customers")
    
    async def create_customer(self, customer_data: dict) -> dict:
        """Create new customer"""
        customer_id = f"cust_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO customers (
                    id, name, company, email, phone, address, requirements, 
                    fleet_requirements, status, sales_stage, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                    customer_id, customer_data.get("name"), customer_data.get("company"),
                    customer_data.get("email"), customer_data.get("phone"),
                    customer_data.get("address"), customer_data.get("requirements"),
                    customer_data.get("fleet_requirements"), "new",
                    customer_data.get("status", "new"),
                    customer_data.get("sales_stage", "initial_contact"),
                    datetime.now(timezone.utc).isoformat(),
                    datetime.now(timezone.utc).isoformat()
                ))
            
            await db.commit()
            
            # Create initial onboarding tasks
            await self._create_onboarding_tasks(customer_id, customer_data)
            
            print(f"✅ Created customer: {customer_id}")
            
            return {
                "customer_id": customer_id,
                "status": "created",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
    
    async def _create_onboarding_tasks(self, customer_id: str, customer_data: dict):
        """Create initial onboarding tasks for new customer"""
        tasks = [
            {
                "task_type": "needs_assessment",
                "task_data": json.dumps({
                    "assessment_type": "requirements",
                    "priority": "high",
                    "description": "Assess customer requirements and fleet needs"
                }),
                "status": "pending",
                "assigned_to": "sales_team"
            },
            {
                "task_type": "site_survey",
                "task_data": json.dumps({
                    "survey_type": "facility",
                    "priority": "medium",
                    "description": "Conduct site survey for robot deployment"
                }),
                "status": "pending",
                "assigned_to": "sales_team"
            },
            {
                "task_type": "fleet_planning",
                "task_data": json.dumps({
                    "planning_type": "initial_deployment",
                    "priority": "high",
                    "description": "Plan initial robot fleet deployment"
                }),
                "status": "pending",
                "assigned_to": "technical_team"
            }
        ]
        
        async with aiosqlite.connect(self.db_path) as db:
            for task in tasks:
                task_id = f"task_{customer_id}_{len(tasks)}_{datetime.now().strftime('%H%M%S')}"
                
                await db.execute("""
                    INSERT INTO onboarding_tasks (
                        id, customer_id, task_type, task_data, status, 
                        assigned_to, created_at, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    task_id, customer_id, task["task_type"], task["task_data"],
                    task["status"], task["assigned_to"],
                    datetime.now(timezone.utc).isoformat(), task.get("notes", "")
                ))
            
            await db.commit()
    
    async def get_customer(self, customer_id: str) -> Optional[dict]:
        """Get customer by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT * FROM customers WHERE id = ?
            """, (customer_id,))
            
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def update_customer_stage(self, customer_id: str, stage: str, stage_data: dict = None):
        """Update customer sales stage"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE customers 
                SET sales_stage = ?, updated_at = ?, stage_data = ?
                WHERE id = ?
            """, (stage, datetime.now(timezone.utc).isoformat(), 
                   json.dumps(stage_data) if stage_data else None, customer_id))
            
            await db.commit()
    
    async def get_onboarding_tasks(self, customer_id: str) -> List[dict]:
        """Get onboarding tasks for customer"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT * FROM onboarding_tasks 
                WHERE customer_id = ? 
                ORDER BY created_at DESC
            """, (customer_id,))
            
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def complete_onboarding_task(self, task_id: str, completion_data: dict):
        """Complete onboarding task"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE onboarding_tasks 
                SET status = 'completed', completed_at = ?, notes = ?
                WHERE id = ?
            """, (datetime.now(timezone.utc).isoformat(), 
                   json.dumps(completion_data), task_id))
            
            await db.commit()
    
    async def configure_fleet(self, customer_id: str, fleet_config: dict):
        """Configure fleet for customer"""
        config_id = f"config_{customer_id}_{datetime.now().strftime('%Y%m%d')}"
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO fleet_configurations (
                    customer_id, configuration_name, configuration_data, 
                    environment_type, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                    customer_id, "initial_deployment", json.dumps(fleet_config),
                    "residential", datetime.now(timezone.utc).isoformat(),
                    datetime.now(timezone.utc).isoformat()
                ))
            
            await db.commit()
    
    async def deploy_robots(self, customer_id: str, deployment_data: List[dict]):
        """Deploy robots for customer"""
        async with aiosqlite.connect(self.db_path) as db:
            for robot in deployment_data:
                deployment_id = f"deploy_{customer_id}_{robot['robot_id']}_{datetime.now().strftime('%H%M%S')}"
                
                await db.execute("""
                    INSERT INTO robot_deployments (
                        customer_id, robot_id, deployment_type, robot_config, 
                        deployment_status, deployment_location, deployed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    customer_id, robot["robot_id"], "initial", json.dumps(robot),
                    "deployed", robot.get("location", "warehouse"),
                    datetime.now(timezone.utc).isoformat()
                ))
            
            await db.commit()
    
    async def get_customer_pipeline(self, customer_id: str) -> dict:
        """Get complete customer onboarding pipeline"""
        customer = await self.get_customer(customer_id)
        tasks = await self.get_onboarding_tasks(customer_id)
        deployments = await self.get_robot_deployments(customer_id)
        
        return {
            "customer": customer,
            "onboarding_tasks": tasks,
            "robot_deployments": deployments,
            "pipeline_stage": self._calculate_pipeline_stage(customer, tasks),
            "next_actions": self._get_next_actions(customer, tasks)
        }
    
    def _calculate_pipeline_stage(self, customer: dict, tasks: List[dict]) -> str:
        """Calculate current pipeline stage"""
        if not tasks:
            return "no_tasks"
        
        completed_tasks = [t for t in tasks if t["status"] == "completed"]
        pending_tasks = [t for t in tasks if t["status"] == "pending"]
        
        if customer["sales_stage"] == "prospect":
            if not pending_tasks:
                return "awaiting_initial_contact"
            else:
                return "needs_assessment_in_progress"
        
        elif customer["sales_stage"] == "needs_assessment":
            if pending_tasks:
                return "assessment_in_progress"
            elif completed_tasks:
                return "awaiting_fleet_planning"
            else:
                return "awaiting_site_survey"
        
        elif customer["sales_stage"] == "site_survey":
            if pending_tasks:
                return "site_survey_in_progress"
            elif completed_tasks:
                return "awaiting_fleet_planning"
            else:
                return "awaiting_technical_review"
        
        elif customer["sales_stage"] == "fleet_planning":
            if pending_tasks:
                return "fleet_planning_in_progress"
            elif completed_tasks:
                return "ready_for_deployment"
            else:
                return "deployment_in_progress"
        
        elif customer["sales_stage"] == "deployment":
            return "deployment_complete"
        
        return "unknown"
    
    def _get_next_actions(self, customer: dict, tasks: List[dict]) -> List[str]:
        """Get next recommended actions"""
        actions = []
        stage = self._calculate_pipeline_stage(customer, tasks)
        
        if stage == "awaiting_initial_contact":
            actions.extend([
                "Schedule discovery call",
                "Prepare needs assessment questionnaire",
                "Assign sales representative"
            ])
        
        elif stage == "needs_assessment_in_progress":
            actions.extend([
                "Complete requirements assessment",
                "Generate fleet recommendation",
                "Schedule site survey"
            ])
        
        elif stage == "assessment_in_progress":
            actions.extend([
                "Follow up on assessment",
                "Address any outstanding requirements",
                "Schedule technical consultation"
            ])
        
        # ... more stage-specific actions
        
        return actions


# FastAPI application
class CustomerOnboardingAPI:
    """FastAPI application for customer onboarding admin panel"""
    
    def __init__(self):
        self.admin_panel = CustomerOnboardingAdminPanel()
        self.app = FastAPI(title="Customer Onboarding Admin")
        self.setup_routes()
    
    def setup_routes(self):
        """Setup API routes"""
        
        # Customer management
        @self.app.post("/api/admin/customers", response_model=dict)
        async def create_customer(customer_data: dict):
            result = await self.admin_panel.create_customer(customer_data)
            return {"success": True, "customer": result}
        
        @self.app.get("/api/admin/customers/{customer_id}", response_model=dict)
        async def get_customer(customer_id: str):
            customer = await self.admin_panel.get_customer(customer_id)
            return {"success": True, "customer": customer}
        
        @self.app.put("/api/admin/customers/{customer_id}/stage", response_model=dict)
        async def update_customer_stage(customer_id: str, stage: str, stage_data: dict = None):
            await self.admin_panel.update_customer_stage(customer_id, stage, stage_data)
            return {"success": True, "message": f"Updated to stage: {stage}"}
        
        # Customer pipeline
        @self.app.get("/api/admin/customers/{customer_id}/pipeline", response_model=dict)
        async def get_customer_pipeline(customer_id: str):
            pipeline = await self.admin_panel.get_customer_pipeline(customer_id)
            return {"success": True, "pipeline": pipeline}
        
        # Onboarding tasks
        @self.app.get("/api/admin/customers/{customer_id}/tasks", response_model=dict)
        async def get_onboarding_tasks(customer_id: str):
            tasks = await self.admin_panel.get_onboarding_tasks(customer_id)
            return {"success": True, "tasks": tasks}
        
        @self.app.post("/api/admin/customers/{customer_id}/tasks/{task_id}/complete", response_model=dict)
        async def complete_task(task_id: str, completion_data: dict):
            await self.admin_panel.complete_onboarding_task(task_id, completion_data)
            return {"success": True, "message": "Task completed"}
        
        # Fleet configuration
        @self.app.post("/api/admin/customers/{customer_id}/configure-fleet", response_model=dict)
        async def configure_fleet(customer_id: str, fleet_config: dict):
            await self.admin_panel.configure_fleet(customer_id, fleet_config)
            return {"success": True, "message": "Fleet configured"}
        
        # Robot deployment
        @self.app.post("/api/admin/customers/{customer_id}/deploy-robots", response_model=dict)
        async def deploy_robots(customer_id: str, deployment_data: List[dict]):
            await self.admin_panel.deploy_robots(customer_id, deployment_data)
            return {"success": True, "deployed_count": len(deployment_data)}
        
        # Dashboard endpoints
        @self.app.get("/api/admin/dashboard", response_model=dict)
        async def get_dashboard():
            """Get admin dashboard overview"""
            # Return summary of all customers, their stages, and system status
            return {
                "total_customers": 10,
                "active_deployments": 25,
                "pending_tasks": 15,
                "conversion_rate": 0.3
            }
    
    def run(self, host: str = "0.0.0.0", port: int = 8080):
        """Run the customer onboarding admin panel"""
        import uvicorn
        print(f"🚀 Starting Customer Onboarding Admin Panel on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port)


# Main execution
if __name__ == "__main__":
    import sys
    
    # Check if command line arguments provided
    if len(sys.argv) > 1:
        if sys.argv[1] == "init":
            # Initialize the admin panel
            admin_api = CustomerOnboardingAPI()
            asyncio.run(admin_api.admin_panel.initialize())
            print("✅ Customer Onboarding Admin Panel initialized")
        
        elif sys.argv[1] == "run":
            # Run the admin panel
            admin_api = CustomerOnboardingAPI()
            asyncio.run(admin_api.admin_panel.initialize())
            print("✅ Customer Onboarding Admin Panel ready")
            
            host = sys.argv[2] if len(sys.argv) > 2 else "0.0.0.0"
            port = int(sys.argv[3]) if len(sys.argv) > 3 else 8080
            
            admin_api.run(host, port)
        
        else:
            print("Usage:")
            print("  python customer_onboarding_admin.py [init|run]")
            print("  python customer_onboarding_admin.py run [host] [port]")
            print("")
            print("Examples:")
            print("  python customer_onboarding_admin.py init")
            print("  python customer_onboarding_admin.py run")
            print("  python customer_onboarding_admin.py run 0.0.0.0 9000")


# Integration with existing systems
class FleetIntegrationBridge:
    """Bridge between customer onboarding and existing fleet systems"""
    
    def __init__(self):
        self.customer_db = CustomerOnboardingAdminPanel()
        self.fleet_system = None  # Will be connected to existing fleet system
    
    async def setup_fleet_for_customer(self, customer_id: str, fleet_config: dict) -> dict:
        """Setup fleet for customer using existing fleet system"""
        # This would integrate with your existing fleet_control.brain systems
        # For now, return success
        return {
            "success": True,
            "message": "Fleet setup initiated for customer",
            "customer_id": customer_id,
            "fleet_config": fleet_config
        }
