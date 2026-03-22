# Unitree SDK and simulation

This directory contains the official Unitree SDK and MuJoCo simulator as **git submodules**:

| Path | Description |
|------|-------------|
| **unitree_sdk2_python** | Python interface for Unitree SDK2 — use this from `fleet_control/robot_manager.py` to talk to real robots or the sim. |
| **unitree_mujoco** | Official MuJoCo simulator. Same DDS protocol as hardware; your Python SDK code can target the sim (loopback) or the robot. |

---

## Run a simulation first (what to test)

### Option A: Stub sim (no SDK install) — run now

From the **repo root**, with no Unitree SDK or MuJoCo installed:

```bash
cd robot_fleet
python -m fleet_control.pilot_module --sim --robots 2
```

This runs the in-repo pilot with in-memory robot stubs: walk 2 m, turn 90°, scan (placeholder), report (placeholder), alternating between two “robots.” Use it to verify fleet logic, task assignment, and logging under `data/logs/`.

### Option B: MuJoCo + SDK (Go2 in sim) — after installing the SDK

Once you’ve installed **unitree_sdk2_python** and **mujoco** (see sections below), you can drive the **MuJoCo** simulator with the real SDK:

1. **Terminal 1 — start the sim**
   ```bash
   cd robot_fleet/SDK/unitree_mujoco/simulate_python
   python3 unitree_mujoco.py
   ```
   A MuJoCo window opens with a **Go2** quadruped (default in `config.py`).

2. **Terminal 2 — send commands to the sim**
   ```bash
   cd robot_fleet/SDK/unitree_mujoco/example/python
   python3 stand_go2.py
   ```
   When prompted, press Enter. The Go2 in the sim will stand up, then stand down. (No args = use domain 1 and loopback, so it talks to the sim.)

**Alternative test** (low-level motor commands and state printout):

- Terminal 1: same as above (`unitree_mujoco.py`).
- Terminal 2:
  ```bash
  cd robot_fleet/SDK/unitree_mujoco/simulate_python/test
  python3 test_unitree_sdk2.py
  ```
  You’ll see pose/IMU printed in the terminal and the robot receiving torque commands in the viewer.

So: **first** run Option A to confirm the repo; **then** install the SDK and run Option B to confirm the SDK + MuJoCo pipeline.

**Run the fleet pilot against MuJoCo:** After the sim is running (Terminal 1), in another terminal from the repo root:
```bash
python -m fleet_control.pilot_module --mujoco --robots 1
```
This sends walk/turn/scan/report tasks to the Go2 in the sim. Use `--interface enp2s0` (and no `--mujoco`) to target a real robot instead.

---

## First-time setup (clone with submodules)

If you just cloned the repo, pull the SDK and sim in one step:

```bash
cd /path/to/robot_fleet
git submodule update --init --recursive
```

## 1. Install unitree_sdk2_python

Used for all Python control and for connecting to the MuJoCo sim.

### Dependencies

- Python ≥ 3.8
- **cyclonedds** (DDS middleware) — often needs to be built from source; see below.
- numpy, opencv-python (pip)

### Install CycloneDDS (if needed)

If `pip install -e .` fails with “Could not locate cyclonedds”, build and set `CYCLONEDDS_HOME`:

```bash
cd ~
git clone https://github.com/eclipse-cyclonedds/cyclonedds -b releases/0.10.x
cd cyclonedds && mkdir build install && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../install
cmake --build . --target install
export CYCLONEDDS_HOME=~/cyclonedds/install   # add to your shell profile for persistence
```

### Install the Python SDK from this repo

```bash
cd robot_fleet/SDK/unitree_sdk2_python
pip install -e .
```

See [unitree_sdk2_python/README.md](unitree_sdk2_python/README.md) for more detail and FAQ.

## 2. Run MuJoCo simulation (no hardware)

The simulator uses the same DDS messages as the robot. Use **domain id 1** and interface **lo** (loopback) so your control code talks to the sim instead of the network.

### Dependencies for MuJoCo Python sim

```bash
pip install mujoco pygame
```

### Start the Python simulator

In a **first terminal**:

```bash
cd robot_fleet/SDK/unitree_mujoco/simulate_python
python3 unitree_mujoco.py
```

You should see the MuJoCo window with a robot (default is Go2). Config is in `simulate_python/config.py`: robot model, `DOMAIN_ID = 1`, `INTERFACE = "lo"`.

### Run your control code against the sim

In a **second terminal**, run any unitree_sdk2_python example (or later, your `robot_manager`-backed pilot) **without** a network interface, so it uses the sim’s domain and loopback:

```bash
# Example: stand_go2 from unitree_mujoco
cd robot_fleet/SDK/unitree_mujoco/example/python
python3 stand_go2.py

# With real robot you would pass the interface, e.g.:
# python3 stand_go2.py enp2s0
```

The examples use `ChannelFactoryInitialize(1, "lo")` when no interface is given — that connects to the running MuJoCo sim.

### Sim vs real in this repo

- **Stub sim** (no SDK): `pilot_module --sim` uses in-memory stubs only (no MuJoCo, no DDS).
- **MuJoCo sim**: Start `SDK/unitree_mujoco/simulate_python/unitree_mujoco.py`, then run your SDK-based code with domain 1 and interface `lo` so it talks to the sim.
- **Real robot**: Run SDK-based code with domain 0 and the network interface connected to the robot (e.g. `enp2s0`).

When we wire `robot_manager.py` to the real SDK, we’ll use the same pattern: no-interface / `lo` + domain 1 for MuJoCo, and interface + domain 0 for hardware.

## Supported robots (MuJoCo / SDK2)

Unitree_mujoco documents support for **Go2, B2, B2w, H1** in the config; **G1** uses the `unitree_hg` IDL (see unitree_mujoco readme). **R1** may work with the same or a similar IDL; check Unitree docs and the sim’s `unitree_robots` and config for R1-specific scenes.

## Links

- [Unitree developer docs](https://support.unitree.com/home/en/developer)
- [unitree_sdk2_python](https://github.com/unitreerobotics/unitree_sdk2_python)
- [unitree_mujoco](https://github.com/unitreerobotics/unitree_mujoco)
- [unitree_sdk2](https://github.com/unitreerobotics/unitree_sdk2) (C++ core; optional unless building SDK from source)
