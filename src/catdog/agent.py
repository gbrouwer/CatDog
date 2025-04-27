import yaml
import threading
import platform
import argparse
import time
import subprocess
import asyncio
from catdog.vibes import VibeSender, VibeListener


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
        self.modules = {}
        self.last_heartbeats = {}  # {module_name: (timestamp, status)}
        self.config = {}
        self.monitor_thread = threading.Thread(target=self.monitor_heartbeats, daemon=True)
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
        system = platform.system()
        if self.mode == 'live' and system != 'Linux':
            print("[Agent] Warning: Live mode recommended for Linux (e.g., Raspberry Pi).")
        print(f"[Agent] Running in {self.mode.upper()} mode on {system}.")

    def build_modules(self):
        for module_name, module_info in self.config.get('modules', {}).items():
            module_class_path = module_info['class']
            params = module_info.get('params', {})
            module_class = self.dynamic_import(module_class_path)
            module_instance = module_class(**params)
            self.modules[module_name] = module_instance
            self.last_heartbeats[module_name] = (time.time(), 'unknown')

    def dynamic_import(self, class_path):
        module_path, class_name = class_path.rsplit('.', 1)
        module = __import__(module_path, fromlist=[class_name])
        return getattr(module, class_name)

    def start(self):
        if self.is_primary:
            self.launch_ephemeral_agents()

        print("[Agent] Starting modules...")
        for module in self.modules.values():
            module.start()

        self.await_heartbeats(expected_status="online")
        self.test_modules()
        self.await_heartbeats(expected_status=["connected", "receiving", "sending"])
        self.enter_operational_mode()

    def launch_ephemeral_agents(self):
        print("[Agent] Launching ephemeral agents...")
        for device_name, device_ip in self.connected_devices.items():
            if device_name != self.device_name:
                print(f"[Agent] Launching ephemeral agent on {device_name} at {device_ip}")
                try:
                    subprocess.Popen([
                        "ssh", f"{device_ip}",
                        f"python3 /path/to/agent.py --config /path/to/config.yaml"
                    ])
                except Exception as e:
                    print(f"[Agent] Failed to launch ephemeral agent on {device_ip}: {e}")

    def await_heartbeats(self, expected_status, timeout=10):
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
            time.sleep(1)

        print("[Agent] ERROR: Timeout waiting for module heartbeats!")
        self.stop()
        raise RuntimeError("Agent startup failed due to missing heartbeats.")

    def test_modules(self):
        for name, module in self.modules.items():
            if hasattr(module, "selftest"):
                print(f"[Agent] Running self-test for {name}")
                module.selftest()

    def enter_operational_mode(self):
        self.monitor_thread.start()
        asyncio.create_task(self.start_vibe_system())
        print("[Agent] System is now operational.")

    async def start_vibe_system(self):
        vibe_sender = VibeSender(self.device_name, self.get_health_snapshot)
        vibe_listener = VibeListener()
        await asyncio.gather(
            vibe_sender.start(),
            vibe_listener.start()
        )

    def get_health_snapshot(self):
        return {
            module_name: status for module_name, (timestamp, status) in self.last_heartbeats.items()
        } | {"start_time": self.start_time}

    def monitor_heartbeats(self):
        print("[Agent] Heartbeat monitoring started.")
        while True:
            current_time = time.time()
            for name, (last_time, status) in self.last_heartbeats.items():
                if current_time - last_time > self.HEARTBEAT_TIMEOUT:
                    print(f"[Agent] WARNING: No heartbeat from {name}!")
            time.sleep(self.HEARTBEAT_CHECK_INTERVAL)

    def update_heartbeat(self, module_name, status):
        self.last_heartbeats[module_name] = (time.time(), status)

    def stop(self):
        print("[Agent] Stopping modules...")
        for module in self.modules.values():
            module.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to the config YAML file.")
    parser.add_argument("--primary", action="store_true", help="Is this the primary agent?")
    args = parser.parse_args()

    agent = Agent(config_path=args.config, is_primary=args.primary)
    agent.start()

    try:
        print("[Agent] Running. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[Agent] Shutting down...")
        agent.stop()
