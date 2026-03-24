"""
Setup script for Azure Digital Twin integration with RAG system.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from .multi_tenant_rag import MultiTenantRAG
from .azure_digital_twin_rag import EnhancedRAGWithDigitalTwin
from .digital_twin_enhanced_intent import DigitalTwinEnhancedIntentService


class DigitalTwinRAGSetup:
    """Setup and manage Azure Digital Twin integration with RAG"""
    
    def __init__(self, adt_endpoint: Optional[str] = None):
        self.adt_endpoint = adt_endpoint
        self.base_path = Path("data/rag")
        self.setup_complete = False
        
        # Initialize components
        self.rag_system = None
        self.dtw_integration = None
        self.enhanced_intent_service = None
    
    async def setup_digital_twin_rag(self, client_id: str = "cot_12345678") -> Dict[str, Any]:
        """Setup Azure Digital Twin integration with RAG system"""
        print("🔗 Setting up Azure Digital Twin RAG Integration...")
        
        try:
            # 1. Create directory structure
            await self._create_directory_structure()
            
            # 2. Initialize RAG system
            self.rag_system = await self._initialize_rag_system()
            
            # 3. Initialize Digital Twin integration
            self.dtw_integration = EnhancedRAGWithDigitalTwin(self.rag_system, self.adt_endpoint)
            
            # 4. Initialize enhanced intent service
            self.enhanced_intent_service = DigitalTwinEnhancedIntentService(self.rag_system, self.adt_endpoint)
            
            # 5. Initialize Digital Twin integration
            await self.enhanced_intent_service.initialize(client_id)
            
            # 6. Create cottage Digital Twins
            await self.dtw_integration.create_cottage_digital_twins(client_id)
            
            # 7. Setup monitoring
            await self._setup_monitoring(client_id)
            
            self.setup_complete = True
            
            return {
                "success": True,
                "client_id": client_id,
                "rag_system": "initialized",
                "digital_twin_integration": "active",
                "enhanced_intent_service": "ready",
                "cottage_digital_twins": "created",
                "setup_time": datetime.now(timezone.utc).isoformat(),
                "features": {
                    "real_time_search": self.dtw_integration.enhanced_search is not None,
                    "telemetry_updates": hasattr(self.dtw_integration, 'updater'),
                    "enhanced_intent_parsing": True,
                    "digital_twin_sync": True
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stage": self._get_error_stage(e),
                "setup_time": datetime.now(timezone.utc).isoformat()
            }
    
    async def _create_directory_structure(self) -> None:
        """Create necessary directory structure"""
        print("📁 Creating directory structure...")
        
        directories = [
            self.base_path,
            self.base_path / "clients",
            self.base_path / "clients" / "cot_12345678",
            self.base_path / "clients" / "cot_12345678" / "personal",
            self.base_path / "clients" / "cot_12345678" / "history",
            self.base_path / "indexes",
            self.base_path / "digital_twin",
            self.base_path / "digital_twin" / "telemetry",
            self.base_path / "digital_twin" / "models"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        print("✅ Directory structure created")
    
    async def _initialize_rag_system(self) -> MultiTenantRAG:
        """Initialize the RAG system"""
        print("🧠 Initializing RAG system...")
        
        rag_system = MultiTenantRAG(
            base_db_path=str(self.base_path / "shared_knowledge.db"),
            client_storage_path=str(self.base_path / "clients")
        )
        
        await rag_system.initialize()
        print("✅ RAG system initialized")
        return rag_system
    
    async def _setup_monitoring(self, client_id: str) -> None:
        """Setup monitoring for Digital Twin integration"""
        print("📊 Setting up monitoring...")
        
        # Create monitoring configuration
        monitoring_config = {
            "client_id": client_id,
            "digital_twin_endpoint": self.adt_endpoint,
            "monitoring_enabled": True,
            "telemetry_subscriptions": [
                "zone_temperature",
                "zone_humidity", 
                "zone_occupancy",
                "robot_battery",
                "robot_status",
                "robot_location"
            ],
            "sync_interval_minutes": 5,
            "alert_thresholds": {
                "low_battery": 20.0,
                "high_temperature": 30.0,
                "high_humidity": 80.0
            }
        }
        
        # Save monitoring config
        config_path = self.base_path / "digital_twin" / "monitoring_config.json"
        with open(config_path, 'w') as f:
            json.dump(monitoring_config, f, indent=2)
        
        print("✅ Monitoring setup complete")
    
    def _get_error_stage(self, error: Exception) -> str:
        """Determine which stage failed based on error"""
        error_str = str(error).lower()
        
        if "directory" in error_str or "path" in error_str:
            return "directory_creation"
        elif "rag" in error_str or "database" in error_str:
            return "rag_initialization"
        elif "azure" in error_str or "digital twin" in error_str:
            return "digital_twin_integration"
        elif "intent" in error_str:
            return "intent_service_initialization"
        else:
            return "unknown"
    
    async def test_integration(self, client_id: str = "cot_12345678") -> Dict[str, Any]:
        """Test the Digital Twin RAG integration"""
        print("🧪 Testing Digital Twin RAG Integration...")
        
        if not self.setup_complete:
            return {
                "success": False,
                "error": "Integration not setup complete"
            }
        
        test_results = {
            "rag_search_test": await self._test_rag_search(client_id),
            "enhanced_intent_test": await self._test_enhanced_intent_parsing(client_id),
            "digital_twin_sync_test": await self._test_digital_twin_sync(client_id),
            "real_time_context_test": await self._test_real_time_context(client_id)
        }
        
        all_passed = all(result["success"] for result in test_results.values())
        
        return {
            "success": all_passed,
            "test_results": test_results,
            "overall_status": "PASS" if all_passed else "FAIL",
            "test_time": datetime.now(timezone.utc).isoformat()
        }
    
    async def _test_rag_search(self, client_id: str) -> Dict[str, Any]:
        """Test RAG search functionality"""
        try:
            # Test search query
            query = "Scan kitchen for QR codes"
            
            if hasattr(self.dtw_integration, 'search') and self.dtw_integration.search:
                results = await self.dtw_integration.search(client_id, query, limit=3)
                
                return {
                    "success": True,
                    "query": query,
                    "results_count": len(results),
                    "has_digital_twin_context": any("twin_context" in result for result in results),
                    "top_result": results[0] if results else None
                }
            else:
                # Fallback to standard RAG search
                results = await self.rag_system.search(client_id, query, limit=3)
                
                return {
                    "success": True,
                    "query": query,
                    "results_count": len(results),
                    "fallback_mode": True,
                    "top_result": results[0] if results else None
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    async def _test_enhanced_intent_parsing(self, client_id: str) -> Dict[str, Any]:
        """Test enhanced intent parsing"""
        try:
            query = "Scan kitchen for QR codes"
            requested_by = "user@ios_app"
            
            intent = await self.enhanced_intent_service.parse_request(
                request_text=query,
                requested_by=requested_by,
                context={"currentLocation": "living_room"}
            )
            
            return {
                "success": True,
                "query": query,
                "parsed_intent": {
                    "mission_type": intent.mission_type,
                    "source_zone": intent.source_zone,
                    "required_capabilities": intent.required_capabilities,
                    "confidence_score": intent.confidence_score,
                    "has_real_time_considerations": len(intent.real_time_considerations) > 0
                },
                "real_time_considerations": intent.real_time_considerations
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    async def _test_digital_twin_sync(self, client_id: str) -> Dict[str, Any]:
        """Test Digital Twin synchronization"""
        try:
            if not self.dtw_integration.adt_client:
                return {
                    "success": True,
                    "status": "mock_mode",
                    "message": "Azure Digital Twins not available - using mock data"
                }
            
            # Test sync of a specific twin
            twin_id = "zone_kitchen"
            await self.dtw_integration.dtw_integration.sync_digital_twin_to_rag(client_id, twin_id)
            
            return {
                "success": True,
                "twin_id": twin_id,
                "sync_status": "completed"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _test_real_time_context(self, client_id: str) -> Dict[str, Any]:
        """Test real-time context retrieval"""
        try:
            context = await self.enhanced_intent_service._get_real_time_context(client_id)
            
            return {
                "success": True,
                "context_available": len(context) > 0,
                "zones_count": len(context.get("zones", {})),
                "robots_count": len(context.get("robots", {})),
                "sample_zone": list(context.get("zones", {}).values())[0] if context.get("zones") else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def simulate_real_time_updates(self, client_id: str = "cot_12345678") -> Dict[str, Any]:
        """Simulate real-time Digital Twin updates"""
        print("📡 Simulating real-time Digital Twin updates...")
        
        updates = [
            {
                "twin_id": "zone_kitchen",
                "telemetry": {
                    "temperature": 23.5,
                    "humidity": 48.0,
                    "occupancy": 1,
                    "lighting_level": 850,
                    "noise_level": 42
                }
            },
            {
                "twin_id": "zone_living_room",
                "telemetry": {
                    "temperature": 21.0,
                    "humidity": 52.0,
                    "occupancy": 0,
                    "lighting_level": 600,
                    "noise_level": 38
                }
            },
            {
                "twin_id": "robot_quadruped_001",
                "telemetry": {
                    "status": "active",
                    "battery_level": 82.0,
                    "current_zone": "kitchen",
                    "current_task": "patrol"
                }
            }
        ]
        
        results = []
        for update in updates:
            try:
                await self.enhanced_intent_service.simulate_telemetry_update(
                    update["twin_id"], 
                    update["telemetry"]
                )
                results.append({
                    "twin_id": update["twin_id"],
                    "success": True,
                    "telemetry": update["telemetry"]
                })
            except Exception as e:
                results.append({
                    "twin_id": update["twin_id"],
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "success": all(r["success"] for r in results),
            "updates_sent": len(updates),
            "successful_updates": sum(1 for r in results if r["success"]),
            "results": results,
            "simulation_time": datetime.now(timezone.utc).isoformat()
        }
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get current integration status"""
        status = {
            "setup_complete": self.setup_complete,
            "components": {
                "rag_system": self.rag_system is not None,
                "digital_twin_integration": self.dtw_integration is not None,
                "enhanced_intent_service": self.enhanced_intent_service is not None
            },
            "azure_connection": {
                "endpoint_configured": self.adt_endpoint is not None,
                "client_available": self.dtw_integration.dtw_integration.adt_client is not None if self.dtw_integration else False
            },
            "features": {
                "real_time_search": self.dtw_integration.enhanced_search is not None if self.dtw_integration else False,
                "telemetry_updates": hasattr(self.dtw_integration, 'updater') if self.dtw_integration else False,
                "enhanced_intent_parsing": self.enhanced_intent_service is not None
            }
        }
        
        return status


