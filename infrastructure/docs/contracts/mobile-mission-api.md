# Mobile Mission API

This document defines the current local-first contract used by the iPhone app
scaffold under [ios/Cottage](/Users/jeffboggs/robot_fleet/ios/Cottage).

## Canonical Flow

1. `POST /api/mobile/missions/preview`
2. If needed: `POST /api/mobile/missions/{mission_id}/clarify`
3. `POST /api/mobile/missions/{mission_id}/confirm`
4. Poll with:
   - `GET /api/mobile/missions`
   - `GET /api/mobile/missions/{mission_id}`
5. Optional: `POST /api/mobile/missions/{mission_id}/cancel`

## Mission Status Values

- `clarification_required`
- `ok` in preview payloads
- `planned`
- `dispatched`
- `in_progress`
- `completed`
- `blocked`
- `cancelled`

The mobile-facing `mission.status` field is the user-oriented lifecycle value.
The `preview.status` field reflects the preview/plan result.

## Preview Request

```json
{
  "requestText": "Bring groceries from dock to kitchen",
  "requestedBy": "operator@local",
  "context": {}
}
```

## Preview Response

```json
{
  "mission": {
    "missionId": "msn-1234abcd",
    "title": "Bring groceries from dock to kitchen",
    "requestText": "Bring groceries from dock to kitchen",
    "status": "planned",
    "missionType": "cargo_transfer",
    "from": "dock",
    "to": "kitchen",
    "assignedRobotId": "carrier-01",
    "taskCount": 1,
    "taskIds": [],
    "clarificationRequired": false,
    "clarificationQuestion": null,
    "summary": "All 1 planned tasks have candidate robot assignments.",
    "createdAt": "2026-03-19T00:00:00Z",
    "updatedAt": "2026-03-19T00:00:00Z"
  },
  "preview": {
    "status": "ok",
    "intent_provider": "local-rule-parser",
    "intent": {},
    "resources": {},
    "plan": {},
    "explanation": {}
  }
}
```

## Clarification Response Shape

When the backend needs more information, `mission.clarificationRequired` is
`true` and `mission.clarificationQuestion` contains:

```json
{
  "mission_id": "msn-1234abcd",
  "prompt": "Which area should the mission start from?",
  "field_name": "source_zone",
  "reason": "Could not infer source_zone from the request."
}
```

The app should present that prompt conversationally, collect one answer, and
send it to the `clarify` endpoint.

## Confirm Response

`confirm` returns the updated `mission` plus a `dispatch` payload when tasks were
created in the backend. The app should treat a successful confirm as the start
of mission tracking and then poll `GET /api/mobile/missions/{mission_id}`.

## Notes

- The current local implementation stores mission sessions in SQLite.
- The mobile `missionId` is stable across preview, clarification, and confirm.
- Intent parsing may come from `local-rule-parser`, `local-fallback`,
  `openai`, or `azure-openai`.
