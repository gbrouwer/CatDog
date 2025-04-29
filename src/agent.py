import yaml
import asyncio
import platform
import argparse
import time
import subprocess
import shlex
import os
import json
from vibes import VibeSender, VibeListener


class Agent:
    HEARTBEAT_TIMEOUT = 10  # seconds
    HEARTBEAT_CHECK_INTERVAL = 2  # seconds

    def __init__(self, config_path, is_primary=False):
        self.config_path = config_path
        self.is_primary = is_primary
        self.mode = None
        self.device_name = None
        self.ip_self = None
        self.connected_devices = {}
        self.modules = {}  # {module_name: subprocess handle}
        self.last_heartbeats = {}  # {module_name: (timestamp, status)}
        self.config = {}
        self.start_time = time.time()

        self.load_config()
        self.setup_environment()
        self.build_modules()

    def load_config(self):
        with open(self.config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        self.mode = self.config.get('mode', 'simulation')
        device_info = self.config.get('device', {})
        self.device_name = device_info.get('name', 'unknown')
        self.ip_self = device_info.get('ip', '127.0.0.1')
        self.connected_devices = self.config.get('connected_devices', {})

    def setup_environment(self):
        self.kill_old_python_processes()
        system = platform.system()
        if self.mode == 'live' and system != 'Linux':
            print("[Agent] Warning: Live mode recommended for Linux (e.g., Raspberry Pi).")
        print(f"[Agent] Running in {self.mode.upper()} mode on {system}.")

    def kill_old_python_processes(self):
        print("[Agent] Checking for old Python processes...")
        try:
            result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq python.exe"], capture_output=True, text=True)
            if "python.exe" in result.stdout:
                print("[Agent] Found old python.exe process(es), attempting to clean up...")
                subprocess.run(["taskkill", "/F", "/IM", "python.exe"])
                print("[Agent] Old Python processes killed.")
            else:
                print("[Agent] No old Python processes found.")
        except Exception as e:
            print(f"[Agent] Error during process cleanup: {e}")

    def build_modules(self):
        print("[Agent] Spawning modules as subprocesses...")
        for module_name, module_info in self.config.get('modules', {}).items():
            module_class_path = module_info['class']
            params = module_info.get('params', {})
            self.spawn_module_process(module_name, module_class_path, params)
            self.last_heartbeats[module_name] = (time.time(), 'unknown')

    def spawn_module_process(self, module_name, module_class_path, params):
        launcher_script = os.path.join(os.path.dirname(__file__), 'launcher.py')

        command = [
            "python3",
            launcher_script,
            "--module", module_class_path,
            "--params", json.dumps(params)
        ]

        print(f"[Agent] Launching module '{module_name}' with command: {' '.join(shlex.quote(arg) for arg in command)}")

        try:
            # Copy current environment and add PYTHONPATH pointing to the src folder
            env = os.environ.copy()
            src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            env["PYTHONPATH"] = src_path

            # Set working directory to src/
            process = subprocess.Popen(
                command,
                cwd=os.path.abspath(os.path.dirname(__file__)),  # This is /src
                env=env
            )
            self.modules[module_name] = process
        except Exception as e:
            print(f"[Agent] Failed to launch module {module_name}: {e}")

    async def start(self):
        if self.is_primary:
            self.launch_ephemeral_agents()

        await self.await_heartbeats(expected_status="online")
        self.test_modules()
        await self.await_heartbeats(expected_status=["connected", "receiving", "sending"])
        await self.enter_operational_mode()

    def launch_ephemeral_agents(self):
        print("[Agent] Launching ephemeral agents...")
        for device_name, device_ip in self.connected_devices.items():
            if device_name != self.device_name:
                print(f"[Agent] Launching ephemeral agent on {device_name} at {device_ip}")
                try:
                    subprocess.Popen(["ssh", f"{device_ip}", "python3 /path/to/agent.py --config /path/to/config.yaml"])
                except Exception as e:
                    print(f"[Agent] Failed to launch ephemeral agent on {device_ip}: {e}")

    async def await_heartbeats(self, expected_status, timeout=10):
        print(f"[Agent] Waiting for heartbeats with status: {expected_status}")
        expected_statuses = expected_status if isinstance(expected_status, list) else [expected_status]
        start_time = time.time()

        while time.time() - start_time < timeout:
            all_ok = True
            for name, (last_time, status) in self.last_heartbeats.items():
                if status not in expected_statuses:
                    all_ok = False
                    break
            if all_ok:
                print("[Agent] All modules have reported expected status.")
                return
            await asyncio.sleep(1)

        print("[Agent] ERROR: Timeout waiting for module heartbeats!")
        await self.stop()
        raise RuntimeError("Agent startup failed due to missing heartbeats.")

    def test_modules(self):
        print("[Agent] Running module self-tests...")
        for name in self.modules.keys():
            print(f"[Agent] (Placeholder) Self-test for module {name}")
            # Self-test should probably move inside the individual modules themselves.

    async def enter_operational_mode(self):
        asyncio.create_task(self.monitor_heartbeats())
        asyncio.create_task(self.start_vibe_system())
        print("[Agent] System is now operational.")

    async def start_vibe_system(self):
        vibe_sender = VibeSender(self.device_name, self.get_health_snapshot)
        vibe_listener = VibeListener()
        await asyncio.gather(vibe_sender.start(), vibe_listener.start())

    def get_health_snapshot(self):
        return {module_name: status for module_name, (timestamp, status) in self.last_heartbeats.items()} | {"start_time": self.start_time}

    async def monitor_heartbeats(self):
        print("[Agent] Heartbeat monitoring started.")
        while True:
            current_time = time.time()
            for name, (last_time, status) in self.last_heartbeats.items():
                if current_time - last_time > self.HEARTBEAT_TIMEOUT:
                    print(f"[Agent] WARNING: No heartbeat from {name}!")
            for name, process in self.modules.items():
                if process.poll() is not None:
                    print(f"[Agent] ERROR: Module process {name} has crashed!")
            await asyncio.sleep(self.HEARTBEAT_CHECK_INTERVAL)

    def update_heartbeat(self, module_name, status):
        self.last_heartbeats[module_name] = (time.time(), status)

    async def stop(self):
        print("[Agent] Stopping all modules...")
        for name, process in self.modules.items():
            if process.poll() is None:
                print(f"[Agent] Terminating module {name}...")
                process.terminate()
        await asyncio.sleep(2)  # Give processes time to shutdown


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to the config YAML file.")
    parser.add_argument("--primary", action="store_true", help="Is this the primary agent?")
    args = parser.parse_args()

    agent = Agent(config_path=args.config, is_primary=args.primary)
    await agent.start()

    try:
        print("[Agent] Running. Press Ctrl+C to exit.")
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("[Agent] Shutting down...")
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
