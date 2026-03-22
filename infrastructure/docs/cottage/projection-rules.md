# Cottage Projection Rules

These rules define how canonical events should update the cottage Azure Digital
Twin graph. They are intended to be implemented by a projection worker that
consumes canonical events and writes deterministic ADT patches.

## General Rules

- The twin graph stores current operational state.
- Raw telemetry goes to history storage, not into ADT unchanged.
- Projections must be replay-safe.
- Relationship changes must be deterministic.

## Event Families

### `robot.telemetry`

Update:

- robot `status`
- robot `batteryPct`
- robot `robotType`
- robot `robotCategory`
- robot `lastUpdatedAt`

Optional derived updates:

- if location inference is available, update `locatedAt`
- if battery is below threshold, emit/update warning state

### `robot.health`

Update:

- robot `connectivity`
- robot `healthStatus`
- robot `batteryPct`
- robot `lastUpdatedAt`

### `robot.task_status`

Update:

- task twin `taskStatus`
- task twin `summary`
- task twin `lastUpdatedAt`
- robot `currentTaskId`

Relationship updates:

- ensure `robot -> assignedToTask -> task`

### `robot.alert`

Create or update:

- alert twin with severity, code, message, status

Relationship updates:

- link the alert to the affected location if the location can be resolved

### Future Cottage-Specific Events

Planned event families:

- `boat.status`
- `cargo.status`
- `cargo.handoff`
- `zone.occupancy`
- `inspection.result`
- `hazard.detected`

## Location Rules

- A movable asset should have exactly one active `locatedAt` relationship.
- The projection worker should replace prior `locatedAt` relationships when a new location is authoritative.
- Static structure relationships such as `containsLocation` and `containsRoom` should be provisioned during site bootstrap, not during live telemetry projection.

## History Split

Store in ADT:

- current robot state
- current task state
- current boat availability
- current cargo location
- active alerts

Store in history layer:

- raw telemetry streams
- image and detection payloads
- task execution traces
- operator interaction logs
- weather time series
