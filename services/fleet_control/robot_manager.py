"""
Individual robot interfaces and SDK wrappers.

Wraps Unitree SDK2 Python (SDK/unitree_sdk2_python) so the rest of the stack uses a
uniform Python API for motion, status, and sensors.

Sim modes:
- sim=True (stub): in-memory only, no DDS; used by pilot_module --sim.
- MuJoCo sim: run SDK/unitree_mujoco/simulate_python/unitree_mujoco.py, then connect
  with domain_id=1 and interface "lo" (see SDK/README.md).
- Real robot: connect with domain_id=0 and the robot's network interface.

Pilot module uses: connect(), get_status(), walk_forward(), turn(), scan_qr_placeholder().

Note: DDS ChannelFactoryInitialize is process-global. For multiple robots in one process
you must use the same (domain_id, interface); for distinct robots use separate processes
or separate interfaces and init only once per (domain_id, interface).
"""

import math
import threading
import time
import zmq
import json
from typing import Any, Optional

# Optional SDK: allow running without unitree_sdk2_python (stub-only).
_sdk_available = False
_sport_client_class = None
_g1_loco_client_class = None
_g1_arm_action_client_class = None
_channel_initialized: dict[tuple[int, str], bool] = {}  # (domain_id, interface) -> bool

try:
    from unitree_sdk2py.core.channel import ChannelFactoryInitialize
    from unitree_sdk2py.core.channel import ChannelSubscriber
    from unitree_sdk2py.go2.sport.sport_client import SportClient
    from unitree_sdk2py.idl.unitree_go.msg.dds_ import SportModeState_
    from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_ as HGLowState_
    from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
    from unitree_sdk2py.g1.arm.g1_arm_action_client import G1ArmActionClient, action_map as g1_action_map

    _sdk_available = True
    _sport_client_class = SportClient
    _g1_loco_client_class = LocoClient
    _g1_arm_action_client_class = G1ArmActionClient
except ImportError:
    ChannelFactoryInitialize = None  # type: ignore
    ChannelSubscriber = None  # type: ignore
    SportClient = None  # type: ignore
    SportModeState_ = None  # type: ignore
    HGLowState_ = None  # type: ignore
    LocoClient = None  # type: ignore
    G1ArmActionClient = None  # type: ignore
    g1_action_map = {}  # type: ignore

# Robot status constants for fleet coordination
STATUS_IDLE = "idle"
STATUS_BUSY = "busy"
STATUS_COMPLETED = "completed"
STATUS_ERROR = "error"
STATUS_DISCONNECTED = "disconnected"

# Default motion params for SDK (Go2 sport mode)
DEFAULT_WALK_VX = 0.2   # m/s forward
DEFAULT_TURN_VYAW = 0.5  # rad/s for turn in place
DEFAULT_G1_WALK_VX = 0.25
DEFAULT_G1_TURN_VYAW = 0.45


def _ensure_channel(domain_id: int, interface: str | None) -> None:
    """Call ChannelFactoryInitialize once per (domain_id, interface) per process."""
    key = (domain_id, interface or "")
    if key in _channel_initialized and _channel_initialized[key]:
        return
    if ChannelFactoryInitialize is None:
        raise RuntimeError("unitree_sdk2_python not installed; use sim=True for stub.")
    ChannelFactoryInitialize(domain_id, interface if interface else None)
    _channel_initialized[key] = True


