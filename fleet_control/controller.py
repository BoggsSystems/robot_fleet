"""
Central AI orchestration module for the robot fleet.

Responsibilities:
- Multi-robot task assignment and scheduling
- Conflict avoidance and coordination
- High-level decision points for task routing

Pilot module uses: register_robot(), assign_task(), get_fleet_status(),
report_task_done() to coordinate 1–2 robots and track idle/busy/completed.
"""

from .robot_manager import RobotManager, STATUS_IDLE, STATUS_BUSY, STATUS_COMPLETED


class FleetController:
    """
    Central orchestrator for the Unitree R1 fleet.
    Assigns tasks to robots and coordinates multi-robot operations.
    Tracks per-robot status: idle, busy, completed.
    """

    def __init__(self):
        self._robots: dict[str, RobotManager] = {}
        self._robot_status: dict[str, str] = {}  # robot_id -> idle|busy|completed
        self._active_tasks: list[dict] = []  # { task_id, robot_id, spec }
        self._completed_tasks: list[dict] = []

    def register_robot(self, robot_id: str, robot_manager: RobotManager | None = None, **kwargs) -> RobotManager:
        """
        Register a robot with the fleet.
        If robot_manager is provided, use it; else create one from kwargs (host, sim).
        """
        if robot_manager is None:
            robot_manager = RobotManager(robot_id=robot_id, **kwargs)
        self._robots[robot_id] = robot_manager
        self._robot_status[robot_id] = STATUS_IDLE
        return robot_manager

    def get_robot(self, robot_id: str) -> RobotManager | None:
        """Return RobotManager for robot_id, or None if not registered."""
        return self._robots.get(robot_id)

    def assign_task(self, task_id: str, robot_id: str, task_spec: dict) -> None:
        """
        Assign a high-level task to a robot. Marks robot busy and records active task.
        Pilot should then execute the task via get_robot(robot_id) and call report_task_done().
        """
        if robot_id not in self._robots:
            raise ValueError(f"Robot {robot_id} not registered")
        self._robot_status[robot_id] = STATUS_BUSY
        self._active_tasks.append({"task_id": task_id, "robot_id": robot_id, "spec": task_spec})

    def report_task_done(self, robot_id: str, task_id: str, result: dict) -> None:
        """Mark task complete and set robot back to idle (or completed for reporting)."""
        self._robot_status[robot_id] = STATUS_IDLE
        # Move from active to completed
        for i, t in enumerate(self._active_tasks):
            if t["task_id"] == task_id and t["robot_id"] == robot_id:
                self._completed_tasks.append({**t, "result": result})
                self._active_tasks.pop(i)
                break

    def set_robot_status(self, robot_id: str, status: str) -> None:
        """Explicitly set robot status (idle, busy, completed). Pilot can use for consistency."""
        if robot_id in self._robot_status:
            self._robot_status[robot_id] = status

    def get_fleet_status(self) -> dict:
        """Return current status of all robots and active/completed tasks."""
        robots = []
        for rid, mgr in self._robots.items():
            s = mgr.get_status()
            s["fleet_status"] = self._robot_status.get(rid, STATUS_IDLE)
            robots.append(s)
        return {
            "robots": robots,
            "active_tasks": list(self._active_tasks),
            "completed_tasks": list(self._completed_tasks[-20:]),  # last 20
        }

    def run(self) -> None:
        """
        Main loop: dispatch tasks, handle completion, resolve conflicts.
        TODO: Implement for fully autonomous loop; pilot currently drives via assign_task + report_task_done.
        """
        pass


# AI extension point: Add functions for multi-robot optimization,
# dynamic re-assignment, and priority-based scheduling here.
