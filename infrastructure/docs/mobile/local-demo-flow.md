# Local Demo Flow

This is the current canonical local demo path for the backend and iPhone app
scaffold.

## Backend

1. Start the dashboard server.
2. Use the mobile mission endpoints:
   - preview
   - clarify if needed
   - confirm
   - list/detail for tracking
3. Mission sessions and generated tasks are stored in the local SQLite store.

## Frontend Surfaces

- React operations terminal:
  - reads `/api/fleet/status`
  - can trigger the grocery scenario
  - reflects backend-created tasks
- iPhone scaffold:
  - targets `/api/mobile/missions/*`
  - uses MVVM service contracts in [ios/Cottage/Services](/Users/jeffboggs/robot_fleet/ios/Cottage/Services)

## Demo Credentials

- Web terminal: `admin / demo123`
- iPhone scaffold auth layer: `admin / demo123`

## Example Mission Sequence

1. Preview: `Bring groceries from dock to kitchen`
2. Backend returns:
   - structured mission
   - candidate robot assignment
   - stable `missionId`
3. Confirm the mission.
4. Backend creates real task records.
5. Mission status becomes `in_progress`.
6. Poll mission detail or list to track status.
