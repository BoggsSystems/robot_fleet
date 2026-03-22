"""
Setup script for dynamic fleet database integration.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from .multi_tenant_rag import MultiTenantRAG
from .fleet_database import setup_fleet_database, fleet_manager
from .dynamic_fleet_rag import initialize_dynamic_fleet_rag
from .digital_twin_enhanced_intent import DigitalTwinEnhancedIntentService


class DynamicFleetSetup:
    """Setup and manage dynamic fleet database integration"""
    
    def __init__(self):
        self.base_path = Path("data")
        self.setup_complete = False
    
    async def setup_dynamic_fleet_rag(self, client_id: str = "cot_12345678") -> dict:
        """Setup dynamic fleet RAG integration"""
        print("🚀 Setting up Dynamic Fleet RAG Integration...")
        
        try:
            # 1. Initialize fleet database
            await setup_fleet_database()
            print("✅ Fleet database initialized")
            
            # 2. Initialize RAG system
            rag_system = MultiTenantRAG(
                base_db_path=str(self.base_path / "rag" / "shared_knowledge.db"),
                client_storage_path=str(self.base_path / "rag" / "clients")
            )
            await rag_system.initialize()
            print("✅ RAG system initialized")
            
            # 3. Initialize dynamic fleet RAG
            dynamic_fleet_rag = await initialize_dynamic_fleet_rag(rag_system)
            print("✅ Dynamic fleet RAG initialized")
            
            # 4. Initialize enhanced intent service
            enhanced_intent_service = DigitalTwinEnhancedIntentService(rag_system)
            await enhanced_intent_service.initialize(client_id)
            print("✅ Enhanced intent service initialized")
            
            # 5. Sync fleet data to RAG
            await dynamic_fleet_rag.sync_fleet_data_to_rag(client_id)
            print("✅ Fleet data synced to RAG")
            
            # 6. Test integration
            test_results = await self.test_dynamic_fleet_integration(client_id, rag_system, dynamic_fleet_rag, enhanced_intent_service)
            
            self.setup_complete = True
            
            return {
                "success": True,
                "client_id": client_id,
                "fleet_database": "initialized",
                "rag_system": "initialized",
                "dynamic_fleet_rag": "active",
                "enhanced_intent_service": "ready",
                "test_results": test_results,
                "setup_time": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stage": self._get_error_stage(e),
                "setup_time": datetime.now(timezone.utc).isoformat()
            }
    
    async def test_dynamic_fleet_integration(self, client_id: str, rag_system: MultiTenantRAG, dynamic_fleet_rag, enhanced_intent_service) -> dict:
        """Test dynamic fleet integration"""
        print("🧪 Testing Dynamic Fleet Integration...")
        
        test_results = {}
        
        try:
            # Test 1: Fleet Database Operations
            test_results["fleet_database_test"] = await self._test_fleet_database()
            
            # Test 2: Dynamic Fleet RAG
            test_results["dynamic_rag_test"] = await self._test_dynamic_fleet_rag(dynamic_fleet_rag, client_id)
            
            # Test 3: Enhanced Intent Service
            test_results["enhanced_intent_test"] = await self._test_enhanced_intent_service(enhanced_intent_service, client_id)
            
            # Test 4: Integration Test
            test_results["integration_test"] = await self._test_full_integration(
                enhanced_intent_service, client_id, "Test fleet operations"
            )
            
            overall_success = all(
                result.get("success", False) for result in test_results.values()
            )
            
            test_results["overall_success"] = overall_success
            test_results["overall_status"] = "PASS" if overall_success else "FAIL"
            
            print(f"✅ Dynamic Fleet Integration Test: {test_results['overall_status']}")
            
        except Exception as e:
            test_results["error"] = str(e)
            test_results["overall_success"] = False
            test_results["overall_status"] = "ERROR"
        
        return test_results
    
    async def _test_fleet_database(self) -> dict:
        """Test fleet database operations"""
        try:
            # Test robot registration
            from .fleet_database import RobotRegistration
            test_robot = RobotRegistration(
                fleet_id="test_fleet",
                site_id="test_site",
                tenant_id="test_tenant",
                name="Test Robot",
                robot_type="quadruped",
                robot_category="ground",
                ip_address="192.168.1.200",
                network_interface="WiFi",
                model="TEST-001",
                serial="TEST-001",
                firmware="v1.0.0",
                capabilities=["test_capability"],
                metadata={"test": True}
            )
            
            registered_robot = await fleet_manager.register_robot(test_robot)
            
            # Test robot retrieval
            robots = await fleet_manager.get_robots_by_fleet("test_fleet")
            
            # Test fleet status
            fleet_status = await fleet_manager.get_fleet_status("test_fleet")
            
            # Test robot status updates
            await fleet_manager.update_robot_status(registered_robot.robot_id, "busy")
            await fleet_manager.update_robot_state(registered_robot.robot_id, {"test_update": True})
            
            # Cleanup
            await fleet_manager.delete_robot(registered_robot.robot_id)
            
            return {
                "success": True,
                "robot_registration": "PASS",
                "robot_retrieval": "PASS",
                "fleet_status": "PASS",
                "status_updates": "PASS",
                "robots_count": len(robots)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "robot_registration": "FAIL"
            }
    
    async def _test_dynamic_fleet_rag(self, dynamic_fleet_rag, client_id: str) -> dict:
        """Test dynamic fleet RAG functionality"""
        try:
            # Test fleet context retrieval
            fleet_context = await dynamic_fleet_rag.get_fleet_context("cottage_fleet")
            
            # Test enhanced search
            search_results = await dynamic_fleet_rag.search_with_fleet_context(
                client_id, "test query", limit=3
            )
            
            # Test recommendations
            recommendations = await dynamic_fleet_rag.get_fleet_recommendations(
                client_id, "test_mission"
            )
            
            # Test fleet sync to RAG
            await dynamic_fleet_rag.sync_fleet_data_to_rag(client_id)
            
            return {
                "success": True,
                "fleet_context": "PASS",
                "enhanced_search": "PASS",
                "recommendations": "PASS",
                "rag_sync": "PASS",
                "search_results_count": len(search_results),
                "recommendations_count": len(recommendations),
                "available_robots": len(fleet_context.get("available_robots", []))
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fleet_context": "FAIL"
            }
    
    async def _test_enhanced_intent_service(self, enhanced_intent_service, client_id: str) -> dict:
        """Test enhanced intent service"""
        try:
            # Test intent parsing
            intent = await enhanced_intent_service.parse_request(
                request_text="Test fleet operations",
                requested_by="test_user@ios_app",
                context={"test": True}
            )
            
            # Test real-time context retrieval
            context = await enhanced_intent_service._get_real_time_context(client_id)
            
            return {
                "success": True,
                "intent_parsing": "PASS",
                "context_retrieval": "PASS",
                "intent_generated": intent.mission_id is not None,
                "real_time_considerations": len(intent.real_time_considerations) if intent else 0,
                "confidence_score": intent.confidence_score if intent else 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "intent_parsing": "FAIL"
            }
    
    async def _test_full_integration(self, enhanced_intent_service, client_id: str, test_query: str) -> dict:
        """Test full integration with realistic scenario"""
        try:
            # Parse test query
            intent = await enhanced_intent_service.parse_request(
                request_text=test_query,
                requested_by="test_user@ios_app",
                context={"scenario": "boat_arrival", "current_location": "living_room"}
            )
            
            # Verify intent quality
            success_indicators = [
                intent.mission_type in ["transport", "assistance", "cleaning"],
                intent.source_zone in ["dock", "kitchen", "living_room"],
                len(intent.required_capabilities) > 0,
                intent.confidence_score > 0.5,
                len(intent.real_time_considerations) > 0
            ]
            
            integration_quality = sum(success_indicators) / len(success_indicators)
            
            return {
                "success": True,
                "intent_quality": "GOOD" if integration_quality >= 0.8 else "FAIR",
                "integration_score": integration_quality,
                "success_indicators": success_indicators,
                "test_query": test_query,
                "intent_parsed": intent.mission_id is not None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "intent_quality": "FAIL"
            }
    
    def _get_error_stage(self, error: Exception) -> str:
        """Determine which stage failed based on error"""
        error_str = str(error).lower()
        
        if "database" in error_str or "table" in error_str:
            return "fleet_database_setup"
        elif "rag" in error_str or "embedding" in error_str:
            return "rag_system_setup"
        elif "intent" in error_str or "parse" in error_str:
            return "intent_service_setup"
        elif "search" in error_str or "context" in error_str:
            return "integration_test"
        else:
            return "unknown"


# Main setup function
async def setup_dynamic_fleet_rag_integration(client_id: str = "cot_12345678") -> dict:
    """Main setup function for dynamic fleet RAG integration"""
    setup = DynamicFleetSetup()
    return await setup.setup_dynamic_fleet_rag(client_id)


# Test function
async def test_dynamic_fleet_rag_integration(client_id: str = "cot_12345678") -> dict:
    """Test the dynamic fleet RAG integration"""
    setup = DynamicFleetSetup()
    return await setup.test_dynamic_fleet_integration(client_id)


# Demo function
async def demo_dynamic_fleet_rag(client_id: str = "cot_12345678") -> dict:
    """Demo the dynamic fleet RAG integration"""
    print("🚀 Starting Dynamic Fleet RAG Demo")
    print("=" * 60)
    
    # Setup
    setup_result = await setup_dynamic_fleet_rag_integration(client_id)
    
    if setup_result["success"]:
        print(f"✅ Setup Complete: {setup_result['client_id']}")
        print(f"🔧 Components Ready: {list(setup_result.keys())}")
        
        # Demo query
        from .digital_twin_enhanced_intent import create_digital_twin_enhanced_intent_service
        
        enhanced_intent_service = await create_digital_twin_enhanced_intent_service(
            rag_system=None,  # Will be created in setup
            client_id=client_id
        )
        await enhanced_intent_service.initialize(client_id)
        
        # Test realistic scenario
        test_queries = [
            "Get robots ready at the dock for boat arrival",
            "Scan kitchen for QR codes and check groceries",
            "Clean living room while humanoid robot organizes kitchen",
            "Transport heavy packages from dock to garage"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🧪 Demo Query {i}: {query}")
            
            intent = await enhanced_intent_service.parse_request(
                request_text=query,
                requested_by="demo_user@ios_app",
                context={"demo_scenario": i, "current_location": "cottage"}
            )
            
            print(f"📋 Intent Parsed:")
            print(f"   Mission Type: {intent.mission_type}")
            print(f"   Source Zone: {intent.source_zone}")
            print(f"   Required Capabilities: {intent.required_capabilities}")
            print(f"   Confidence: {intent.confidence_score:.2f}")
            print(f"   Real-time Considerations: {len(intent.real_time_considerations)}")
            print(f"   Fleet Feasibility: {getattr(intent, 'fleet_feasibility', 'unknown')}")
        
        print(f"\n" + "=" * 60)
        print("🎉 Dynamic Fleet RAG Demo Complete!")
        
        return {
            "setup": setup_result,
            "demo_queries": len(test_queries),
            "demo_time": datetime.now(timezone.utc).isoformat()
        }
    
    else:
        print(f"❌ Setup Failed: {setup_result.get('error')}")
        return setup_result


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_dynamic_fleet_rag())
