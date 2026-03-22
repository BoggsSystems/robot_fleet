"""
Simple CLI inspector for local Shadow World persistence.
"""

from __future__ import annotations

import argparse
import json

from .persistence import ShadowWorldStore


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect local Shadow World backend state")
    parser.add_argument("--events", type=int, default=10, help="Number of recent events to show")
    parser.add_argument("--patches", type=int, default=10, help="Number of recent twin patches to show")
    args = parser.parse_args()

    store = ShadowWorldStore()
    report = {
        "robot_states": store.current_robot_states(),
        "recent_events": store.recent_events(args.events),
        "recent_patches": store.recent_patches(args.patches),
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
