# Placeholder Cottage Graph

This graph is the default stand-in before the real site structure is known. It
is intentionally generic so orchestration, projection, and simulation can be
built now.

## Default Twin IDs

- `site--parents-cottage`
- `zone--parents-cottage--landing`
- `path--parents-cottage--landing-to-dock`
- `dock--parents-cottage--main-dock`
- `building--parents-cottage--main-cottage`
- `room--parents-cottage--entry`
- `room--parents-cottage--main-floor`
- `room--parents-cottage--kitchen`
- `room--parents-cottage--bedroom`
- `path--parents-cottage--entry-to-main-floor`
- `robot--placeholder--carrier-01`
- `boat--placeholder--service-01`

## Default Relationships

- `site -> containsLocation -> landing`
- `site -> containsLocation -> landing-to-dock`
- `site -> containsLocation -> main-dock`
- `site -> containsLocation -> main-cottage`
- `main-cottage -> containsRoom -> entry`
- `main-cottage -> containsRoom -> main-floor`
- `main-cottage -> containsRoom -> kitchen`
- `main-cottage -> containsRoom -> bedroom`
- `landing -> connectedTo -> landing-to-dock`
- `landing-to-dock -> connectedTo -> main-dock`
- `landing -> connectedTo -> entry`
- `entry -> connectedTo -> main-floor`
- `main-floor -> connectedTo -> kitchen`
- `main-floor -> connectedTo -> bedroom`
- `robot--placeholder--carrier-01 -> locatedAt -> landing`
- `boat--placeholder--service-01 -> locatedAt -> main-dock`

## Suggested Default Properties

### Landing

- `locationType = "zone"`
- `status = "available"`

### Landing To Dock

- `locationType = "path_segment"`
- `distanceMeters = 30`
- `gradePct = 4`
- `isStairAccess = false`

### Main Dock

- `locationType = "dock"`
- `dockStatus = "available"`

### Main Cottage

- `locationType = "building"`
- `buildingType = "residential"`

## First Simulation Workflows

- delivery handoff from landing to dock
- dock to entry cargo transfer
- entry to kitchen delivery
- inspection route from entry to bedroom
- hazard alert on path segment
