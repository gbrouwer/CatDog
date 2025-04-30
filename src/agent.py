import sys
import os

# Dynamically resolve the root project directory based on this file's location
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from log import log, log_error

import yaml
import asyncio
import platform
import argparse
import time
import subprocess
import shlex
import os
import json
import socket
from pathlib import Path
from vibes import VibeSender, VibeListener

class Agent:
    HEARTBEAT_TIMEOUT = 10  # seconds
    HEARTBEAT_CHECK_INTERVAL = 2  # seconds

    def __init__(self, config_path, is_primary=False):
        self.config_path = config_path
        self.is_primary = is_primary
        self.device_name = None
        self.ip_self = self.get_own_ip()
        self.config = {}
        self.modules = {}
        self.connected_devices = {}
        self.last_heartbeats = {}
        self.start_time = time.time()
        self.gcc_process = None
        self.agent_processes = []
        self.load_config()
        self.setup_environment()

    def get_own_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return '127.0.0.1'

    def load_config(self):
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
            self.config = config
            self.devices = config.get('devices', {})
            log("Agent", f"Loaded devices: {list(self.devices.keys())}")
        except Exception as e:
            log_error("Agent", f"ERROR while loading config: {e}")
            raise

    def setup_environment(self):
        system = platform.system()
        if self.is_primary and system != 'Linux' and system != 'Windows':
            log("Agent", "Warning: Primary agent recommended on Linux or Windows.")
        log("Agent", f"Running on {system} at {self.ip_self}")

    def start_gcc_server(self):
        log("Agent", "Starting GCC server...")
        try:
            gcc_script = os.path.join(os.path.dirname(__file__), 'gcc.py')

            # Use venv Python on Windows, system Python elsewhere
            if platform.system() == "Windows":
                venv_python = os.path.join(os.path.dirname(__file__), '..', '.venv', 'Scripts', 'python.exe')
                python_exe = venv_python
            else:
                python_exe = "python3"

            log("Agent", f"Using Python executable: {python_exe}")
            self.gcc_process = subprocess.Popen([
                python_exe, gcc_script
            ], cwd=os.path.dirname(__file__))

            if self.gcc_process is not None:
                log("Agent", f"GCC subprocess launched: PID={self.gcc_process.pid}")
            else:
                log_error("Agent", "GCC launch failed: subprocess returned None")
        except Exception as e:
            log_error("Agent", f"Failed to start GCC: {e}")
            self.gcc_process = None

    async def start(self):
        log("Agent", f"Starting agent (is_primary={self.is_primary})...")
        if self.is_primary:
            self.start_gcc_server()

        await self.spawn_local_modules()

        if self.is_primary:
            await self.launch_remote_agents()

        await self.start_vibe_system()
        asyncio.create_task(self.monitor_heartbeats())

        log("Agent", "System operational.")

    async def spawn_local_modules(self):
        log("Agent", "Spawning local modules...")
        for device_name, device_info in self.config.get('devices', {}).items():
            if device_info.get('ip') == self.ip_self:
                for module in device_info.get('modules', []):
                    await self.spawn_module(module['module'], module.get('params', {}))

    async def spawn_module(self, module_class_path, params):
        launcher_script = os.path.join(os.path.dirname(__file__), 'launcher.py')
        command = [
            "python",
            launcher_script,
            "--module", module_class_path,
            "--params", json.dumps(params)
        ]
        log("Agent", f"Launching module with command: {' '.join(shlex.quote(arg) for arg in command)}")
        try:
            env = os.environ.copy()
            src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            env["PYTHONPATH"] = src_path
            process = subprocess.Popen(command, cwd=os.path.dirname(__file__), env=env)
            self.modules[module_class_path] = process
            self.last_heartbeats[module_class_path] = (time.time(), 'unknown')
        except Exception as e:
            log_error("Agent", f"Failed to launch module {module_class_path}: {e}")

    async def launch_remote_agents(self):
        log("Agent", "Launching remote agents...")
        for device_name, device_info in self.devices.items():
            if device_info.get('ip') != self.ip_self:
                ip = device_info['ip']
                agent_path = device_info['agent_path']
                config_path = device_info['config_path']
                remote_python_command = f"/usr/bin/python {device_info['agent_path']} --config {device_info['config_path']}"
                remote_command = f"tmux new-session -d -s catdog_agent {remote_python_command}"
                log("Agent", remote_command)

                ssh_user = device_info.get('ssh_user', 'gbrouwer')  # Default fallback
                ssh_command = ["ssh", f"{ssh_user}@{device_info['ip']}", remote_command]
                log("Agent", f"Launching remote agent on {ip} with tmux...")
                try:
                    proc = subprocess.Popen(ssh_command)
                    self.agent_processes.append(proc)
                except Exception as e:
                    log_error("Agent", f"Failed to launch remote agent on {ip}: {e}")

    async def start_vibe_system(self):
        log("Agent", "Starting Vibe system...")
        vibe_sender = VibeSender(platform.node(), self.get_health_snapshot)
        vibe_listener = VibeListener()
        await asyncio.gather(vibe_sender.start(), vibe_listener.start())

    def get_health_snapshot(self):
        return {module: status for module, (timestamp, status) in self.last_heartbeats.items()} | {"start_time": self.start_time}

    async def monitor_heartbeats(self):
        log("Agent", "Heartbeat monitor started.")
        while True:
            current_time = time.time()
            for module_name, (last_time, status) in self.last_heartbeats.items():
                if current_time - last_time > self.HEARTBEAT_TIMEOUT:
                    log_error("Agent", f"WARNING: Module {module_name} missed heartbeat!")
            await asyncio.sleep(self.HEARTBEAT_CHECK_INTERVAL)

    async def stop(self):
        log("Agent", "Shutting down...")
        for module, process in self.modules.items():
            if process.poll() is None:
                process.terminate()
        if self.gcc_process and self.gcc_process.poll() is None:
            self.gcc_process.terminate()
        await asyncio.sleep(2)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to config file.")
    parser.add_argument("--primary", action="store_true", help="Run as primary agent.")
    args = parser.parse_args()

    agent = Agent(config_path=args.config, is_primary=args.primary)
    await agent.start()

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
