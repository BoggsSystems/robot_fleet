# ADR-001: Edge / Cloud Boundary

## Status

Accepted

## Context

The platform must support robot operation during cloud unavailability, while
still projecting fleet state into a cloud-managed operational model.

## Decision

Edge responsibilities:

- DDS ingestion from Unitree SDK
- Canonical event creation
- Local buffering and replay
- Safety-critical degraded behavior
- Local command execution

Cloud responsibilities:

- Operational twin graph
- Historical analytics
- Cross-site fleet management
- Alerting, reporting, and orchestration workflows
- Simulation and training feedback loops

## Consequences

- Edge services must be cloud-neutral
- Cloud projections must consume canonical events, not DDS messages directly
- Outage handling and replay become first-class edge requirements
