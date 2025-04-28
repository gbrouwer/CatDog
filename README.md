# CatDog System Overview

---

## Project Vision

CatDog is a **modular, distributed, bio-inspired nervous system** for robotics, simulation, and autonomous systems.

Modules interact **only** via **one-way asynchronous messages** through lightweight WebSocket connections.
They operate in **self-organized closed loops**, enabling truly adaptive behavior.

The **Agent** is responsible for:
- Spinning up local modules
- Managing heartbeats
- Monitoring overall system health ("Vibe System")
- Cleaning up leftover processes at boot
- Managing communication lifecycles

---

## 🚀 Key Features

- **Fully asynchronous Agent framework**
- **Boot/Start lifecycle** for each module
- **Heartbeat monitoring** per module
- **Distributed message routing** (via WebSockets)
- **Automatic zombie process cleanup** at Agent startup
- **Modular actuator support** (e.g., PCSpeaker)
- **Vibe System**: live monitoring of system health

---

## System Updates (April 27, 2025)

### 1. Full Async Agent Refactor
- `Agent.start()` now **fully async**.
- Each module is:
  - `boot()`ed (self-diagnostics first)
  - `start()`ed (connects to upstream nodes)
- `stop()` gracefully halts all modules.

### 2. Zombie Process Cleanup
- Agent kills leftover `python.exe` processes (Windows only).

### 3. Vibe System
- `VibeSender` broadcasts module statuses.
- `VibeListener` receives heartbeat signals.

### 4. New Module: `PCSpeaker`
- Actuator module playing `.wav` files through system speakers.
- `boot()` ensures audio works before startup.
- `receive()` plays sound when a message is received.

### 5. Test Suite: `test_pcspeaker.py`
- Standalone sound playback verification.
- Validates file paths and `.wav` file availability.

---

## Folder Structure

```plaintext
/your_project/
├── src/
│   ├── catdog/
│   │   └── modules/
│   │       └── actuators/
│   │           └── pcspeaker.py
│   ├── catdog/agent.py
│   ├── catdog/vibes.py
├── assets/
│   └── sounds/
│       └── boot.wav
├── configs/
│   └── test_local.yaml
├── tests/
│   └── test_pcspeaker.py
├── setup.py
```

---

## Future Directions

- Build a Vibe visualizer dashboard.
- Heartbeat-based self-healing system (auto module restart).
- Secure WebSocket messaging (encryption/authentication).
- Dynamic module discovery and runtime expansion.
- Real distributed deployment (PC + Raspberry Pi split).

---

## Final Status (April 27, 2025)

| Subsystem | Status |
|:---|:---|
| Agent Boot | ✅ Stable |
| Modules Start/Stop | ✅ Working |
| Messaging | ✅ Operational |
| PCSpeaker Actuator | ✅ Functional |
| Tests | ✅ Passing |
| Documentation | ✅ Complete |

---

*Weird stuff our LLM assistant wanted us to put here...*