class RobotManager:
    """
    Interface to a single Unitree robot (Go2 for SDK path; R1/G1 when supported).
    Abstracts SDK calls for motion, status, and sensor data.
    Supports stub sim (sim=True), MuJoCo (domain_id=1, interface="lo"), and real hardware.
    """

    def __init__(
        self,
        robot_id: str,
        host: str = "",
        sim: bool = False,
        *,
        domain_id: int = 0,
        interface: Optional[str] = None,
        robot_type: str = "unitree_r1",
        vendor: str = "unitree_sdk2",
        **kwargs: Any,
    ):
        self.robot_id = robot_id
        self.host = host or "localhost"
        self.sim = sim
        self.domain_id = domain_id
        self.interface = interface or ""
        self.robot_type = robot_type
        self.vendor = vendor
        self.robot_category = kwargs.get("robot_category", self._infer_category(robot_type))
        self._connected = False
        self._sport_client: Any = None
        self._loco_client: Any = None
        self._arm_action_client: Any = None
        self._state_sub: Any = None
        self._last_sport_state: Any = None
        self._last_low_state: Any = None
        self._last_state_timestamp: float | None = None
        self._state_lock = threading.Lock()
        self._last_status: dict[str, Any] = {}
        self._detections: list[str] = []
        self._perception_sub_thread: Optional[threading.Thread] = None

    def _infer_category(self, robot_type: str) -> str:
        """Infer robot category from type."""
        if "go2" in robot_type.lower():
            return "Quadruped"
        elif "r1" in robot_type.lower() or "g1" in robot_type.lower():
            return "Humanoid"
        elif "wheeled" in robot_type.lower() or "mobile" in robot_type.lower():
            return "Wheeled"
        return "Custom"

    def connect(self) -> bool:
        """Establish connection. Stub sim: in-memory. SDK: Go2 sport or G1 loco/arm client."""
        if self.sim:
            self._connected = True
            self._last_status = {
                "robot_id": self.robot_id,
                "status": STATUS_IDLE,
                "battery": 100,
                "pose": {"x": 0, "y": 0, "theta": 0},
                "robot_type": self.robot_type,
                "robot_category": self.robot_category,
                "vendor": self.vendor,
                "telemetry_source": "sim",
                "telemetry_fresh": True,
                "telemetry_age_sec": 0.0,
            }
            return True

        if not _sdk_available:
            self._connected = False
            return False

        try:
            # MuJoCo sim: pass interface="lo". Real robot: pass your NIC, e.g. "enp2s0".
            _ensure_channel(self.domain_id, self.interface or None)
            if self._uses_g1_sdk():
                if _g1_loco_client_class is None:
                    raise RuntimeError("G1 loco client is unavailable in unitree_sdk2py")
                self._loco_client = _g1_loco_client_class()
                self._loco_client.SetTimeout(10.0)
                self._loco_client.Init()
                if _g1_arm_action_client_class is not None:
                    self._arm_action_client = _g1_arm_action_client_class()
                    self._arm_action_client.SetTimeout(10.0)
                    self._arm_action_client.Init()
                if ChannelSubscriber is not None and HGLowState_ is not None:
                    self._state_sub = ChannelSubscriber("rt/lowstate", HGLowState_)
                    self._state_sub.Init(self._on_g1_low_state, 10)
            else:
                if _sport_client_class is None:
                    raise RuntimeError("Go2 sport client is unavailable in unitree_sdk2py")
                self._sport_client = _sport_client_class()
                self._sport_client.SetTimeout(10.0)
                self._sport_client.Init()
                # Subscribe to live state (position, velocity) from robot/sim
                if ChannelSubscriber is not None and SportModeState_ is not None:
                    self._state_sub = ChannelSubscriber("rt/sportmodestate", SportModeState_)
                    self._state_sub.Init(self._on_sport_state, 10)
            self._connected = True
            
            # Start perception subscriber thread
            self._start_perception_subscriber()
            
            self._last_status = {
                "robot_id": self.robot_id,
                "status": STATUS_IDLE,
                "battery": 100,
                "pose": {"x": 0, "y": 0, "theta": 0},
                "robot_type": self.robot_type,
                "robot_category": self.robot_category,
                "vendor": self.vendor,
                "telemetry_source": "g1_lowstate" if self._uses_g1_sdk() else "go2_sportmodestate",
                "telemetry_fresh": False if self._uses_g1_sdk() else True,
            }
            return True
        except Exception:
            self._connected = False
            self._sport_client = None
            self._loco_client = None
            self._arm_action_client = None
            self._state_sub = None
            return False

    def _uses_g1_sdk(self) -> bool:
        normalized = self.robot_type.lower()
        return "g1" in normalized or self.robot_category.lower() == "humanoid"

    def is_humanoid(self) -> bool:
        return self._uses_g1_sdk()

    def supports_arm_actions(self) -> bool:
        return self._arm_action_client is not None

    def available_actions(self) -> list[str]:
        if not self._uses_g1_sdk():
            return []
        return sorted(g1_action_map.keys())

    def _on_sport_state(self, msg: Any) -> None:
        """Callback for rt/sportmodestate: cache latest pose/velocity for get_status()."""
        with self._state_lock:
            self._last_sport_state = msg
            self._last_state_timestamp = time.time()
            # position[0]=x, position[1]=y, position[2]=z; velocity same; yaw from imu or velocity
            if hasattr(msg, "position") and len(msg.position) >= 3:
                prev_pose = self._last_status.get("pose", {"x": 0, "y": 0, "theta": 0})
                self._last_status["pose"] = {
                    "x": float(msg.position[0]),
                    "y": float(msg.position[1]),
                    "theta": prev_pose.get("theta", 0),  # heading not in SportModeState; use last or 0
                }
            if hasattr(msg, "velocity") and len(msg.velocity) >= 3:
                self._last_status["velocity"] = [float(msg.velocity[0]), float(msg.velocity[1]), float(msg.velocity[2])]

    def _on_g1_low_state(self, msg: Any) -> None:
        """Callback for G1 rt/lowstate: normalize posture, IMU, and motor-health telemetry."""
        now = time.time()
        with self._state_lock:
            self._last_low_state = msg
            self._last_state_timestamp = now
            pose = dict(self._last_status.get("pose", {"x": 0.0, "y": 0.0, "theta": 0.0}))
            imu = getattr(msg, "imu_state", None)
            rpy = [0.0, 0.0, 0.0]
            gyro = [0.0, 0.0, 0.0]
            accel = [0.0, 0.0, 0.0]
            quaternion = [0.0, 0.0, 0.0, 1.0]
            if imu is not None:
                rpy = [float(v) for v in getattr(imu, "rpy", [0.0, 0.0, 0.0])]
                gyro = [float(v) for v in getattr(imu, "gyroscope", [0.0, 0.0, 0.0])]
                accel = [float(v) for v in getattr(imu, "accelerometer", [0.0, 0.0, 0.0])]
                quaternion = [float(v) for v in getattr(imu, "quaternion", [0.0, 0.0, 0.0, 1.0])]
            pose["theta"] = float(rpy[2]) if len(rpy) >= 3 else pose.get("theta", 0.0)

            motor_states = list(getattr(msg, "motor_state", []) or [])
            motor_temps: list[float] = []
            motor_voltages: list[float] = []
            fault_count = 0
            moving_count = 0
            for motor in motor_states:
                temps = [float(v) for v in getattr(motor, "temperature", [])]
                motor_temps.extend(temps)
                try:
                    motor_voltages.append(float(getattr(motor, "vol", 0.0)))
                except Exception:
                    pass
                try:
                    if abs(float(getattr(motor, "dq", 0.0))) > 0.01:
                        moving_count += 1
                except Exception:
                    pass
                try:
                    if int(getattr(motor, "motorstate", 0)) != 0:
                        fault_count += 1
                except Exception:
                    pass

            self._last_status.update(
                {
                    "pose": pose,
                    "telemetry_source": "g1_lowstate",
                    "telemetry_fresh": True,
                    "telemetry_age_sec": 0.0,
                    "control_mode": {
                        "mode_machine": int(getattr(msg, "mode_machine", 0)),
                        "mode_pr": int(getattr(msg, "mode_pr", 0)),
                    },
                    "tick": int(getattr(msg, "tick", 0)),
                    "imu": {
                        "rpy": rpy,
                        "gyroscope": gyro,
                        "accelerometer": accel,
                        "quaternion": quaternion,
                        "temperature_c": float(getattr(imu, "temperature", 0.0)) if imu is not None else None,
                    },
                    "motion_summary": {
                        "joint_motion_count": moving_count,
                    },
                    "motor_summary": {
                        "count": len(motor_states),
                        "avg_temperature_c": round(sum(motor_temps) / len(motor_temps), 2) if motor_temps else None,
                        "max_temperature_c": max(motor_temps) if motor_temps else None,
                        "avg_voltage": round(sum(motor_voltages) / len(motor_voltages), 2) if motor_voltages else None,
                        "fault_count": fault_count,
                    },
                    "battery": self._last_status.get("battery"),
                }
            )

    def get_status(self) -> dict:
        """Return current robot state including type and vendor info."""
        if not self._connected:
            return {
                "robot_id": self.robot_id,
                "status": STATUS_DISCONNECTED,
                "robot_type": self.robot_type,
                "robot_category": self.robot_category,
                "vendor": self.vendor,
            }
        # Ensure robot metadata is always present
        status = dict(self._last_status)
        status.setdefault("robot_type", self.robot_type)
        status.setdefault("robot_category", self.robot_category)
        status.setdefault("vendor", self.vendor)
        if self._last_state_timestamp is not None:
            age = max(0.0, time.time() - self._last_state_timestamp)
            status["telemetry_age_sec"] = round(age, 3)
            status["telemetry_fresh"] = age < 2.0
        else:
            status.setdefault("telemetry_fresh", False if self._uses_g1_sdk() else True)
        return status

    def _set_status(self, status: str, **kwargs: Any) -> None:
        """Update internal status for sim/fleet tracking."""
        self._last_status["status"] = status
        self._last_status.update(kwargs)

    def send_motion_command(self, command: dict) -> bool:
        """
        Send motion command. command: {"type": "walk_forward"|"turn"|..., "params": {...}}
        """
        cmd_type = command.get("type", "")
        params = command.get("params", {})

        if self.sim:
            if cmd_type == "walk_forward":
                meters = params.get("meters", 0)
                time.sleep(0.3)
                self._last_status.setdefault("pose", {"x": 0, "y": 0, "theta": 0})
                self._last_status["pose"]["x"] += meters
                return True
            if cmd_type == "turn":
                degrees = params.get("degrees", 0)
                time.sleep(0.2)
                self._last_status.setdefault("pose", {"x": 0, "y": 0, "theta": 0})
                self._last_status["pose"]["theta"] = (
                    self._last_status["pose"].get("theta", 0) + degrees
                ) % 360
                return True
            return True

        # SDK path
        if self._uses_g1_sdk():
            return self._send_g1_motion_command(cmd_type, params)

        if not self._sport_client:
            return False
        try:
            if cmd_type == "walk_forward":
                meters = params.get("meters", 0)
                vx = params.get("vx", DEFAULT_WALK_VX)
                if meters <= 0:
                    return True
                duration = meters / vx
                self._sport_client.Move(vx, 0.0, 0.0)
                time.sleep(duration)
                self._sport_client.StopMove()
                return True
            if cmd_type == "turn":
                degrees = params.get("degrees", 0)
                vyaw_deg = params.get("vyaw_deg_per_sec", 90.0)
                if abs(degrees) < 1e-6:
                    return True
                vyaw = math.radians(vyaw_deg) if degrees >= 0 else -math.radians(vyaw_deg)
                duration = abs(math.radians(degrees) / vyaw)
                self._sport_client.Move(0.0, 0.0, vyaw)
                time.sleep(duration)
                self._sport_client.StopMove()
                return True
        except Exception:
            return False
        return True

    def _send_g1_motion_command(self, cmd_type: str, params: dict) -> bool:
        if not self._loco_client:
            return False
        try:
            if cmd_type == "walk_forward":
                meters = float(params.get("meters", 0))
                vx = float(params.get("vx", DEFAULT_G1_WALK_VX))
                if meters <= 0:
                    return True
                self._loco_client.Start()
                duration = meters / max(vx, 0.05)
                self._loco_client.Move(vx, 0.0, 0.0)
                time.sleep(duration)
                self._loco_client.StopMove()
                return True
            if cmd_type == "turn":
                degrees = float(params.get("degrees", 0))
                vyaw = float(params.get("vyaw", DEFAULT_G1_TURN_VYAW))
                if abs(degrees) < 1e-6:
                    return True
                self._loco_client.Start()
                signed_vyaw = vyaw if degrees >= 0 else -vyaw
                duration = abs(math.radians(degrees) / max(abs(signed_vyaw), 0.05))
                self._loco_client.Move(0.0, 0.0, signed_vyaw)
                time.sleep(duration)
                self._loco_client.StopMove()
                return True
            if cmd_type == "wave_hand":
                if self._arm_action_client is None:
                    return False
                action_id = g1_action_map.get("high wave")
                if action_id is None:
                    return False
                return self._arm_action_client.ExecuteAction(action_id) == 0
            if cmd_type == "shake_hand":
                if self._loco_client is None:
                    return False
                self._loco_client.ShakeHand()
                time.sleep(3.0)
                self._loco_client.ShakeHand()
                return True
        except Exception:
            return False
        return False

    def perform_action(self, action_name: str) -> bool:
        """Execute a named G1 arm action when available."""
        if self.sim:
            time.sleep(0.5)
            self._last_status["last_action"] = action_name
            return True
        if not self._uses_g1_sdk() or self._arm_action_client is None:
            return False
        action_id = g1_action_map.get(action_name.lower())
        if action_id is None:
            return False
        try:
            ok = self._arm_action_client.ExecuteAction(action_id) == 0
        except Exception:
            return False
        if ok:
            self._last_status["last_action"] = action_name
        return ok

    def _start_perception_subscriber(self) -> None:
        """Start background thread to listen for perception results."""
        def sub_loop():
            context = zmq.Context()
            socket = context.socket(zmq.SUB)
            # Match perception_service.py port logic: 5555 + (domain % 100) + 10
            port = 5555 + (self.domain_id % 100) + 10
            socket.connect(f"tcp://localhost:{port}")
            socket.setsockopt_string(zmq.SUBSCRIBE, "")
            socket.setsockopt(zmq.RCVTIMEO, 1000) # 1s timeout
            
            while self._connected:
                try:
                    msg = socket.recv_string()
                    with self._state_lock:
                        self._detections = json.loads(msg)
                        self._last_status["detections"] = self._detections
                except zmq.Again:
                    continue
                except Exception:
                    break
            socket.close()
            context.term()

        self._perception_sub_thread = threading.Thread(target=sub_loop, daemon=True)
        self._perception_sub_thread.start()

    def stand_up(self) -> bool:
        """Command the robot to stand up. Required for humanoid stability."""
        self._set_status(STATUS_BUSY)
        if self.sim:
            time.sleep(1.0)
            self._set_status(STATUS_IDLE)
            return True

        try:
            if self._uses_g1_sdk():
                if not self._loco_client:
                    return False
                self._loco_client.Damp()
                time.sleep(0.3)
                self._loco_client.Squat2StandUp()
            else:
                if not self._sport_client:
                    return False
                self._sport_client.StandUp()
            time.sleep(1.0)
            self._set_status(STATUS_IDLE)
            return True
        except Exception:
            self._set_status(STATUS_ERROR)
            return False

    def recovery_stand(self) -> bool:
        """Command the robot to perform a recovery stand (e.g. after falling)."""
        self._set_status(STATUS_BUSY)
        if self.sim:
            time.sleep(2.0)
            self._set_status(STATUS_IDLE)
            return True

        try:
            if self._uses_g1_sdk():
                if not self._loco_client:
                    return False
                self._loco_client.Damp()
                time.sleep(0.3)
                self._loco_client.Lie2StandUp()
            else:
                if not self._sport_client:
                    return False
                self._sport_client.RecoveryStand()
            time.sleep(2.0)
            self._set_status(STATUS_IDLE)
            return True
        except Exception:
            self._set_status(STATUS_ERROR)
            return False

    def walk_forward(self, meters: float) -> bool:
        """Walk forward by the given distance in meters. SDK: Move(vx,0,0) then StopMove()."""
        self._set_status(STATUS_BUSY)
        ok = self.send_motion_command({"type": "walk_forward", "params": {"meters": meters}})
        self._set_status(STATUS_IDLE if ok else STATUS_ERROR)
        return ok

    def turn(self, degrees: float) -> bool:
        """Turn in place by the given degrees (positive = counterclockwise)."""
        self._set_status(STATUS_BUSY)
        ok = self.send_motion_command({"type": "turn", "params": {"degrees": degrees}})
        self._set_status(STATUS_IDLE if ok else STATUS_ERROR)
        return ok

    def get_sensor_data(self, sensor_type: str = "") -> dict:
        """Return sensor data. TODO: Implement camera/lidar via SDK when needed."""
        if self.sim:
            return {"sensor_type": sensor_type or "camera", "sim": True, "data": None}
        return {"sensor_type": sensor_type or "camera", "sdk": True, "data": None}

    def disconnect(self) -> None:
        """Clean up connection. SDK: stop move, clear state sub and client reference."""
        if not self.sim:
            try:
                if self._sport_client:
                    self._sport_client.StopMove()
                if self._loco_client:
                    self._loco_client.StopMove()
            except Exception:
                pass
            self._sport_client = None
            self._loco_client = None
            self._arm_action_client = None
            if getattr(self._state_sub, "Close", None):
                try:
                    self._state_sub.Close()
                except Exception:
                    pass
            self._state_sub = None
        self._connected = False
        self._last_status["status"] = STATUS_DISCONNECTED


def sdk_available() -> bool:
    """Return True if unitree_sdk2_python is installed and usable."""
    return _sdk_available
