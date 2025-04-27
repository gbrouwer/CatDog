
# CatDog Project Documentation

## 1. General Overview

### Project Name: CatDog Autonomous Distributed Agent System

---

## Vision and Philosophy

We are building CatDog, a fully modular, distributed, and semi-autonomous robotic intelligence system, designed for real-world learning, adaptability, and resilience.

CatDog is intended to:

- Emulate real biological systems (nervous systems, modular brains)
- Operate across multiple physical devices (PC + Raspberry Pi + future devices)
- Enable intelligent behavior to emerge from decentralized communication
- Be extensible and future-proof for true multi-agent distributed intelligence

Inspired by:

| Thinker | Core Ideas |
|---------|------------|
| Marvin Minsky | Society of Mind — intelligence from interacting agents |
| Rodney Brooks | Subsumption architecture — bottom-up behavior |
| Modern Swarm Robotics | Local rules produce global intelligence |
| NASA/Voyager missions | System adaptability, self-diagnosis, remote upgrades |
| Biological Systems | Distributed pre-processing (retina, cochlea, muscle spindles) |

---

## Core Architectural Principles

| Principle | Meaning |
|-----------|---------|
| Modularity | Every sensor, actuator, body part is an independent module |
| Distributed Intelligence | No central brain micromanages actions |
| Emergent Behavior | Intelligence arises from interactions between modules |
| Robust Communication | Messages, queues, pathways drive the system |
| Heartbeat Monitoring | Continuous health checking of all parts |
| Global Signal System | Critical events can broadcast system-wide awareness |

---

## Key Concepts

- **Agent**: The entity that spawns and orchestrates modules according to a configuration.
- **Module**: The fundamental building block (sensor, actuator, processor).
- **Message**: The packet of communication flowing between modules.
- **Global Bus**: Broadcasts critical signals to all modules (e.g., "SELF_TEST", "SHUTDOWN").
- **Heartbeat**: Regular life signals from each module to detect failure.
- **Boot Sequence**: Ensures all parts are alive before entering operational mode.
- **Closed Loop**: Sensors → Processors → Actuators → Environment → back to Sensors.

---

## System Flow

Agent → Spawn Modules from Config → Direct Tests → Setup Communication → Broadcast SELF_TEST → Autonomous Module Communication → Closed Loop Behavior

---

## Why This Matters

- Resilient
- Scalable
- Adaptable
- Educational
- Research-Grade

---

## 2. Technical Deep Dive

### `agent.py`

The orchestrator:

- `load_config()`
- `setup_environment()`
- `build_modules()`
- `start()`, `stop()`
- `monitor_heartbeats()`, `update_heartbeat(module_name)`
- (Planned) `boot_sequence()`

---

### `module.py`

Base unit:

- `start()`, `stop()`
- `_listen()`, `_broadcast()`
- `receive(message)`, `receive_global(message)`
- `send_output(content)`

---

### `message.py`

```python
class Message:
    def __init__(self, sender, content, timestamp=None):
        self.sender = sender
        self.content = content
        self.timestamp = timestamp or time.time()
```

---

### Communication System

- Input/Output Queues
- Message objects
- Subscriptions
- Transport-agnostic future design

---

### Heartbeat System

- Periodic heartbeat signals
- Agent monitors health

---

## 3. What's Next

Now that messaging is established, the next step is to build a **real network-transparent messaging infrastructure**. WebSockets are the leading candidate because they provide lightweight, bi-directional communication suitable for modular distributed systems. Other candidates like ZeroMQ and MQTT remain open depending on evolving needs.

---
