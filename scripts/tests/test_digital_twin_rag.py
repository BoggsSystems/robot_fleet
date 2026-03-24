#!/usr/bin/env python3
"""
Quick test script for Azure Digital Twin RAG integration.
"""

import asyncio
import json
from datetime import datetime, timezone

# Import our modules
from fleet_control.brain.multi_tenant_rag import MultiTenantRAG
from fleet_control.brain.digital_twin_rag_setup import DigitalTwinRAGSetup


async def quick_test():
    """Quick test of the Digital Twin RAG integration"""
    print("🚀 Quick Test: Azure Digital Twin RAG Integration")
    print("=" * 50)
    
    # Initialize setup (without Azure endpoint for demo)
    setup = DigitalTwinRAGSetup(adt_endpoint=None)  # Mock mode
    
    try:
        # Setup the integration
        print("📋 Setting up integration...")
        result = await setup.setup_digital_twin_rag(client_id="cot_12345678")
        
        if result["success"]:
            print("✅ Setup successful!")
            print(f"🔧 Features: {json.dumps(result['features'], indent=2)}")
        else:
            print(f"❌ Setup failed: {result['error']}")
            return
        
        # Test RAG search
        print("\n🔍 Testing RAG search...")
        search_result = await setup._test_rag_search("cot_12345678")
        
        if search_result["success"]:
            print(f"✅ Search successful: {search_result['results_count']} results")
            if search_result.get("top_result"):
                print(f"📄 Top result: {search_result['top_result']['id']}")
        else:
            print(f"❌ Search failed: {search_result['error']}")
        
        # Test enhanced intent parsing
        print("\n🧠 Testing enhanced intent parsing...")
        intent_result = await setup._test_enhanced_intent_parsing("cot_12345678")
        
        if intent_result["success"]:
            intent = intent_result["parsed_intent"]
            print(f"✅ Intent parsed: {intent['mission_type']}")
            print(f"📍 Zone: {intent['source_zone']}")
            print(f"💡 Confidence: {intent['confidence_score']}")
            print(f"⚡ Real-time considerations: {len(intent.get('real_time_considerations', []))}")
        else:
            print(f"❌ Intent parsing failed: {intent_result['error']}")
        
        # Test real-time updates
        print("\n📡 Testing real-time updates...")
        update_result = await setup.simulate_real_time_updates("cot_12345678")
        
        if update_result["success"]:
            print(f"✅ Updates successful: {update_result['successful_updates']}/{update_result['updates_sent']}")
        else:
            print(f"❌ Updates failed: {update_result.get('error', 'Unknown error')}")
        
        # Get recommendations
        print("\n💡 Getting real-time recommendations...")
        try:
            recommendations = await setup.enhanced_intent_service.get_real_time_mission_recommendations("cot_12345678")
            
            if recommendations:
                print(f"✅ Found {len(recommendations)} recommendations")
                for i, rec in enumerate(recommendations[:2], 1):
                    print(f"🏆 {i}. {rec['zone_name']}")
                    for mission in rec.get("recommended_missions", [])[:2]:
                        print(f"   • {mission['mission_type']}")
                    if rec.get("best_robot"):
                        print(f"   🤖 Robot: {rec['best_robot']['name']}")
            else:
                print("ℹ️  No recommendations available")
        except Exception as e:
            print(f"⚠️  Recommendations failed: {e}")
        
        # Final status
        print("\n📊 Final Status:")
        status = await setup.get_integration_status()
        print(json.dumps(status, indent=2))
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🎉 Quick Test Complete!")


if __name__ == "__main__":
    asyncio.run(quick_test())
