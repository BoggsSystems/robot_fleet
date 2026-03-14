# Robot Fleet — Unitree R1 Fleet Control

A complete software solution to control fleets of **Unitree R1 humanoid robots** for warehouse, retail, and manufacturing automation.

## Goals

- **Multi-robot orchestration**: Central coordination, task assignment, and conflict-free scheduling.
- **High-level tasks**: Inventory scanning, restocking, picking/placing, and custom workflows.
- **Monitoring & analytics**: Real-time dashboard with robot positions, task completion, and KPI metrics.
- **Simulation**: Virtual environment for single and multi-robot testing before deployment.

## Project Structure

```
robot_fleet/
├── SDK/                 # Unitree SDK2 Python + unitree_mujoco (git submodules)
├── fleet_control/       # Multi-robot orchestration, task assignment, coordination
├── tasks/               # High-level task definitions (inventory, restock, pick/place, etc.)
├── dashboard/           # Analytics and monitoring UI
├── simulation/          # Virtual environment and testing scripts
├── data/                # Logs, metrics, and history
├── docs/                # Architecture diagrams and user guides (optional)
├── requirements.txt     # Python/C++ dependencies
└── README.md            # This file
```

## Setup Instructions

1. **Clone the repository (with SDK submodules)**
   ```bash
   git clone <repo-url>
   cd robot_fleet
   git submodule update --init --recursive
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Linux/macOS
   # or: venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install the Unitree SDK for full E2E (recommended)**
   - See `SDK/README.md`. In short: build CycloneDDS if needed, then `pip install -e SDK/unitree_sdk2_python`. For MuJoCo sim also install `mujoco` and `pygame` (in `requirements.txt`).

5. **Configure environment (when needed)**
   - Copy any `.env.example` to `.env` and set robot IPs, API keys, and paths.

## Running Pilots

- **Stub (no SDK):** `python -m fleet_control.pilot_module --sim` — runs the task sequence in-memory and logs to `data/logs/`.
- **Full E2E with SDK (MuJoCo or real robot):** Install the Unitree SDK (see `SDK/README.md`), then:
  - **MuJoCo:** In one terminal start the sim (`cd SDK/unitree_mujoco/simulate_python && python3 unitree_mujoco.py`). In another run `python -m fleet_control.pilot_module --mujoco --robots 1`. Tasks (walk, turn, scan, report) are sent over DDS to the Go2 in the viewer.
  - **Real robot:** `python -m fleet_control.pilot_module --interface <your-NIC> --robots 1` (e.g. `--interface enp2s0`).
- If the SDK is installed and you run the pilot with no flags, it defaults to MuJoCo (domain 1, loopback); have the sim running first.
- **Dashboard**: Start the monitoring UI with `dashboard/dashboard.py` (when implemented).
- **Simulation**: Run `simulation/sim_test.py` for multi-robot coordination tests.

## Development

- Use **Python 3.x** for orchestration and dashboard.
- Extension points are marked with `# TODO:` and `# AI extension point:` for AI-assisted code generation.
- Robot interface is in `fleet_control/robot_manager.py`; it uses `SDK/unitree_sdk2_python` for connect, move, turn, and live state (SportModeState) when the SDK is installed.

## License

[Specify your license here.]
