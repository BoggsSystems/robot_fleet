# Cottage Domain Twin Model Outline

This document defines the site-independent Azure Digital Twins model set for a
cottage robotics deployment. It is intended to be loaded alongside the existing
fleet contracts and populated with site-specific twins later.

## Scope

The cottage domain covers:

- property layout
- dock and shoreline access
- exterior traversal paths
- building and room structure
- robots, boats, cargo, and tasks
- alerts and operational site conditions

## Core Interfaces

- `Site`
- `Location`
- `Zone`
- `PathSegment`
- `Building`
- `Room`
- `Dock`
- `Robot`
- `Boat`
- `Cargo`
- `Task`
- `Alert`

## Location Strategy

Use `Location` as the common target for graph traversal and entity placement.
Specific location types extend `Location`.

This keeps the model stable before the real site map is available.

## Relationship Vocabulary

- `containsLocation`
- `containsRobot`
- `containsBoat`
- `containsRoom`
- `connectedTo`
- `locatedAt`
- `assignedToTask`
- `servesBoat`
- `affectsLocation`

## Property Guidelines

The twin graph should store operational state, not raw telemetry.

Recommended operational properties:

- identity
- status
- battery percentage
- health/connectivity summary
- current task identifier
- weather or hazard summary
- last update timestamps

Keep high-rate telemetry in the history layer.

## What Is Deferred Until Site Intake

- real zone names
- actual path distances and slope
- room inventory
- charging and network coverage
- exact boat/dock operating rules
- no-go zones and seasonal hazards
