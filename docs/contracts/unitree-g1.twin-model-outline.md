# Unitree G1 Twin Model Outline

This is the Phase 0 outline for the Unitree G1 Digital Twin model. The actual
DTDL JSON-LD can be generated after the domain review is approved.

## Root Model

- Interface ID: `dtmi:boggssystems:robotics:unitree:g1;1`
- Display name: `Unitree G1 Robot`

## Core Properties

- `robotId` (string)
- `fleetId` (string)
- `siteId` (string)
- `model` (string)
- `firmwareVersion` (string)
- `healthStatus` (string)
- `batteryPct` (double)
- `networkStatus` (string)
- `currentTaskId` (string)
- `currentZoneId` (string)

## Components

### Mobility

- gait mode
- pose
- velocity
- balance state

### Power

- battery percentage
- charging state
- estimated runtime

### Health

- system status
- fault summary
- subsystem health

### Joints

Represent the 43 degrees of freedom as grouped telemetry components rather than
one flat property bag where possible.

Suggested grouping:

- torso and head
- left arm
- right arm
- left hand
- right hand
- left leg
- right leg

Each grouped component should expose:

- `position`
- `velocity`
- `temperature`
- `torque_estimate`

## Relationships

- `belongsToFleet`
- `locatedInZone`
- `assignedToTask`
- `connectedToEdgeNode`

## Notes

- The twin graph stores current operational state
- High-rate joint telemetry should be summarized/projected, not fully persisted
  in the twin graph
- Full raw telemetry belongs in the history layer