# Main setup function
async def setup_digital_twin_rag_integration(adt_endpoint: Optional[str] = None, 
                                           client_id: str = "cot_12345678") -> Dict[str, Any]:
    """Main setup function for Digital Twin RAG integration"""
    setup = DigitalTwinRAGSetup(adt_endpoint)
    return await setup.setup_digital_twin_rag(client_id)


# Test function
async def test_digital_twin_rag_integration(adt_endpoint: Optional[str] = None,
                                           client_id: str = "cot_12345678") -> Dict[str, Any]:
    """Test the Digital Twin RAG integration"""
    setup = DigitalTwinRAGSetup(adt_endpoint)
    
    # First setup
    setup_result = await setup.setup_digital_twin_rag(client_id)
    if not setup_result["success"]:
        return setup_result
    
    # Then test
    test_result = await setup.test_integration(client_id)
    
    return {
        "setup": setup_result,
        "test": test_result,
        "overall_success": setup_result["success"] and test_result["success"]
    }


# Demo function
async def demo_digital_twin_rag(adt_endpoint: Optional[str] = None,
                               client_id: str = "cot_12345678") -> Dict[str, Any]:
    """Demo the Digital Twin RAG integration"""
    print("🚀 Starting Digital Twin RAG Demo")
    print("=" * 60)
    
    # Setup
    setup = DigitalTwinRAGSetup(adt_endpoint)
    setup_result = await setup.setup_digital_twin_rag(client_id)
    
    if not setup_result["success"]:
        print(f"❌ Setup failed: {setup_result.get('error')}")
        return setup_result
    
    print(f"✅ Setup complete for client: {client_id}")
    print(f"🔧 Features: {setup_result.get('features', {})}")
    
    # Test integration
    print("\n🧪 Testing integration...")
    test_result = await setup.test_integration(client_id)
    
    print(f"📊 Test Status: {test_result.get('overall_status', 'UNKNOWN')}")
    for test_name, result in test_result.get("test_results", {}).items():
        status = "✅" if result["success"] else "❌"
        print(f"  {status} {test_name}: {result.get('error', 'PASS')}")
    
    # Demo real-time updates
    print("\n📡 Simulating real-time updates...")
    update_result = await setup.simulate_real_time_updates(client_id)
    print(f"📊 Updates: {update_result['successful_updates']}/{update_result['updates_sent']} successful")
    
    # Demo enhanced intent parsing
    print("\n🧠 Demo enhanced intent parsing...")
    query = "Scan kitchen for QR codes"
    intent = await setup.enhanced_intent_service.parse_request(
        request_text=query,
        requested_by="user@ios_app",
        context={"currentLocation": "living_room"}
    )
    
    print(f"📝 Query: {query}")
    print(f"🎯 Mission Type: {intent.mission_type}")
    print(f"📍 Source Zone: {intent.source_zone}")
    print(f"🔧 Required Capabilities: {intent.required_capabilities}")
    print(f"💡 Confidence: {intent.confidence_score:.2f}")
    print(f"⚡ Real-time Considerations: {len(intent.real_time_considerations)}")
    for consideration in intent.real_time_considerations:
        print(f"   • {consideration}")
    
    # Get recommendations
    print("\n💡 Getting real-time recommendations...")
    recommendations = await setup.enhanced_intent_service.get_real_time_mission_recommendations(client_id)
    
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"🏆 Recommendation {i}: {rec['zone_name']}")
        for mission in rec.get("recommended_missions", []):
            print(f"   • {mission['mission_type']}: {mission['reason']}")
        print(f"   🤖 Best Robot: {rec['best_robot']['name']} ({rec['best_robot']['battery_level']}% battery)")
    
    print("\n" + "=" * 60)
    print("✅ Digital Twin RAG Demo Complete!")
    
    return {
        "setup": setup_result,
        "test": test_result,
        "updates": update_result,
        "intent_parsing": {
            "query": query,
            "mission_type": intent.mission_type,
            "confidence": intent.confidence_score,
            "real_time_considerations": intent.real_time_considerations
        },
        "recommendations": recommendations[:3],
        "demo_time": datetime.now(timezone.utc).isoformat()
    }


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_digital_twin_rag())
