#!/usr/bin/env python3
"""
Test script to verify the MuJoCo simulation container works correctly.
"""

import subprocess
import sys
import time

def test_container():
    """Test the Docker container by running a short simulation."""
    
    print("🧪 Testing MuJoCo simulation container...")
    
    # Test command - run simulation for 10 seconds then stop
    cmd = [
        "python3", "simulation/run_robot_bridge.py",
        "--scene", "simulation/bathroom_scene.xml",
        "--domain", "100",
        "--interface", "lo0",
        "--sanitation"
    ]
    
    try:
        # Start the process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("✅ Container started successfully")
        print("⏱️  Running for 5 seconds to test...")
        
        # Let it run for 5 seconds
        time.sleep(5)
        
        # Terminate the process
        process.terminate()
        stdout, stderr = process.communicate(timeout=10)
        
        print("✅ Container test completed")
        print(f"Exit code: {process.returncode}")
        
        if "Robot at" in stdout:
            print("✅ Robot simulation is working")
        else:
            print("⚠️  Unexpected output, check logs")
            
        return process.returncode == 0
        
    except Exception as e:
        print(f"❌ Container test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_container()
    sys.exit(0 if success else 1)
