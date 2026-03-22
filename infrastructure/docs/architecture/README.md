# Architecture Baseline

This directory contains the Phase 0 architecture baseline for the robot fleet
platform. The purpose of these artifacts is to lock the core interfaces before
any cloud-specific implementation is allowed to spread through the codebase.

Files:

- `system-context.md`: target architecture, platform boundaries, and service roles
- `identity-strategy.md`: robot, fleet, site, and certificate naming strategy
- `adr-001-edge-cloud-boundary.md`: edge vs cloud responsibility split
- `adr-002-twin-projection.md`: Digital Twins projection strategy

Related contracts live in `/Users/jeffboggs/robot_fleet/docs/contracts`.
