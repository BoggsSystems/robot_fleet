# Identity Strategy

## Goals

- Support local-first development without breaking future Azure identity design
- Keep naming deterministic across edge, control plane, Digital Twins, and analytics
- Prepare for X.509 onboarding for fleets of 100+ units

## Identity Domains

### Tenant

- Format: `tenant:<slug>`
- Example: `tenant:boggs-demo`

### Site

- Format: `site:<tenant_slug>:<site_slug>`
- Example: `site:boggs-demo:london-costco`

### Fleet

- Format: `fleet:<tenant_slug>:<site_slug>:<fleet_slug>`
- Example: `fleet:boggs-demo:london-costco:g1-retail`

### Robot

- Format: `robot:<vendor>:<model>:<serial>`
- Example: `robot:unitree:g1:G1-000042`

### Edge Node

- Format: `edge:<site_slug>:<node_slug>`
- Example: `edge:london-costco:orin-a`

## MQTT Topic Conventions

- `fleet/<fleet_id>/robot/<robot_id>/telemetry`
- `fleet/<fleet_id>/robot/<robot_id>/health`
- `fleet/<fleet_id>/robot/<robot_id>/task-status`
- `fleet/<fleet_id>/robot/<robot_id>/intent`
- `fleet/<fleet_id>/robot/<robot_id>/command`

Replace `:` with `_` or URL-safe escaping when a topic transport requires it.

## Twin Identity Conventions

Twin IDs:

- `robot--unitree--g1--G1-000042`
- `fleet--boggs-demo--london-costco--g1-retail`
- `site--boggs-demo--london-costco`
- `zone--boggs-demo--london-costco--bathroom-east`

Relationships:

- robot -> belongsTo -> fleet
- robot -> locatedIn -> zone
- fleet -> operatesAt -> site
- robot -> assignedTo -> task

## Certificate Strategy

Robot device subject:

- `CN=<robot_id>, O=Boggs Systems, OU=Robotics`

Example:

- `CN=robot:unitree:g1:G1-000042, O=Boggs Systems, OU=Robotics`

Requirements:

- Device certs must be replaceable without changing the logical robot ID
- Certificates authenticate transport identity
- Logical robot ID remains the primary application identity

## Implementation Notes

- Store logical IDs in every canonical event envelope
- Do not infer fleet or site solely from certificate subject
- All adapters must accept local mock certs and local mock identities
