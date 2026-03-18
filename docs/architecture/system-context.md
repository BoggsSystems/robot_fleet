# System Context

## Goal

Build a cloud-backed orchestration layer for Unitree humanoid robot fleets that
supports local-first development now and Azure-backed operational state later.

## Primary Architecture Principle

Separate the platform into five planes:

1. Edge plane
   - Collects telemetry from Unitree DDS
   - Converts robot-native data into canonical fleet events
   - Maintains local resilience during cloud loss
2. Messaging plane
   - Carries canonical events between edge and cloud
   - Uses Mosquitto/EMQX locally and Azure IoT Operations later
3. State plane
   - Projects meaningful state into Azure Digital Twins
   - Does not store raw telemetry as the twin graph
4. History plane
   - Stores telemetry, events, alerts, and replay data
   - Feeds analytics, reporting, and simulation datasets
5. Intelligence plane
   - Consumes snapshots and history for simulation, training, and policy evaluation

## Current Local-First Runtime

- Robot SDK: Unitree SDK2 / DDS
- Edge runtime: containerized services on local K3s
- Broker: Mosquitto or EMQX
- Twin projection: mock twin store with Azure-compatible interfaces
- Simulation: local Isaac Sim or MuJoCo-backed scenarios

## Target Azure Runtime

- Edge management: Azure Arc-enabled Kubernetes
- Edge/cloud data plane: Azure IoT Operations
- Operational state graph: Azure Digital Twins
- Workflow/orchestration logic: Azure Functions and/or containerized services
- Analytics: Fabric and related historical storage

## Core Interfaces

These contracts must remain stable across local and cloud environments.

1. `robot.telemetry`
   - High-rate sensor, pose, battery, actuator, and environment data
2. `robot.health`
   - Faults, warnings, thermal state, comms health, and subsystem readiness
3. `robot.task_status`
   - Task assignment, progress, completion, failure, cancellation
4. `robot.intent`
   - Edge-computed intent or autonomy state changes that matter operationally
5. `fleet.command`
   - Commands issued by operators or workflows toward robots and fleets
6. `twin.projection`
   - Internal projection output from canonical events to Digital Twin updates

## Canonical Flow

1. Unitree robot publishes DDS messages
2. Edge bridge converts DDS to canonical events
3. Canonical events publish to MQTT
4. Projection service updates operational state
5. History service stores raw events for replay and analytics
6. Control plane consumes state and issues commands
7. Simulation consumes historical snapshots, not live control topics

## Architectural Constraints

- The edge bridge must not depend directly on Azure-specific SDKs
- Business logic must not be embedded in transport adapters
- Azure Digital Twins is the operational graph, not the event log
- Event schemas must be versioned
- All robot identities must be X.509-ready even in local mode
- A single site must continue degraded operation during cloud outage
