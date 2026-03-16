import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory reference to the running FleetController
_fleet_controller = None

def set_fleet_controller(controller):
    global _fleet_controller
    _fleet_controller = controller

@app.get("/api/fleet/status")
async def get_fleet_status():
    if _fleet_controller is None:
        return {"error": "Fleet controller not running"}
    return _fleet_controller.get_fleet_status()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            if _fleet_controller is not None:
                status = _fleet_controller.get_fleet_status()
                # Broadcast the live position and task metrics
                await websocket.send_text(json.dumps(status))
            # Stream at 20Hz (every 50ms)
            await asyncio.sleep(0.05)
    except WebSocketDisconnect:
        print("Dashboard client disconnected from WebSocket")
    except Exception as e:
        print(f"WebSocket error: {e}")

def run_server(controller, port=8000):
    global _fleet_controller
    _fleet_controller = controller
    import uvicorn
    # Important: Run programmatically since we share the controller memory
    print(f"Starting dashboard telemetry server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
