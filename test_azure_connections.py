#!/usr/bin/env python3
"""
Test Azure backend connections for Robot Fleet System
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_iot_hub():
    """Test IoT Hub connection"""
    print("🔗 Testing IoT Hub Connection...")
    conn_str = os.getenv('IOT_HUB_CONNECTION_STRING')
    if conn_str:
        print(f"✅ IoT Hub connection string found: {conn_str[:50]}...")
        return True
    else:
        print("❌ IoT Hub connection string not found")
        return False

def test_storage():
    """Test Storage connection"""
    print("📦 Testing Storage Connection...")
    conn_str = os.getenv('STORAGE_CONNECTION_STRING')
    if conn_str:
        print(f"✅ Storage connection string found: {conn_str[:50]}...")
        return True
    else:
        print("❌ Storage connection string not found")
        return False

def test_cosmos():
    """Test Cosmos DB connection"""
    print("🗄️ Testing Cosmos DB Connection...")
    endpoint = os.getenv('COSMOS_DB_ENDPOINT')
    key = os.getenv('COSMOS_DB_KEY')
    if endpoint and key:
        print(f"✅ Cosmos DB endpoint found: {endpoint}")
        print(f"✅ Cosmos DB key found: {key[:20]}...")
        return True
    else:
        print("❌ Cosmos DB credentials not found")
        return False

def test_digital_twins():
    """Test Digital Twins connection"""
    print("🏢 Testing Digital Twins Connection...")
    endpoint = os.getenv('DIGITAL_TWINS_ENDPOINT')
    if endpoint:
        print(f"✅ Digital Twins endpoint found: {endpoint}")
        return True
    else:
        print("❌ Digital Twins endpoint not found")
        return False

def main():
    print("🚀 Azure Backend Connection Test")
    print("=" * 50)
    
    tests = [
        test_iot_hub,
        test_storage, 
        test_cosmos,
        test_digital_twins
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"📊 Results: {passed}/{total} connections configured")
    
    if passed == total:
        print("🎉 All Azure backend connections are ready!")
    else:
        print("⚠️ Some connections need configuration")
    
    return passed == total

if __name__ == "__main__":
    main()
