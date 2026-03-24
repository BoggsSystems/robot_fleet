#!/usr/bin/env python3
"""
Send test robot telemetry to Azure IoT Hub
"""
import os
import json
import time
import random
from datetime import datetime
from dotenv import load_dotenv
from azure.iot.device import IoTHubDeviceClient, Message

# Load environment variables
load_dotenv()

def create_robot_telemetry(robot_id):
    """Create sample robot telemetry data"""
    return {
        "robotId": robot_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "position": {
            "x": round(random.uniform(-10, 10), 2),
            "y": round(random.uniform(-10, 10), 2),
            "z": 0
        },
        "battery": round(random.uniform(20, 100), 1),
        "status": random.choice(["idle", "moving", "working", "charging"]),
        "temperature": round(random.uniform(18, 35), 1),
        "cpu_usage": round(random.uniform(10, 80), 1),
        "memory_usage": round(random.uniform(30, 90), 1)
    }

def send_telemetry_to_iot_hub(robot_id, connection_string):
    """Send telemetry data to IoT Hub"""
    try:
        # Create device client
        device_client = IoTHubDeviceClient.create_from_connection_string(connection_string)
        
        # Connect to IoT Hub
        device_client.connect()
        print(f"✅ {robot_id} connected to IoT Hub")
        
        # Send telemetry
        telemetry = create_robot_telemetry(robot_id)
        message = Message(json.dumps(telemetry))
        device_client.send_message(message)
        print(f"📤 {robot_id} sent telemetry: {telemetry['status']} at {telemetry['position']['x']},{telemetry['position']['y']}")
        
        # Disconnect
        device_client.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ {robot_id} failed to send telemetry: {str(e)}")
        return False

def main():
    print("🤖 Robot Fleet Telemetry Test")
    print("=" * 50)
    
    # Get IoT Hub connection string
    iot_hub_conn_str = os.getenv('IOT_HUB_CONNECTION_STRING')
    if not iot_hub_conn_str:
        print("❌ IoT Hub connection string not found in .env")
        return
    
    # Test with 3 robots
    robots = ["robot-001", "robot-002", "robot-003"]
    
    for robot in robots:
        # Create device-specific connection string
        device_conn_str = iot_hub_conn_str.replace("DeviceId=;", f"DeviceId={robot};")
        if "DeviceId=" not in device_conn_str:
            device_conn_str = iot_hub_conn_str + f";DeviceId={robot}"
        
        print(f"\n🔗 Testing {robot}...")
        success = send_telemetry_to_iot_hub(robot, device_conn_str)
        
        if success:
            print(f"✅ {robot} telemetry sent successfully")
        else:
            print(f"❌ {robot} telemetry failed")
        
        time.sleep(1)
    
    print("\n🎉 Telemetry test completed!")
    print("📊 Check your Event Processor logs to see data being processed")

if __name__ == "__main__":
    main()
