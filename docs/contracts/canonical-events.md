# Canonical Events

All events share a common envelope.

## Shared Envelope

```json
{
  "schema_version": "1.0.0",
  "event_type": "robot.telemetry",
  "event_id": "evt_01JABC...",
  "occurred_at": "2026-03-18T12:00:00Z",
  "tenant_id": "tenant:boggs-demo",
  "site_id": "site:boggs-demo:london-costco",
  "fleet_id": "fleet:boggs-demo:london-costco:g1-retail",
  "robot_id": "robot:unitree:g1:G1-000042",
  "source": {
    "adapter": "unitree-dds-bridge",
    "edge_node_id": "edge:london-costco:orin-a"
  },
  "payload": {}
}
```

## `robot.telemetry`

Purpose:

- high-rate operational measurements for robot state and analytics

Payload fields:

- `pose`
- `velocity`
- `battery`
- `joint_states`
- `motor_temps`
- `network_rtt_ms`
- `task_context`

## `robot.health`

Purpose:

- health snapshots and fault transitions

Payload fields:

- `status`: `ok | warning | fault | offline | maintenance`
- `fault_codes`
- `subsystems`
- `battery_health`
- `comms_health`
- `safety_state`

## `robot.task_status`

Purpose:

- operational task lifecycle

Payload fields:

- `task_id`
- `task_type`
- `state`: `queued | assigned | active | blocked | completed | failed | canceled`
- `progress_pct`
- `reason`

## `robot.intent`

Purpose:

- edge-computed autonomy state that matters to orchestration

Payload fields:

- `mode`
- `target_zone`
- `confidence`
- `requires_operator_attention`

## `fleet.command`

Purpose:

- control-plane commands directed at a robot or fleet

Payload fields:

- `command_id`
- `target_type`
- `target_id`
- `command_type`
- `params`
- `issued_by`

## Rules

- Event producers own transport translation, not business logic
- Consumers must tolerate additive fields
- `schema_version` increments on breaking changes
- Every event must be replay-safe and idempotent where possible
