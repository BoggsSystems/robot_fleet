"""
Logging utilities for robot tasks and fleet operations.

Centralizes log format, rotation, and optional forwarding to metrics/analytics.
Writes to data/logs/ with timestamps and robot ID for pilot and dashboard use.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any

# Log directory: project_root/data/logs
_LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(_LOG_DIR, exist_ok=True)

# Single pilot/fleet log file; can be split by date later (AI extension point)
_PILOT_LOG = os.path.join(_LOG_DIR, "pilot.log")
_METRICS_LOG = os.path.join(_LOG_DIR, "metrics.jsonl")


def _ensure_log_dir() -> None:
    os.makedirs(_LOG_DIR, exist_ok=True)


def get_task_logger(task_id: str, robot_id: str = "") -> logging.Logger:
    """
    Return a logger configured for a specific task and optional robot.
    Logs to data/logs/pilot.log with consistent format.
    """
    _ensure_log_dir()
    name = f"task.{task_id}.{robot_id}" if robot_id else f"task.{task_id}"
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(_PILOT_LOG, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
        )
        logger.addHandler(handler)
    return logger


def log_task_start(task_id: str, robot_id: str, spec: dict) -> None:
    """Record task start with timestamp; written to pilot.log."""
    _ensure_log_dir()
    logger = get_task_logger(task_id, robot_id)
    logger.info("TASK_START | robot_id=%s | spec=%s", robot_id, spec)


def log_task_end(
    task_id: str, robot_id: str, result: dict, duration_sec: float
) -> None:
    """Record task completion and duration to pilot.log."""
    _ensure_log_dir()
    logger = get_task_logger(task_id, robot_id)
    logger.info(
        "TASK_END | robot_id=%s | result=%s | duration_sec=%.2f",
        robot_id,
        result,
        duration_sec,
    )
    # Append one line to metrics JSONL for dashboard/KPI (AI extension point)
    _append_metric(
        {
            "event": "task_end",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "task_id": task_id,
            "robot_id": robot_id,
            "result": result,
            "duration_sec": round(duration_sec, 2),
        }
    )


def log_robot_status(robot_id: str, status: dict) -> None:
    """Record robot status snapshot to pilot.log and optional metrics."""
    _ensure_log_dir()
    logger = get_task_logger("fleet", robot_id)
    logger.debug("ROBOT_STATUS | robot_id=%s | status=%s", robot_id, status)


def _append_metric(record: dict[str, Any]) -> None:
    """Append a single JSON line to data/logs/metrics.jsonl for dashboard."""
    _ensure_log_dir()
    with open(_METRICS_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def get_log_dir() -> str:
    """Return path to data/logs for tests and dashboard."""
    return _LOG_DIR
