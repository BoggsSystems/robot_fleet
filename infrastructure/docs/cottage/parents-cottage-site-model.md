# Parents Cottage Site Model

This is the first manually authored operational graph for the cottage workflow,
based directly on the verbal description of the trip, landing, dock, boardwalk,
path, deck, and interior rooms.

Primary model file:

- [parents-cottage-site-model.json](/Users/jeffboggs/robot_fleet/docs/cottage/parents-cottage-site-model.json)

## Modeling Approach

This graph is operational rather than architectural. It focuses on:

- where cargo changes transport mode
- where handoffs happen
- where terrain or route risk matters
- where robots would stage, deliver, or inspect

It intentionally includes upstream logistics before the island:

- Whitby house interior staging
- Whitby driveway truck bay
- regional road waypoint near Woods Road
- landing truck bay
- landing boat ramp

That means the model supports end-to-end missions, not only on-island missions.

## Key Workflow Spine

The initial grocery workflow is:

1. Whitby interior staging
2. Whitby driveway truck bay
3. Woods Road turnoff waypoint
4. landing truck bay
5. landing boat ramp
6. water route
7. main dock
8. dock walkway
9. square dock area
10. narrow walkway
11. island path entry
12. natural cottage path
13. deck stairs
14. deck
15. screened dining area
16. entry foyer
17. dining room
18. kitchen
19. fridge

## Interior Nodes Included

The authored interior graph currently includes:

- entry foyer
- dining room
- kitchen
- fridge
- living room
- hallway
- laundry/storage room
- front left bedroom
- main bedroom
- rear right bedroom
- hall cabinet

## Explicit Assumptions Frozen In This Version

- The final drive from the Woods Road turnoff to the landing is modeled as about 15 minutes.
- The boat route from landing to dock is modeled as about 10 minutes.
- The narrow dock-to-shore walkway is modeled as about 60 feet.
- The uphill natural path is modeled as mild-to-medium grade.
- The deck stairs are modeled as 3 steps.
- The screened dining area is modeled as a semi-outdoor transition space.
- The foyer and dining room are modeled as separate nodes.
- The fridge is modeled as a separate destination fixture inside the kitchen.
- The hallway connects both the living room and kitchen to the bedroom/utility corridor.

## Known Gaps To Refine Later

- exact distances between interior nodes
- exact widths and turning constraints for doorways
- whether alternate dock/path routes exist
- charging/staging locations for robots at the property
- exact placement surfaces for groceries in kitchen and dining room
- whether the hall cabinet should remain a distinct fixture node
- any additional sheds, exterior storage, or service structures

## Why This Phase Matters

This file is enough to replace the idea of a generic cottage with a real first
site graph. The next backend phase can now load this graph and use it for:

- route lookup
- handoff-aware planning
- blocked-zone avoidance
- site-specific approval UX
- more realistic replanning
