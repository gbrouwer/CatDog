# CatDog System

## Overview

The CatDog Project is a modular, distributed, event-driven system for coordinating hardware and software modules across multiple devices. It was built to simulate a bio-inspired nervous system that allows sensor-based perception and actuator-based response in real time.

The system is designed for cross-device operation, currently running distributed agents on a PC and a Raspberry Pi. Modules interact solely via asynchronous WebSocket messages, enabling loose coupling and scalable orchestration.

## Architecture

The architecture is composed of the following layers:

- **Agent Layer**: Orchestrates modules, launches remote agents, monitors module health via heartbeats.
- **Messaging Layer**: Manages inter-module communication over WebSockets.
- **Module Layer**: Sensor and actuator components, each with defined behavior, state, and interface.
- **Infrastructure Layer**: Utility modules for asset management, logging, and shared enums.

Modules communicate via a Global Communication Channel (GCC), and system presence is detected and tracked through a UDP-based Vibe system.

## Folder Structure

```
CatDog/
├── assets/                  # Audio files and data assets
├── configs/                 # YAML system configuration files
├── src/
│   ├── agent.py             # Agent controller script
│   ├── gcc.py               # Global Communication Channel WebSocket server
│   ├── launcher.py          # Module launcher entry point
│   ├── log.py               # Centralized logger with color formatting and padding
│   ├── asset_manager.py     # Resolves file paths for assets
│   ├── enums.py             # Heartbeat and connection enums
│   ├── heartbeat.py         # Heartbeat message structure
│   ├── messaging/
│   │   ├── sender.py        # Sends messages to the GCC
│   │   ├── receiver.py      # Receives messages from the GCC
│   │   ├── module_link_server.py   # Handles module-to-module WebSocket reception
│   │   ├── module_link_client.py   # Handles module-to-module WebSocket sending
│   ├── modules/
│   │   ├── actuators/
│   │   │   └── emitters/
│   │   │       └── sounds/
│   │   │           ├── sound_emitter.py
│   │   │           └── sound.py
│   │   └── sensors/
│   │       ├── sensor.py
│   │       └── sounds/
│   │           └── ultrasonic_sensor.py
│   └── vibes.py             # UDP heartbeat system
└── tests/                   # Test scripts (if applicable)
```

## Class Index

| Class                      | Description                                                                 |
|---------------------------|-----------------------------------------------------------------------------|
| `Agent`                   | Central orchestrator, launches modules, manages heartbeats and remote agents |
| `Sender`                  | Sends structured JSON messages to the GCC                                   |
| `Receiver`                | Receives and dispatches messages from the GCC                               |
| `ModuleLinkClient`        | Connects directly to another module's WebSocket for data ingestion          |
| `ModuleLinkServer`        | Hosts a WebSocket server for module-to-module transmission                   |
| `SoundEmitter`            | Actuator that plays a sound when a threshold event is received              |
| `UltrasonicSensor`        | Sensor that measures distance and broadcasts values over WebSocket          |
| `Sensor`                  | Abstract base class for all sensor modules                                  |
| `Sound`                   | Abstract base class for audio-emitting modules                              |
| `AssetManager`            | Resolves full asset file paths in a platform-safe way                       |
| `Heartbeat`               | Message wrapper for broadcasting module health and status                   |
| `HeartbeatStatus`         | Enum for module states (booting, operational, processing, error)            |
| `ConnectionStatus`        | Enum for module link status (connected, lost)                               |
| `VibeSender`              | Sends out UDP heartbeats for device visibility                              |
| `VibeListener`            | Listens for UDP heartbeats and maintains device state map                   |

## Usage

1. Configure your system in `configs/catdog_test.yaml`
2. Run the primary agent on the PC:

```powershell
.\start-catdog.ps1
```

3. The primary agent will automatically launch the remote agent on the Raspberry Pi via SSH and `tmux`

## Status

- MVP Complete: UltrasonicSensor on Pi triggers sound on PC
- Cross-device messaging, modular boot/start/stop lifecycle verified
- Fully structured logging and centralized message routing implemented

## Roadmap

- Authentication on GCC
- Secure messaging and signed heartbeats
- Monitoring UI for status maps
- Runtime module injection and dynamic discovery
- Unit and integration test coverage
