# MuJoCo Robot Training Container
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV MUJOCO_GL=egl

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    unzip \
    libgl1-mesa-dev \
    libegl1-mesa-dev \
    libglu1-mesa-dev \
    libglew-dev \
    libosmesa6-dev \
    libxinerama1 \
    libxcursor1 \
    libxrandr2 \
    libxi6 \
    libxext6 \
    libx11-dev \
    libxrandr-dev \
    libxinerama-dev \
    libxcursor-dev \
    libxfixes-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the robot fleet codebase
COPY . .

# Install Unitree SDK
RUN pip install -e SDK/unitree_sdk2_python

# Create directories for data and logs
RUN mkdir -p data/logs simulation/output

# Expose port for potential dashboard/API
EXPOSE 5000

# Default command - run bathroom sanitation simulation
CMD ["python3", "simulation/run_robot_bridge.py", "--scene", "simulation/bathroom_scene.xml", "--domain", "100", "--interface", "lo0", "--sanitation"]
