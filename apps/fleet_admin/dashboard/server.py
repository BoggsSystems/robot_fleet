#!/usr/bin/env python3
"""
Fleet Admin Dashboard Server
Dedicated server for fleet management and customer administration
"""

import os
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI(title="Fleet Admin Dashboard", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="web/dist"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("web/index.html")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "fleet-admin"}

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=5174,
        reload=True,
        log_level="info"
    )
