# ADR-002: Twin Projection Strategy

## Status

Accepted

## Context

Azure Digital Twins should represent the current operational state of the
system, but not absorb high-rate telemetry as the system of record.

## Decision

Use a projection service that consumes canonical fleet events and writes
meaningful state transitions into the Digital Twin graph.

Projection examples:

- robot battery thresholds -> twin property updates
- robot fault events -> health state property updates
- robot zone movement -> relationship or location property changes
- task status transitions -> assignment/completion relationships

## Non-Goals

- Raw telemetry storage inside Digital Twins
- Replay and analytics directly from the twin graph
- Direct DDS -> Digital Twins coupling

## Consequences

- Historical storage is separate from twin storage
- Projection logic must be deterministic and testable
- Local mock twin stores can be used before Azure access exists
