"""
Minimal CLI for Phase 3 backend registry and task services.
"""

from __future__ import annotations

import argparse
import json

from .brain import LocalMissionBrain, make_sample_phase1_contracts
from .config import LocalRuntimeConfig
from .persistence import ShadowWorldStore
from .services import FleetBackendServices


def build_services() -> FleetBackendServices:
    services = FleetBackendServices(store=ShadowWorldStore(), config=LocalRuntimeConfig())
    services.ensure_defaults()
    return services


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage the local fleet backend")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("overview", help="Show persistent backend overview")
    subparsers.add_parser("brain-contracts", help="Show the Phase 1 brain contract shapes")

    mission_parser = subparsers.add_parser("plan-mission", help="Preview a local mission plan from natural language")
    mission_parser.add_argument("request_text")
    mission_parser.add_argument("--requested-by", default="operator@local")

    subparsers.add_parser("assess-resources", help="Show allocatable robots and resource reasoning")

    robot_status_parser = subparsers.add_parser("robot-status", help="Update a robot resource profile/status")
    robot_status_parser.add_argument("robot_id")
    robot_status_parser.add_argument("--status", default=None)
    robot_status_parser.add_argument("--zone-id", default=None)
    robot_status_parser.add_argument("--battery-level", type=float, default=None)
    robot_status_parser.add_argument("--payload-capacity-kg", type=float, default=None)
    robot_status_parser.add_argument("--range-minutes", type=int, default=None)
    robot_status_parser.add_argument("--capabilities", default=None, help="Comma-separated capabilities")

    subparsers.add_parser("reassign-tasks", help="Assign queued tasks to currently allocatable robots")

    zone_parser = subparsers.add_parser("create-zone", help="Create a zone")
    zone_parser.add_argument("zone_id")
    zone_parser.add_argument("name")
    zone_parser.add_argument("--site-id", default=LocalRuntimeConfig().site_id)
    zone_parser.add_argument("--zone-type", default="operational")

    task_parser = subparsers.add_parser("create-task", help="Create a queued task")
    task_parser.add_argument("task_type")
    task_parser.add_argument("--robot-id", default=None)
    task_parser.add_argument("--zone-id", default=None)
    task_parser.add_argument("--spec", default="{}", help="JSON task spec")

    args = parser.parse_args()
    services = build_services()
    brain = LocalMissionBrain(services)

    if args.command == "overview":
        print(json.dumps(services.fleet_overview(), indent=2))
        return 0
    if args.command == "brain-contracts":
        print(json.dumps(make_sample_phase1_contracts(), indent=2))
        return 0
    if args.command == "plan-mission":
        result = brain.preview_mission(args.request_text, requested_by=args.requested_by)
        print(json.dumps(result, indent=2))
        return 0
    if args.command == "assess-resources":
        print(json.dumps(brain.assess_resources(), indent=2))
        return 0
    if args.command == "robot-status":
        metadata_updates = {}
        if args.battery_level is not None:
            metadata_updates["battery_level"] = args.battery_level
        if args.payload_capacity_kg is not None:
            metadata_updates["payload_capacity_kg"] = args.payload_capacity_kg
        if args.range_minutes is not None:
            metadata_updates["range_minutes"] = args.range_minutes
        capabilities = None
        if args.capabilities is not None:
            capabilities = [item.strip() for item in args.capabilities.split(",") if item.strip()]
        robot = services.update_robot_profile(
            args.robot_id,
            status=args.status,
            zone_id=args.zone_id,
            capabilities=capabilities,
            metadata_updates=metadata_updates or None,
        )
        print(json.dumps(robot, indent=2))
        return 0
    if args.command == "reassign-tasks":
        print(json.dumps(brain.reassign_queued_tasks(), indent=2))
        return 0
    if args.command == "create-zone":
        zone = services.create_zone(args.zone_id, args.site_id, args.name, args.zone_type)
        print(json.dumps(zone, indent=2))
        return 0
    if args.command == "create-task":
        task = services.create_task(
            task_type=args.task_type,
            spec=json.loads(args.spec),
            robot_id=args.robot_id,
            zone_id=args.zone_id,
        )
        print(json.dumps(task, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
